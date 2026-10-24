"""
ScamGraph AI - Investigations Page
Manage and view scam investigations.
"""

import streamlit as st

from scamgraph.ui.theme import get_theme


def render_investigations() -> None:
    """Render the investigations management page."""
    theme = get_theme()

    # Page header with new investigation button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1rem;">
                <h1 style="color: {theme['text_primary']}; margin: 0;">Investigations</h1>
                <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Manage your scam investigation cases</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ New Investigation", use_container_width=True, type="primary"):
            st.session_state.show_new_investigation = True

    # New investigation form
    if st.session_state.get("show_new_investigation", False):
        with st.form("new_investigation_form"):
            st.markdown("### Create New Investigation")

            title = st.text_input("Investigation Title*", placeholder="e.g., Phishing Campaign - Fake Bank Login")
            st.text_area("Description", placeholder="Details about the case...")
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            with col2:
                st.selectbox("Status", ["Open", "In Progress", "Closed"])

            submit_col1, submit_col2 = st.columns(2)
            with submit_col1:
                submitted = st.form_submit_button("Create Investigation", type="primary", use_container_width=True)
            with submit_col2:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if title:
                    st.success(f"Investigation '{title}' created! (Database integration coming in Phase 2)")
                    st.session_state.show_new_investigation = False
                    st.rerun()
                else:
                    st.error("Title is required")

            if cancelled:
                st.session_state.show_new_investigation = False
                st.rerun()

    st.divider()

    # Investigations list (placeholder)
    st.markdown("### All Investigations")

    # Sample data for UI demonstration
    sample_investigations = [
        {
            "id": 1,
            "title": "Phishing Campaign - Fake Bank Login",
            "status": "In Progress",
            "risk_score": 85,
            "created": "2024-01-15",
            "entities": 12,
        },
        {
            "id": 2,
            "title": "Romance Scam - Military Impersonation",
            "status": "Open",
            "risk_score": 72,
            "created": "2024-01-10",
            "entities": 8,
        },
        {
            "id": 3,
            "title": "Tech Support Scam - Remote Access",
            "status": "Closed",
            "risk_score": 45,
            "created": "2024-01-05",
            "entities": 5,
        },
    ]

    # Display as cards
    for inv in sample_investigations:
        get_risk_color(inv["risk_score"])
        status_class = f"status-{inv['status'].lower().replace(' ', '-')}"

        st.markdown(
            f"""
            <div class="scamgraph-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div>
                        <h3 style="margin: 0; color: {theme['text_primary']};">{inv['title']}</h3>
                        <p style="margin: 0.25rem 0 0; color: {theme['text_secondary']}; font-size: 0.9rem;">Created: {inv['created']} • {inv['entities']} entities</p>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span class="risk-badge risk-{get_risk_level(inv['risk_score'])}">{inv['risk_score']}/100</span>
                        <span class="status-indicator {status_class}">{inv['status']}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <button style="background: {theme['surface_light']}; border: 1px solid {theme['border']}; color: {theme['text_primary']}; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">View Details</button>
                    <button style="background: {theme['surface_light']}; border: 1px solid {theme['border']}; color: {theme['text_primary']}; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Add Evidence</button>
                    <button style="background: {theme['surface_light']}; border: 1px solid {theme['border']}; color: {theme['text_primary']}; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">View Graph</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not sample_investigations:
        st.info("No investigations yet. Click 'New Investigation' to create your first case.")


def get_risk_level(score: float) -> str:
    """Get risk level label from score."""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "low"
    return "none"


def get_risk_color(score: float) -> str:
    """Get risk color from score."""
    from scamgraph.ui.theme import RISK_COLORS
    return RISK_COLORS[get_risk_level(score)]