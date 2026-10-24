"""
ScamGraph AI - Dashboard Page
Main dashboard view with overview metrics and quick actions.
"""

import streamlit as st

from scamgraph.config import config
from scamgraph.ui.theme import get_theme


def render_dashboard() -> None:
    """Render the main dashboard page."""
    theme = get_theme()

    # Page header
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0;">Dashboard</h1>
            <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Overview of your scam investigations</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {theme['primary']};">0</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">Active Investigations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {theme['info']};">0</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">Total Evidence Items</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {theme['warning']};">0</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">Graph Entities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="scamgraph-card" style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {theme['success']};">0</div>
                <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">Risk Alerts</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Quick actions
    st.markdown("### Quick Actions")

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("🔍 New Investigation", use_container_width=True, type="primary"):
            st.session_state.current_page = "investigations"
            st.rerun()

    with action_col2:
        if st.button("📁 Add Evidence", use_container_width=True):
            st.session_state.current_page = "evidence"
            st.rerun()

    with action_col3:
        if st.button("🕸️ View ScamGraph", use_container_width=True):
            st.session_state.current_page = "graph"
            st.rerun()

    st.divider()

    # Recent activity placeholder
    st.markdown("### Recent Activity")
    st.info("No recent activity. Start by creating a new investigation.")

    # System info
    with st.expander("System Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**App Version:** {config.app.version}")
            st.markdown(f"**Database:** {config.database.path}")
        with col2:
            st.markdown(f"**Debug Mode:** {'Enabled' if config.app.debug else 'Disabled'}")
            st.markdown(f"**Log Level:** {config.app.log_level}")

        st.markdown("---")
        st.markdown("**Future Integrations Status:**")
        integrations = [
            ("Gmail API", config.gmail.is_configured),
            ("OpenAI", config.ai.openai_api_key is not None),
            ("Anthropic", config.ai.anthropic_api_key is not None),
            ("TinyFish", config.tinyfish.api_key is not None),
        ]
        for name, configured in integrations:
            status = "✅ Configured" if configured else "❌ Not Configured"
            color = theme["success"] if configured else theme["text_muted"]
            st.markdown(f"<span style='color: {color};'>{name}: {status}</span>", unsafe_allow_html=True)