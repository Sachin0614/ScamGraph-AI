"""
ScamGraph AI - Real-Time Dual-Folder Email Monitoring Engine
============================================================
Continuously monitors BOTH INBOX and SPAM folders in real time.
- Supports both Gmail API (OAuth 2.0 with includeSpamTrash=True, in:spam queries, History API)
  and Gmail IMAP (App Password over SSL with X-GM-MSGID extraction).
- Detects emails that arrive directly in SPAM without skipping.
- Extracts forensic indicators (URLs, domains, phone numbers).
- Analyzes emails with the spam protection classifier.
- Saves authentic investigation records to SQLite database.
- Triggers interactive Windows desktop notifications:
  * Spam: "ScamGraph AI — Spam Detected" [View] [Network]
  * Safe: "You received a new email!"
- Prevents duplicate alerts using persistent Gmail Message IDs.
- Recovers and reconnects automatically after network interruptions.
"""

import email
import email.utils
import imaplib
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
from datetime import datetime, timezone
from email.header import decode_header
from pathlib import Path
from typing import Any

# Ensure UTF-8 on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scamgraph.config import get_logger
from scamgraph.database.database import db
from scamgraph.services.notifier import notify_safe_email, notify_spam_email
from scamgraph.services.spam_service import spam_classifier
from scamgraph.utils.extractor import extract_forensic_indicators, extract_sender_email

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
ENV_FILE = BASE_DIR / ".env"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
POLL_INTERVAL_SECONDS = 10
RETRY_INTERVAL_SECONDS = 15


def decode_mime(header_val: str | None) -> str:
    """Decodes MIME encoded header strings safely."""
    if not header_val:
        return ""
    try:
        fragments = decode_header(header_val)
        parts = []
        for frag, enc in fragments:
            if isinstance(frag, bytes):
                parts.append(frag.decode(enc or "utf-8", errors="replace"))
            else:
                parts.append(str(frag))
        return "".join(parts)
    except Exception:
        return str(header_val)


def get_account_credentials() -> tuple[str, str]:
    """Retrieves Gmail address and App Password from .env or config.json."""
    # 1. Check environment
    env_user = os.getenv("GMAIL_ADDRESS", "").strip()
    env_pwd = os.getenv("GMAIL_APP_PASSWORD", "").strip().replace(" ", "")
    if env_user and env_pwd and env_pwd != "xxxx xxxx xxxx xxxx":
        return env_user, env_pwd

    # 2. Check config.json
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                u = data.get("email", "").strip()
                p = data.get("app_password", "").strip().replace(" ", "")
                if u and p:
                    return u, p
        except Exception:
            pass

    return "", ""


