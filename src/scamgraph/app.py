"""
Email Notification & Spam Protection Agent - Minimal UI
=======================================================
Simple, clean, single-screen UI:
Enter your Gmail address, start the agent, and everything runs in the background.
Desktop pop-up notification appears on every incoming email.
"""

import json
import os
import sys
from pathlib import Path
import streamlit as st

# Auto-launch Streamlit if invoked directly via `python app.py`
from streamlit.runtime.scriptrunner import get_script_run_ctx
if get_script_run_ctx() is None:
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", __file__, "--server.port=8501", "--server.address=localhost", "--browser.gatherUsageStats=false"]
    sys.exit(stcli.main())

# Ensure src in Python path
CURRENT_DIR = Path(__file__).resolve().parent
search_dirs = [
    CURRENT_DIR.parent,
    CURRENT_DIR.parent.parent / "src",
    CURRENT_DIR.parent.parent.parent / "src",
    CURRENT_DIR / "src",
    Path(r"D:\RBMI\Mini Project\ScamGraph-Combined\src")
]
for d in search_dirs:
    if d.exists() and str(d) not in sys.path:
        sys.path.insert(0, str(d))

from scamgraph.database.database import db
from scamgraph.services.email_monitor import email_monitor, get_account_credentials, CONFIG_FILE
from scamgraph.services.notifier import notify_safe_email, notify_spam_email

# Streamlit Page Configuration - Minimal Centered View
st.set_page_config(
    page_title="Email Notification Agent",
    page_icon="📬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Minimalist Dark Styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 650px;
    }
    .agent-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }
    .status-pill-active {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
    .status-pill-idle {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1 style="color: #F8FAFC; font-size: 28px; margin: 0 0 6px 0;">
            📬 Email Notification Agent
        </h1>
        <p style="color: #94A3B8; font-size: 14.5px; margin: 0;">
            Apna email enter karein. Agent backend mein silently run hoga aur naya email aane par desktop par pop-up aayega.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Automatically start background monitoring thread if credentials exist
    saved_email, saved_pwd = get_account_credentials()
    if saved_email and saved_pwd and not email_monitor.is_running:
        email_monitor.start()

    is_running = email_monitor.is_running
    status_label = "🟢 Active & Monitoring in Background" if is_running else "🟡 Idle / Disconnected"
    status_class = "status-pill-active" if is_running else "status-pill-idle"

    # =========================================================================
    # SINGLE FOCUSED EMAIL INPUT CARD
    # =========================================================================
    with st.container():
        st.markdown(f"""
        <div class="agent-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <strong style="color: #F8FAFC; font-size: 16px;">📧 Gmail Account</strong>
                <span class="{status_class}">{status_label}</span>
            </div>
        """, unsafe_allow_html=True)

        email_input = st.text_input("Gmail Address:", value=saved_email, placeholder="yourname@gmail.com")
        pwd_input = st.text_input("16-digit Google App Password:", value=saved_pwd, type="password", placeholder="xxxx xxxx xxxx xxxx")

        btn_col1, btn_col2 = st.columns([2, 1.2])
        with btn_col1:
            if not is_running:
                if st.button("🚀 Start Monitoring", type="primary", use_container_width=True):
                    if not email_input or not pwd_input:
                        st.error("Please enter email & App Password first.")
                    else:
                        clean_u = email_input.strip()
                        clean_p = pwd_input.strip().replace(" ", "")
                        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                            json.dump({"email": clean_u, "app_password": clean_p}, f, indent=4)
                        email_monitor.start()
                        st.success(f"✓ Agent started for {clean_u}! Monitoring in background.")
                        st.rerun()
            else:
                if st.button("💾 Update & Reconnect", type="primary", use_container_width=True):
                    clean_u = email_input.strip()
                    clean_p = pwd_input.strip().replace(" ", "")
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump({"email": clean_u, "app_password": clean_p}, f, indent=4)
                    email_monitor.stop()
                    email_monitor.start()
                    st.success("Credentials updated! Reconnected successfully.")
                    st.rerun()

        with btn_col2:
            if is_running:
                if st.button("⏹️ Stop Agent", use_container_width=True):
                    email_monitor.stop()
                    st.info("Agent stopped.")
                    st.rerun()
            else:
                st.caption("Press Start to begin")

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # SILENT BACKGROUND STATUS & LATEST EMAIL
    # =========================================================================
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid #1E293B; border-radius: 12px; padding: 14px 18px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #94A3B8; font-size: 13px;">
                🔄 Folders Monitored: <strong style="color: #38BDF8;">INBOX & SPAM</strong>
            </span>
            <span style="color: #94A3B8; font-size: 12px;">
                Last Poll: <strong style="color: #F8FAFC;">""" + (email_monitor.last_poll_time or "Active") + """</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show the single latest incoming email
    latest_emails = db.list_email_investigations(limit=1)
    if latest_emails:
        em = latest_emails[0]
        is_spam = bool(em["is_spam"])
        badge_color = "#EF4444" if is_spam else "#10B981"
        badge_txt = f"⚠️ SPAM DETECTED ({em['confidence']}%)" if is_spam else f"📩 SAFE EMAIL ({em['confidence']}%)"

        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); border-left: 4px solid {badge_color}; border-radius: 10px; padding: 14px 18px; border: 1px solid #1E293B; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #94A3B8; font-size: 11px; text-transform: uppercase; font-weight: bold;">Latest Incoming Email</span>
                <span style="background: {badge_color}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{badge_txt}</span>
            </div>
            <strong style="color: #F8FAFC; font-size: 15px;">{em['subject'] or 'No Subject'}</strong>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                👤 <strong>From:</strong> {em['sender_email']} &nbsp;|&nbsp; 🕒 {em['received_at']}
            </div>
            <div style="font-size: 12.5px; color: #CBD5E1; margin-top: 8px; line-height: 1.4;">
                {em['snippet'][:150]}...
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick test button for desktop notification
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        if st.button("🔔 Test Desktop Pop-up", use_container_width=True):
            notify_spam_email(email_id=1)
            st.toast("Windows desktop notification sent to bottom-right corner!", icon="🔔")

    with col_t2:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()


if __name__ == "__main__":
    main()
