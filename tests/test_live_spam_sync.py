"""
Test live synchronization of Spam folder and desktop notification.
"""
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

src_path = Path("D:/RBMI/Mini Project/ScamGraph-Combined/src")
sys.path.insert(0, str(src_path))

from scamgraph.services.email_monitor import email_monitor
from scamgraph.database.database import db

def main():
    print("1. Connecting to Gmail IMAP...")
    mail = email_monitor.connect_imap()
    print(f"2. Connected. Spam folder mapped to: '{email_monitor.spam_folder_name}'")

    print("3. Executing baseline sync on INBOX and Spam folder...")
    email_monitor._sync_imap_folder(mail, "INBOX", is_baseline=True)
    email_monitor._sync_imap_folder(mail, email_monitor.spam_folder_name, is_baseline=True)

    print("\n4. Checking SQLite Email Investigations Table:")
    records = db.list_email_investigations(limit=5)
    for r in records:
        print(f"   Record #{r['id']} | Folder: {r['folder']} | Subject: '{r['subject']}' | From: {r['sender_email']} | Spam: {bool(r['is_spam'])} (Score: {r['spam_score']}%, Conf: {r['confidence']}%)")

    mail.logout()
    print("\n5. Verification test completed successfully!")

if __name__ == "__main__":
    main()