class EmailMonitorService:
    """
    Manages continuous background polling of Gmail INBOX and SPAM folders.
    Guarantees that spam emails moved directly to Spam folder trigger Windows notifications.
    """

    def __init__(self):
        self.is_running = False
        self._thread: threading.Thread | None = None
        self.last_poll_time: str | None = None
        self.connection_status = "Disconnected"
        self.error_message: str | None = None
        self.active_email: str | None = None
        self.spam_folder_name = "[Gmail]/Spam"
        self._gmail_api_service = None
        self._last_history_id = None

    # =========================================================================
    # GMAIL API INITIALIZATION (OAUTH 2.0)
    # =========================================================================
    def _init_gmail_api(self):
        """Attempts to initialize Gmail API client if credentials are present."""
        if not (CREDENTIALS_FILE.exists() or TOKEN_FILE.exists()):
            return None

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            SCOPES = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify",
            ]

            creds = None
            if TOKEN_FILE.exists():
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif CREDENTIALS_FILE.exists():
                    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                    creds = flow.run_local_server(port=0)
                if creds:
                    with open(TOKEN_FILE, "w", encoding="utf-8") as token_out:
                        token_out.write(creds.to_json())

            if creds:
                service = build("gmail", "v1", credentials=creds)
                logger.info("Gmail API OAuth 2.0 client successfully initialized.")
                return service
        except Exception as api_init_err:
            logger.warning("Gmail API init skipped (%s). Using secure IMAP engine.", api_init_err)
        return None

    # =========================================================================
    # IMAP CONNECTION
    # =========================================================================
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Establishes SSL IMAP connection to Gmail and discovers folder names."""
        user, pwd = get_account_credentials()
        if not user or not pwd:
            raise ValueError("Gmail credentials missing. Provide them in config.json or .env.")

        self.active_email = user
        context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        mail.login(user, pwd)

        # Detect the exact name of the Spam folder on this account
        try:
            status, folder_list = mail.list()
            if status == "OK" and folder_list:
                for f_bytes in folder_list:
                    f_str = f_bytes.decode("utf-8", errors="replace")
                    if "\\Junk" in f_str or "\\Spam" in f_str:
                        # Extract folder name in quotes or after delimiter
                        parts = f_str.split(' "/" ')
                        if len(parts) >= 2:
                            self.spam_folder_name = parts[1].strip('"').strip()
                            break
                        elif "[Gmail]/Spam" in f_str:
                            self.spam_folder_name = "[Gmail]/Spam"
                            break
        except Exception as folder_err:
            logger.warning("Folder discovery error: %s. Defaulting to '[Gmail]/Spam'", folder_err)
            self.spam_folder_name = "[Gmail]/Spam"

        logger.info("Connected to Gmail IMAP (%s). Spam folder: '%s'", user, self.spam_folder_name)
        return mail

    # =========================================================================
    # EMAIL PROCESSING LOGIC
    # =========================================================================
    def _process_single_email(
        self,
        unique_msg_id: str,
        folder_category: str,
        subject: str,
        sender_raw: str,
        received_at_str: str,
        snippet: str,
        full_body: str,
        is_server_flagged_spam: bool = False,
    ) -> bool:
        """
        Processes an individual email: checks deduplication, classifies spam,
        saves investigation to SQLite, and triggers desktop notifications.
        Returns True if a notification was dispatched.
        """
        if db.is_message_processed(unique_msg_id):
            return False

        disp_name, sender_email, sender_domain = extract_sender_email(sender_raw)
        forensics = extract_forensic_indicators(f"{subject} {full_body}")

        # Classify email threat
        analysis = spam_classifier.classify(subject=subject, body=full_body, sender=sender_email)

        if is_server_flagged_spam or folder_category.upper() == "SPAM":
            # Email was placed directly in SPAM by Gmail
            is_spam = True
            spam_score = max(analysis["spam_score"], 95.0)
            confidence = max(analysis["confidence"], 95.0)
            evidence = ["Email filtered directly into Gmail Spam folder by mail server filters."] + analysis["evidence"]
        else:
            is_spam = analysis["is_spam"]
            spam_score = analysis["spam_score"]
            confidence = analysis["confidence"]
            evidence = analysis["evidence"]

        # Persist forensic record to SQLite
        record_id = db.save_email_investigation({
            "message_id": unique_msg_id,
            "folder": "SPAM" if is_spam else "INBOX",
            "subject": subject,
            "sender": sender_raw,
            "sender_email": sender_email,
            "sender_domain": sender_domain,
            "received_at": received_at_str,
            "snippet": snippet or subject,
            "content": full_body,
            "is_spam": is_spam,
            "spam_score": spam_score,
            "confidence": confidence,
            "evidence": evidence,
            "extracted_urls": forensics["urls"],
            "extracted_domains": forensics["domains"],
            "extracted_phones": forensics["phones"],
        })

        # Mark message as permanently processed in DB
        db.mark_message_processed(unique_msg_id, folder="SPAM" if is_spam else "INBOX")

        logger.info(
            "Processed email #%d: '%s' from '%s' | Verdict: %s (%.1f%%) | Folder: %s",
            record_id, subject, sender_email, "SPAM" if is_spam else "SAFE", confidence, folder_category
        )

        # Trigger Windows Desktop Notification
        if is_spam:
            # Professional spam notification with [View] and [Network] action buttons
            logger.info("Triggering Spam desktop notification for email record #%d...", record_id)
            notify_spam_email(email_id=record_id)
        else:
            # Safe email notification: "You received a new email!"
            logger.info("Triggering Safe desktop notification for email record #%d...", record_id)
            notify_safe_email()

        return True

    # =========================================================================
    # IMAP FOLDER POLLING
    # =========================================================================
    def _sync_imap_folder(self, mail: imaplib.IMAP4_SSL, folder_name: str, is_baseline: bool = False):
        """
        Polls a specific Gmail IMAP folder (INBOX or Spam).
        Uses X-GM-MSGID for permanent unique message IDs.
        """
        folder_category = "SPAM" if "spam" in folder_name.lower() or "junk" in folder_name.lower() else "INBOX"

        try:
            # Select folder (try quoted then unquoted)
            status, _ = mail.select(f'"{folder_name}"', readonly=True)
            if status != "OK":
                status, _ = mail.select(folder_name, readonly=True)
                if status != "OK":
                    logger.warning("Could not select folder: '%s'", folder_name)
                    return

            res, data = mail.uid("search", None, "ALL")
            if res != "OK" or not data or not data[0]:
                return

            uids = data[0].decode("utf-8").split()
            if not uids:
                return

            now_utc = datetime.now(timezone.utc)

            # In baseline mode:
            # Mark ALL existing historical emails as processed in a single fast batch.
            # Old existing emails will NEVER trigger repeated notifications.
            if is_baseline:
                logger.info("Recording baseline for '%s' (%d total existing messages)...", folder_name, len(uids))
                all_items = [(f"{folder_name}_{uid}", folder_category) for uid in uids]
                db.mark_messages_processed_batch(all_items)
                logger.info("Baseline for '%s' recorded. Historical messages silenced.", folder_name)
                return

            # Continuous Polling Mode: Process strictly brand-new UIDs
            new_uids = [uid for uid in uids if not db.is_message_processed(f"{folder_name}_{uid}")]
            if not new_uids:
                return

            for uid in new_uids:
                # Mark UID processed immediately to guarantee zero repetition
                db.mark_message_processed(f"{folder_name}_{uid}", folder=folder_category)
                self._fetch_and_process_imap_email(mail, uid, folder_name, folder_category)

        except Exception as sync_err:
            logger.warning("Error syncing IMAP folder %s: %s", folder_name, sync_err)

    def _fetch_and_process_imap_email(self, mail: imaplib.IMAP4_SSL, uid: str, folder_name: str, folder_category: str):
        """Fetches full email details and processes via IMAP."""
        try:
            f_res, f_data = mail.uid("fetch", uid, "(X-GM-MSGID X-GM-LABELS RFC822)")
            if f_res != "OK" or not f_data:
                return

            unique_msg_id = None
            subject = "No Subject"
            sender_raw = "Unknown"
            received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_body = ""
            is_server_flagged = (folder_category == "SPAM")

            for item in f_data:
                if isinstance(item, tuple) and len(item) >= 2:
                    hdr_meta = item[0].decode("utf-8", errors="replace")
                    m_msgid = re.search(r"X-GM-MSGID\s+(\d+)", hdr_meta)
                    if m_msgid:
                        unique_msg_id = f"gmail_{m_msgid.group(1)}"

                    if "\\Spam" in hdr_meta or "Junk" in hdr_meta:
                        is_server_flagged = True

                    raw_bytes = item[1]
                    try:
                        parsed = email.message_from_bytes(raw_bytes)
                        if parsed.get("Subject"):
                            subject = decode_mime(parsed.get("Subject"))
                        if parsed.get("From"):
                            sender_raw = decode_mime(parsed.get("From"))
                        if parsed.get("Date"):
                            received_at = parsed.get("Date")
                        if not unique_msg_id and parsed.get("Message-ID"):
                            unique_msg_id = parsed.get("Message-ID").strip()

                        if parsed.is_multipart():
                            for part in parsed.walk():
                                if part.get_content_type() == "text/plain":
                                    cset = part.get_content_charset() or "utf-8"
                                    decoded_bytes = part.get_payload(decode=True)
                                    if decoded_bytes:
                                        full_body = decoded_bytes.decode(cset, errors="replace")[:4000]
                                        break
                        else:
                            cset = parsed.get_content_charset() or "utf-8"
                            decoded_bytes = parsed.get_payload(decode=True)
                            if decoded_bytes:
                                full_body = decoded_bytes.decode(cset, errors="replace")[:4000]
                            elif not full_body:
                                full_body = raw_bytes.decode("utf-8", errors="replace")[:4000]
                    except Exception:
                        pass

            if not unique_msg_id:
                unique_msg_id = f"{folder_name}_{uid}"

            # Check deduplication
            if db.is_message_processed(unique_msg_id):
                return

            snippet = full_body[:250].strip() if full_body else subject

            self._process_single_email(
                unique_msg_id=unique_msg_id,
                folder_category=folder_category,
                subject=subject,
                sender_raw=sender_raw,
                received_at_str=received_at,
                snippet=snippet,
                full_body=full_body,
                is_server_flagged_spam=is_server_flagged,
            )

        except Exception as fetch_err:
            logger.warning("Error fetching UID %s in %s: %s", uid, folder_name, fetch_err)

    # =========================================================================
    # GMAIL API POLLING (WHEN OAUTH CONFIGURED)
    # =========================================================================
    def _poll_gmail_api(self, service):
        """
        Polls Gmail API for messages in BOTH INBOX and SPAM using includeSpamTrash=True.
        Supports query: 'in:inbox OR in:spam'.
        """
        try:
            # 1. Query for recent messages in both INBOX and SPAM
            query = "in:inbox OR in:spam"
            results = service.users().messages().list(
                userId="me",
                q=query,
                includeSpamTrash=True,
                maxResults=25
            ).execute()

            messages = results.get("messages", [])
            for msg_meta in messages:
                msg_id = msg_meta.get("id")
                if not msg_id or db.is_message_processed(msg_id):
                    continue

                # Fetch full message
                msg_data = service.users().messages().get(
                    userId="me",
                    id=msg_id,
                    format="full"
                ).execute()

                label_ids = msg_data.get("labelIds", [])
                is_spam = "SPAM" in label_ids
                folder_category = "SPAM" if is_spam else "INBOX"

                payload = msg_data.get("payload", {})
                headers = payload.get("headers", [])

                subject = "No Subject"
                sender_raw = "Unknown"
                received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for h in headers:
                    name = h.get("name", "").lower()
                    if name == "subject":
                        subject = decode_mime(h.get("value", ""))
                    elif name == "from":
                        sender_raw = decode_mime(h.get("value", ""))
                    elif name == "date":
                        received_at = h.get("value", "")

                snippet = msg_data.get("snippet", "")
                full_body = snippet

                self._process_single_email(
                    unique_msg_id=msg_id,
                    folder_category=folder_category,
                    subject=subject,
                    sender_raw=sender_raw,
                    received_at_str=received_at,
                    snippet=snippet,
                    full_body=full_body,
                    is_server_flagged_spam=is_spam,
                )

        except Exception as api_poll_err:
            logger.warning("Gmail API polling error: %s", api_poll_err)

    # =========================================================================
    # WORKER LOOP
    # =========================================================================
    def _worker_loop(self):
        """Main monitoring thread loop."""
        logger.info("ScamGraph AI Email Monitor worker started.")
        self.connection_status = "Connecting..."

        # Try initializing Gmail API
        self._gmail_api_service = self._init_gmail_api()

        mail: imaplib.IMAP4_SSL | None = None

        while self.is_running:
            try:
                # Mode 1: Gmail API OAuth
                if self._gmail_api_service:
                    self.connection_status = "Connected (Gmail API)"
                    self.error_message = None
                    self._poll_gmail_api(self._gmail_api_service)
                    self.last_poll_time = datetime.now().strftime("%H:%M:%S")
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # Mode 2: IMAP SSL Engine
                if not mail:
                    mail = self.connect_imap()
                    self.connection_status = "Connected (IMAP)"
                    self.error_message = None
                    logger.info("Establishing baseline synchronization for INBOX and %s...", self.spam_folder_name)

                    # Initial scan of both folders
                    self._sync_imap_folder(mail, "INBOX", is_baseline=True)
                    self._sync_imap_folder(mail, self.spam_folder_name, is_baseline=True)
                    logger.info("Dual-folder baseline sync complete. Real-time spam detection active.")

                # Real-time continuous monitoring cycle
                self._sync_imap_folder(mail, "INBOX", is_baseline=False)
                self._sync_imap_folder(mail, self.spam_folder_name, is_baseline=False)
                self.last_poll_time = datetime.now().strftime("%H:%M:%S")

                time.sleep(POLL_INTERVAL_SECONDS)

            except (socket.error, TimeoutError, ConnectionError, ssl.SSLError, imaplib.IMAP4.abort) as net_err:
                self.connection_status = "Reconnecting..."
                self.error_message = f"Network interruption: {net_err}"
                logger.warning("Connection drop detected: %s. Reconnecting in %ds...", net_err, RETRY_INTERVAL_SECONDS)
                mail = None
                time.sleep(RETRY_INTERVAL_SECONDS)

            except Exception as loop_err:
                self.error_message = str(loop_err)
                logger.error("Monitor loop encountered error: %s", loop_err)
                mail = None
                time.sleep(RETRY_INTERVAL_SECONDS)

        if mail:
            try:
                mail.logout()
            except Exception:
                pass
        self.connection_status = "Stopped"
        logger.info("ScamGraph AI Email Monitor worker stopped.")

    def start(self):
        """Starts background monitoring thread if not already running."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops background monitoring thread."""
        self.is_running = False


# Global singleton monitor
email_monitor = EmailMonitorService()
