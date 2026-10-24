"""
ScamGraph AI - Live Email Monitor & Dashboard
=============================================
Interactive UI where users enter their email address to monitor incoming emails,
automatically classify spam with accuracy percentage, view live threat telemetry,
and test emails directly.
"""

import json
import os
from pathlib import Path
import streamlit as st

from scamgraph.database.database import db
from scamgraph.services.email_monitor import email_monitor, get_account_credentials, CONFIG_FILE, ENV_FILE
from scamgraph.services.spam_service import spam_classifier
from scamgraph.services.notifier import notify_safe_email, notify_spam_email
from scamgraph.ui.theme import get_theme


def render_dashboard() -> None:
    """Render the main operations dashboard and email connection center."""
    theme = get_theme()

    # Page Header
    st.markdown(
        f"""
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0; font-size: 26px;">
                📬 Email Monitoring & Spam Protection Agent
            </h1>
            <p style="color: {theme['text_secondary']}; margin: 0.3rem 0 0; font-size: 14px;">
                Enter your email address below to automatically monitor incoming emails across <strong>INBOX & SPAM</strong>, detect threats with high accuracy, and trigger bottom-right Windows pop-up notifications.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 1. PRIMARY EMAIL INPUT & CONNECTION CENTER
    # =========================================================================
    curr_user, curr_pwd = get_account_credentials()

    with st.container():
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1E293B; border-left: 5px solid {theme['primary']}; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <strong style="color: #F8FAFC; font-size: 16px;">📧 Connected Email Account</strong>
                        <div style="color: #94A3B8; font-size: 12.5px;">Agent automatically captures all incoming emails from this account</div>
                    </div>
                    <span style="background: {'#10B981' if email_monitor.connection_status.startswith('Connected') else '#F59E0B'}; color: white; padding: 3px 10px; border-radius: 6px; font-weight: bold; font-size: 12px;">
                        ● {email_monitor.connection_status.upper()}
                    </span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        col_input1, col_input2, col_btn = st.columns([2.5, 2.5, 1.8])
        with col_input1:
            entered_email = st.text_input("Gmail Address:", value=curr_user, placeholder="yourname@gmail.com", key="dash_email_input")
        with col_input2:
            entered_pwd = st.text_input("16-char Google App Password:", value=curr_pwd, type="password", placeholder="xxxx xxxx xxxx xxxx", key="dash_pwd_input")
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            connect_clicked = st.button("🚀 Connect & Monitor", type="primary", use_container_width=True)

        if connect_clicked:
            if not entered_email or not entered_pwd:
                st.error("Please enter both your Gmail address and 16-character App Password.")
            else:
                clean_email = entered_email.strip()
                clean_pwd = entered_pwd.strip().replace(" ", "")

                # Save credentials to config.json and .env
                try:
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump({"email": clean_email, "app_password": clean_pwd}, f, indent=4)
                    
                    # Restart monitoring service
                    email_monitor.stop()
                    email_monitor.start()
                    st.success(f"✓ Connected to {clean_email}! Monitoring both INBOX and SPAM folders.")
                    st.rerun()
                except Exception as save_err:
                    st.error(f"Error saving credentials: {save_err}")

        # Quick guide helper expander
        with st.expander("ℹ️ How to get a free Google App Password (takes 1 minute)"):
            st.markdown("""
            1. Go to your Google Account security settings: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
            2. Make sure 2-Step Verification is turned ON.
            3. Under **App Passwords**, enter an app name (e.g., `ScamGraph AI`) and click **Create**.
            4. Copy the 16-character password displayed and paste it in the box above.
            """)

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # 2. TELEMETRY STATS CARDS
    # =========================================================================
    recent_emails = db.list_email_investigations(limit=100)
    total_emails = len(recent_emails)
    spam_emails = sum(1 for e in recent_emails if e["is_spam"])
    safe_emails = total_emails - spam_emails
    spam_rate = round((spam_emails / total_emails * 100), 1) if total_emails > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center; border-left: 4px solid {theme['primary']};">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['primary']};">{total_emails}</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.82rem; text-transform: uppercase;">Total Monitored</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center; border-left: 4px solid {theme['danger']};">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['danger']};">{spam_emails}</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.82rem; text-transform: uppercase;">Spam Blocked ({spam_rate}%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center; border-left: 4px solid {theme['success']};">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['success']};">{safe_emails}</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.82rem; text-transform: uppercase;">Safe / Clean Emails</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center; border-left: 4px solid #38BDF8;">
                <div style="font-size: 1.6rem; font-weight: 700; color: #38BDF8; margin-top: 4px;">INBOX + SPAM</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.82rem; text-transform: uppercase;">Dual Monitoring</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # =========================================================================
    # 3. LIVE INCOMING EMAIL STREAM
    # =========================================================================
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.markdown("### 📥 Live Incoming Emails (Auto-Captured from Account)")
    with col_hdr2:
        if st.button("🔄 Refresh Feed", use_container_width=True):
            st.rerun()

    if not recent_emails:
        st.info("No incoming emails detected yet. Once you connect your email, any incoming email to your account will automatically appear here with full spam classification and a desktop pop-up alert.")
    else:
        for em in recent_emails[:8]:
            is_spam = bool(em["is_spam"])
            badge_color = "#EF4444" if is_spam else "#10B981"
            badge_label = f"⚠️ SPAM ({em['confidence']}%)" if is_spam else f"📩 SAFE ({em['confidence']}%)"

            with st.container():
                c_data, c_act1, c_act2 = st.columns([4, 1.2, 1.4])
                with c_data:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.5); border-left: 4px solid {badge_color}; border-radius: 8px; padding: 12px 14px; border: 1px solid #1E293B; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <strong style="color: #F8FAFC; font-size: 14.5px;">{em['subject'] or 'No Subject'}</strong>
                            <span style="background: {badge_color}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{badge_label}</span>
                        </div>
                        <div style="font-size: 12px; color: #94A3B8; margin-bottom: 6px;">
                            👤 <strong>From:</strong> {em['sender_email']} &nbsp;|&nbsp; 📁 <strong>Mailbox:</strong> <code style="color: #38BDF8;">{em['folder']}</code> &nbsp;|&nbsp; 🕒 {em['received_at']}
                        </div>
                        <div style="font-size: 12px; color: #CBD5E1; line-height: 1.4;">
                            {em['snippet'][:160]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c_act1:
                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                    if st.button("🔎 View Case", key=f"dash_view_{em['id']}", use_container_width=True):
                        st.session_state.selected_email_id = em['id']
                        st.session_state.current_page = "investigations"
                        st.rerun()

                with c_act2:
                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                    if st.button("🕸️ Threat Graph", key=f"dash_net_{em['id']}", use_container_width=True):
                        st.session_state.selected_email_id = em['id']
                        st.session_state.current_page = "graph"
                        st.rerun()

    st.markdown("---")

    # =========================================================================
    # 4. INSTANT EMAIL ANALYZER (PASTE ANY EMAIL TO TEST)
    # =========================================================================
    st.markdown("### 🧪 Instant Email Tester (Check Any Email Text Directly)")
    st.markdown("Want to test an email without waiting? Paste any email text or subject below to check its spam percentage and trigger a test desktop notification:")

    with st.expander("📝 Open Instant Email Tester", expanded=False):
        test_subj = st.text_input("Email Subject:", placeholder="e.g., Job Offer Letter / Verify Account / Team Meeting")
        test_body = st.text_area("Email Body / Message:", height=120, placeholder="Paste email content here...")
        test_sender = st.text_input("Sender Address (optional):", placeholder="e.g., hr-team@example.com")

        if st.button("🔍 Analyze Email Spam % & Notify", type="primary"):
            if not test_subj and not test_body:
                st.warning("Please enter at least a subject or body text to analyze.")
            else:
                analysis = spam_classifier.classify(subject=test_subj, body=test_body, sender=test_sender)
                score = analysis["spam_score"]
                confidence = analysis["confidence"]
                is_sp = analysis["is_spam"]

                st.markdown("#### Analysis Results:")
                res_col1, res_col2 = st.columns([1, 2])
                with res_col1:
                    if is_sp:
                        st.error(f"⚠️ SPAM DETECTED\n\n**Risk Score:** {score}%")
                        notify_spam_email(email_id=1)
                    else:
                        st.success(f"📩 SAFE / CLEAN EMAIL\n\n**Confidence:** {confidence}%")
                        notify_safe_email()

                with res_col2:
                    st.markdown("**Evidence & Forensic Analysis:**")
                    for ev in analysis.get("evidence", []):
                        st.markdown(f"- 🔴 {ev}")
                    st.caption("Desktop pop-up notification fired!")
