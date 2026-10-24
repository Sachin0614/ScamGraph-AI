"""
ScamGraph AI - Windows Desktop Notification Service
===================================================
Displays bottom-right Windows toast notifications with interactive action buttons:
- Spam Alert: "ScamGraph AI — Spam Detected" with [View] and [Network] buttons.
- Safe Alert: "You received a new email!"
"""

import sys
import subprocess
import time

from scamgraph.config import get_logger

logger = get_logger(__name__)

# Debounce tracking: strictly prevents notification spam / repetitive flooding
_last_notification_time = 0.0
NOTIFICATION_COOLDOWN_SECONDS = 4.0

try:
    from winotify import Notification, audio
    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False

try:
    import winsound
except ImportError:
    winsound = None

APP_ID = "ScamGraph AI"
BASE_URL = "http://localhost:8501"


def play_chime(is_spam: bool = False):
    """Plays non-blocking Windows notification chime."""
    if winsound:
        try:
            if is_spam:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                winsound.PlaySound("Notification.Default", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            pass


def notify_spam_email(email_id: int):
    """
    Displays the required spam desktop notification at bottom-right corner:
    - Title: "ScamGraph AI — Spam Detected"
    - Message: "A suspicious email has been received."
    - Actions: [View] -> opens investigation, [Network] -> opens threat graph
    Enforces strict deduplication and debounce to avoid repeated popups.
    """
    global _last_notification_time
    now = time.time()
    if now - _last_notification_time < NOTIFICATION_COOLDOWN_SECONDS:
        logger.info("Notification suppressed by debounce cooldown (too rapid).")
        return False
    _last_notification_time = now

    play_chime(is_spam=True)

    view_url = f"{BASE_URL}/?page=investigations&id={email_id}"
    network_url = f"{BASE_URL}/?page=graph&id={email_id}"

    title = "ScamGraph AI — Spam Detected"
    msg = "A suspicious email has been received."

    if WINOTIFY_AVAILABLE:
        try:
            toast = Notification(
                app_id=APP_ID,
                title=title,
                msg=msg
            )
            toast.add_actions(label="View", launch=view_url)
            toast.add_actions(label="Network", launch=network_url)
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            logger.info("Windows desktop notification dispatched via winotify: '%s' -> [View] [Network]", title)
            return True
        except Exception as winotify_err:
            logger.warning("winotify notification dispatch failed: %s. Attempting PowerShell toast fallback...", winotify_err)

    # Fallback to PowerShell Toast
    powershell_code = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null\n"
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null\n"
        "$xml = @\"\n"
        "<toast>\n"
        "    <visual>\n"
        "        <binding template=\"ToastGeneric\">\n"
        f"            <text>{title}</text>\n"
        f"            <text>{msg}</text>\n"
        "        </binding>\n"
        "    </visual>\n"
        "    <actions>\n"
        f"        <action activationType=\"protocol\" arguments=\"{view_url}\" content=\"View\"/>\n"
        f"        <action activationType=\"protocol\" arguments=\"{network_url}\" content=\"Network\"/>\n"
        "    </actions>\n"
        "    <audio src=\"ms-winsoundevent:Notification.Default\" />\n"
        "</toast>\n"
        "\"@\n"
        "$doc = New-Object Windows.Data.Xml.Dom.XmlDocument\n"
        "$doc.LoadXml($xml)\n"
        "$toast = [Windows.UI.Notifications.ToastNotification]::new($doc)\n"
        f"$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{APP_ID}')\n"
        "$notifier.Show($toast)\n"
    )

    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_code],
            capture_output=True,
            text=True,
            creationflags=creation_flags,
            timeout=6
        )
        if res.returncode == 0:
            logger.info("Windows desktop notification dispatched via PowerShell fallback: '%s'", title)
            return True
        logger.error("PowerShell toast fallback returned error: %s", res.stderr)
        return False
    except Exception as ps_err:
        logger.error("Failed to display Windows desktop notification: %s", ps_err)
        return False


def notify_safe_email():
    """
    Displays safe email notification at bottom-right corner:
    "You received a new email!"
    Enforces strict deduplication and debounce.
    """
    global _last_notification_time
    now = time.time()
    if now - _last_notification_time < NOTIFICATION_COOLDOWN_SECONDS:
        logger.info("Notification suppressed by debounce cooldown (too rapid).")
        return False
    _last_notification_time = now

    play_chime(is_spam=False)

    title = "Email Notification"
    msg = "You received a new email!"

    if WINOTIFY_AVAILABLE:
        try:
            toast = Notification(
                app_id=APP_ID,
                title=title,
                msg=msg
            )
            toast.set_audio(audio.Mail, loop=False)
            toast.show()
            logger.info("Windows desktop safe email notification dispatched via winotify.")
            return True
        except Exception as winotify_err:
            logger.warning("winotify notification dispatch failed: %s. Attempting PowerShell toast fallback...", winotify_err)

    # Fallback
    powershell_code = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null\n"
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null\n"
        "$xml = @\"\n"
        "<toast>\n"
        "    <visual>\n"
        "        <binding template=\"ToastGeneric\">\n"
        f"            <text>{title}</text>\n"
        f"            <text>{msg}</text>\n"
        "        </binding>\n"
        "    </visual>\n"
        "    <audio src=\"ms-winsoundevent:Notification.Default\" />\n"
        "</toast>\n"
        "\"@\n"
        "$doc = New-Object Windows.Data.Xml.Dom.XmlDocument\n"
        "$doc.LoadXml($xml)\n"
        "$toast = [Windows.UI.Notifications.ToastNotification]::new($doc)\n"
        f"$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{APP_ID}')\n"
        "$notifier.Show($toast)\n"
    )

    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_code],
            capture_output=True,
            text=True,
            creationflags=creation_flags,
            timeout=6
        )
        if res.returncode == 0:
            logger.info("Windows desktop safe email notification dispatched via PowerShell fallback.")
            return True
        logger.error("PowerShell toast fallback returned error: %s", res.stderr)
        return False
    except Exception as ps_err:
        logger.error("Failed to display Windows desktop safe notification: %s", ps_err)
        return False
