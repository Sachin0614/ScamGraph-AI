"""
ScamGraph AI - Evidence Page
Manage and analyze collected evidence.
"""

import streamlit as st

from scamgraph.ui.theme import get_theme
from scamgraph.utils.helpers import (
    extract_domains,
    extract_emails,
    extract_phones,
    extract_urls,
)


def render_evidence() -> None:
    """Render the evidence management page."""
    theme = get_theme()

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1rem;">
                <h1 style="color: {theme['text_primary']}; margin: 0;">Evidence</h1>
                <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Collect and analyze evidence artifacts</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Evidence", use_container_width=True, type="primary"):
            st.session_state.show_add_evidence = True

    # Add evidence form
    if st.session_state.get("show_add_evidence", False):
        with st.form("add_evidence_form"):
            st.markdown("### Add New Evidence")

            st.selectbox(
                "Evidence Type*",
                ["Email", "Phone Number", "Domain", "URL", "Text Message", "Screenshot", "Document", "Other"]
            )
            st.text_input("Source", placeholder="e.g., Gmail, SMS, Manual Entry")
            content = st.text_area("Content*", placeholder="Paste the evidence content here...", height=150)

            # Auto-extract indicators
            if content:
                with st.expander("Auto-Detected Indicators", expanded=True):
                    emails = extract_emails(content)
                    phones = extract_phones(content)
                    domains = extract_domains(content)
                    urls = extract_urls(content)

                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Emails", len(emails))
                        if emails:
                            st.caption(", ".join(emails[:3]))
                    with cols[1]:
                        st.metric("Phones", len(phones))
                        if phones:
                            st.caption(", ".join(phones[:3]))
                    with cols[2]:
                        st.metric("Domains", len(domains))
                        if domains:
                            st.caption(", ".join(domains[:3]))
                    with cols[3]:
                        st.metric("URLs", len(urls))
                        if urls:
                            st.caption(", ".join(urls[:3]))

            submit_col1, submit_col2 = st.columns(2)
            with submit_col1:
                submitted = st.form_submit_button("Add Evidence", type="primary", use_container_width=True)
            with submit_col2:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if content:
                    st.success("Evidence added! (Database integration coming in Phase 2)")
                    st.session_state.show_add_evidence = False
                    st.rerun()
                else:
                    st.error("Content is required")

            if cancelled:
                st.session_state.show_add_evidence = False
                st.rerun()

    st.divider()

    # Evidence list (placeholder)
    st.markdown("### Evidence Items")

    sample_evidence = [
        {
            "id": 1,
            "type": "Email",
            "source": "Gmail",
            "preview": "Urgent: Your account has been compromised. Click here to verify...",
            "indicators": ["support@fake-bank.com", "http://phishing-site.com"],
            "date": "2024-01-15",
        },
        {
            "id": 2,
            "type": "Phone Number",
            "source": "SMS",
            "preview": "+1 (555) 123-4567 - Call from 'Microsoft Support'",
            "indicators": ["+1 (555) 123-4567"],
            "date": "2024-01-14",
        },
        {
            "id": 3,
            "type": "Domain",
            "source": "Manual",
            "preview": "payroll-services-xyz.com - Registered 2 days ago",
            "indicators": ["payroll-services-xyz.com"],
            "date": "2024-01-13",
        },
    ]

    for ev in sample_evidence:
        st.markdown(
            f"""
            <div class="scamgraph-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                            <span style="background: {theme['primary']}; color: {theme['background']}; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{ev['type']}</span>
                            <span style="color: {theme['text_secondary']}; font-size: 0.85rem;">Source: {ev['source']}</span>
                            <span style="color: {theme['text_muted']}; font-size: 0.85rem;">{ev['date']}</span>
                        </div>
                        <p style="margin: 0; color: {theme['text_primary']}; font-family: monospace; font-size: 0.9rem;">{ev['preview']}</p>
                    </div>
                    <button style="background: {theme['surface_light']}; border: 1px solid {theme['border']}; color: {theme['text_primary']}; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Analyze</button>
                </div>
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid {theme['border']};">
                    <span style="color: {theme['text_muted']}; font-size: 0.8rem;">Indicators: </span>
                    {' '.join([f'<span style="background: {theme["surface_light"]}; color: {theme["primary"]}; padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.75rem; margin-right: 0.25rem;">{ind}</span>' for ind in ev['indicators']])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not sample_evidence:
        st.info("No evidence items yet. Click 'Add Evidence' to start collecting artifacts.")