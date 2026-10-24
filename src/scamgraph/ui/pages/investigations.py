"""
ScamGraph AI - Email Investigation View (View Action)
=====================================================
Displays authentic forensic details for monitored emails:
- Actual sender, subject, received timestamp, email address, and message content.
- Spam classification, confidence score, and specific matched evidence.
- Real extracted URLs, domains, and phone numbers.
- Option to open original email in Gmail.
- Never invents sender details or investigation evidence.
"""

import json
import urllib.parse
import streamlit as st
from scamgraph.database.database import db
from scamgraph.ui.theme import get_theme


def render_email_detail(email_id: int):
    """Renders the comprehensive forensic view for an individual email."""
    theme = get_theme()
    email_row = db.get_email_investigation(email_id)

    if not email_row:
        st.error(f"Investigation record #{email_id} not found in database.")
        if st.button("← Back to Investigations"):
            st.session_state.selected_email_id = None
            st.rerun()
        return

    # Header Controls
    col_nav, col_actions = st.columns([2, 2])
    with col_nav:
        if st.button("← Back to All Investigations"):
            st.session_state.selected_email_id = None
            st.rerun()

    is_spam = bool(email_row["is_spam"])
    badge_color = "#EF4444" if is_spam else "#10B981"
    badge_label = f"⚠️ SPAM DETECTED ({email_row['confidence']}%)" if is_spam else f"📩 SAFE / NORMAL ({email_row['confidence']}%)"

    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1E293B; border-left: 6px solid {badge_color}; border-radius: 12px; padding: 20px; margin-top: 10px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 13px; font-weight: bold; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Case #{email_row['id']} • {email_row['folder']}</span>
            <span style="background: {badge_color}; color: white; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px;">{badge_label}</span>
        </div>
        <h2 style="color: #F8FAFC; margin: 0 0 10px 0; font-size: 22px;">{email_row['subject']}</h2>
        <div style="font-size: 13.5px; color: #CBD5E1; line-height: 1.6;">
            <strong>👤 From:</strong> {email_row['sender']} &nbsp;|&nbsp; 
            <strong>📧 Address:</strong> <code style="color: #38BDF8;">{email_row['sender_email']}</code><br>
            <strong>🌐 Domain:</strong> <code style="color: #00F0FF;">{email_row['sender_domain']}</code> &nbsp;|&nbsp; 
            <strong>🕒 Received:</strong> {email_row['received_at']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Toolbar
    act_col1, act_col2, _ = st.columns([1.5, 1.8, 2])
    with act_col1:
        # Open in Gmail button
        search_query = urllib.parse.quote(email_row['subject'] or email_row['sender_email'])
        gmail_url = f"https://mail.google.com/mail/u/0/#search/{search_query}"
        st.link_button("🌐 Open in Gmail", gmail_url, use_container_width=True)

    with act_col2:
        if st.button("🕸️ View Threat Network Graph", type="primary", use_container_width=True):
            st.session_state.current_page = "graph"
            st.session_state.selected_email_id = email_row['id']
            st.rerun()

    st.markdown("---")

    # Metrics & Classification Evidence
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 📊 Threat Score")
        st.metric("Spam Risk Score", f"{email_row['spam_score']}%", delta="High Threat" if is_spam else "Clean")
        st.metric("Confidence Level", f"{email_row['confidence']}%")
        st.caption(f"Gmail Mailbox: **{email_row['folder']}**")

    with c2:
        st.markdown("### 🔍 Specific Forensic Evidence")
        evidence_list = json.loads(email_row["evidence_json"]) if email_row["evidence_json"] else []
        if evidence_list:
            for ev in evidence_list:
                st.markdown(f"- 🔴 **Indicator:** {ev}")
        else:
            st.info("No suspicious scam triggers detected in message headers or body.")

    st.markdown("---")

    # Extracted Indicators Card
    st.markdown("### 🛡️ Extracted Forensic Indicators (Actual Artifacts)")
    urls = json.loads(email_row["extracted_urls"]) if email_row["extracted_urls"] else []
    domains = json.loads(email_row["extracted_domains"]) if email_row["extracted_domains"] else []
    phones = json.loads(email_row["extracted_phones"]) if email_row["extracted_phones"] else []

    ind_c1, ind_c2, ind_c3 = st.columns(3)
    with ind_c1:
        st.markdown("#### 🌐 Extracted Domains")
        if domains:
            for d in domains:
                st.markdown(f"- `{d}`")
        else:
            st.caption("No external domains present.")

    with ind_c2:
        st.markdown("#### 🔗 Extracted URLs")
        if urls:
            for u in urls:
                st.markdown(f"- <span style='font-size: 11px; word-break: break-all; color: #38BDF8;'>`{u}`</span>", unsafe_allow_html=True)
        else:
            st.caption("No hyperlinks present.")

    with ind_c3:
        st.markdown("#### 📞 Extracted Phone Numbers")
        if phones:
            for p in phones:
                st.markdown(f"- `{p}`")
        else:
            st.caption("No phone numbers found.")

    st.markdown("---")

    # Available Message Content
    st.markdown("### 📄 Available Message Content")
    content_display = email_row["content"] or email_row["snippet"] or "No content available."
    st.text_area("Message Body:", value=content_display, height=180, disabled=True)


def render_investigations() -> None:
    """Render the investigations management & case review page."""
    theme = get_theme()

    # Check for direct URL parameter or session state selection
    params = st.query_params
    selected_id = None
    if "id" in params:
        try:
            selected_id = int(params.get("id"))
        except Exception:
            pass

    if selected_id:
        st.session_state.selected_email_id = selected_id

    if st.session_state.get("selected_email_id"):
        render_email_detail(st.session_state.selected_email_id)
        return

    # All Investigations Overview
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0;">🔍 Email Investigations</h1>
            <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Forensic analysis, extracted indicators, and evidence classification</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh Live Feed", use_container_width=True):
            st.rerun()

    # Filter Bar
    filter_choice = st.radio(
        "Filter by Verdict:",
        ["All Investigations", "⚠️ Spam Only", "📩 Safe Only"],
        horizontal=True
    )

    spam_filter = None
    if filter_choice == "⚠️ Spam Only":
        spam_filter = True
    elif filter_choice == "📩 Safe Only":
        spam_filter = False

    records = db.list_email_investigations(limit=50, spam_only=spam_filter)

    if not records:
        st.info("No email investigations recorded yet. Once emails arrive in your connected account, they will automatically appear here.")
        return

    st.markdown(f"**Showing {len(records)} recorded investigations:**")

    for rec in records:
        is_spam = bool(rec["is_spam"])
        badge_color = "#EF4444" if is_spam else "#10B981"
        badge_text = "⚠️ SPAM" if is_spam else "📩 SAFE"

        with st.container():
            c_info, c_action = st.columns([4, 1])
            with c_info:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.5); border-left: 4px solid {badge_color}; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; border: 1px solid #1E293B;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #F8FAFC; font-size: 15px;">{rec['subject'] or 'No Subject'}</strong>
                        <span style="background: {badge_color}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{badge_text} ({rec['confidence']}%)</span>
                    </div>
                    <div style="font-size: 12.5px; color: #94A3B8;">
                        👤 <strong>From:</strong> {rec['sender_email']} &nbsp;|&nbsp; 📁 <strong>Folder:</strong> {rec['folder']} &nbsp;|&nbsp; 🕒 {rec['received_at']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_action:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button(f"🔎 Inspect Case", key=f"view_{rec['id']}", use_container_width=True):
                    st.session_state.selected_email_id = rec['id']
                    st.rerun()
