"""
ScamGraph AI - Sidebar Component
================================
Navigation, real-time Gmail monitoring telemetry, and notification triggers.
"""

import streamlit as st

from scamgraph.database.database import db
from scamgraph.services.email_monitor import email_monitor
from scamgraph.services.notifier import notify_safe_email, notify_spam_email
from scamgraph.ui.theme import get_theme, inject_custom_css


def render_sidebar() -> str:
    """Render the sidebar navigation."""
    theme = get_theme()

    # Inject custom CSS
    st.markdown(inject_custom_css(), unsafe_allow_html=True)

    with st.sidebar:
        # Logo/Brand
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid {theme['border']}; margin-bottom: 1rem;">
                <h1 style="color: {theme['primary']}; margin: 0; font-size: 1.5rem;">🕸️ ScamGraph AI</h1>
                <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0; font-size: 0.8rem;">Real-Time Threat Intelligence</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown("### Navigation")

        pages = {
            "dashboard": "📊 Dashboard",
            "graph": "🕸️ Threat Graph",
            "investigations": "🔍 Investigations",
            "evidence": "📁 Evidence",
            "settings": "⚙️ Settings",
        }

        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        for page_key, page_label in pages.items():
            is_active = st.session_state.current_page == page_key
            button_style = "primary" if is_active else "secondary"

            if st.button(page_label, key=f"nav_{page_key}", use_container_width=True, type=button_style):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        # Real-time Stats from Database
        all_emails = db.list_email_investigations(limit=500)
        total_cases = len(all_emails)
        spam_cases = sum(1 for e in all_emails if e["is_spam"])
        safe_cases = total_cases - spam_cases

        st.markdown("### Telemetry Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cases", total_cases)
        with col2:
            st.metric("Spam Detected", spam_cases)

        st.divider()

        # Monitoring System Status
        status_color = theme["success"] if email_monitor.connection_status == "Connected" else theme["warning"]
        active_email = email_monitor.active_email or "shrishtiraghav66@gmail.com"

        st.markdown("### Live Email Stream")
        st.markdown(
            f"""
            <div style="padding: 0.7rem; background: {theme['surface']}; border-radius: 8px; border: 1px solid {theme['border']}; font-size: 12px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 6px;">
                    <span style="width: 8px; height: 8px; background: {status_color}; border-radius: 50%;"></span>
                    <strong style="color: {theme['text_primary']};">INBOX + SPAM Active</strong>
                </div>
                <div style="color: {theme['text_secondary']};">
                    👤 <code>{active_email}</code><br>
                    🕒 Last Poll: <strong>{email_monitor.last_poll_time or 'Just now'}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick Notification Test Suite
        st.markdown("### 🔔 Desktop Alert Test")
        if st.button("⚠️ Test Spam Notification", use_container_width=True):
            # Test with most recent spam ID or 1
            test_id = 1
            for e in all_emails:
                if e["is_spam"]:
                    test_id = e["id"]
                    break
            notify_spam_email(email_id=test_id)
            st.toast("Fired bottom-right Spam Notification with [View] & [Network] buttons!", icon="⚠️")

        if st.button("📩 Test Safe Notification", use_container_width=True):
            notify_safe_email()
            st.toast("Fired bottom-right Safe Notification!", icon="📩")

    return st.session_state.current_page
