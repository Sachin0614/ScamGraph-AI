"""
ScamGraph AI - Sidebar Component
Navigation and controls sidebar for the dashboard.
"""

import streamlit as st

from scamgraph.ui.theme import get_theme, inject_custom_css


def render_sidebar() -> str:
    """
    Render the sidebar navigation.

    Returns:
        Selected page identifier
    """
    theme = get_theme()

    # Inject custom CSS
    st.markdown(inject_custom_css(), unsafe_allow_html=True)

    with st.sidebar:
        # Logo/Brand
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid {theme['border']}; margin-bottom: 1rem;">
                <h1 style="color: {theme['primary']}; margin: 0; font-size: 1.5rem;">🕸️ ScamGraph AI</h1>
                <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0; font-size: 0.8rem;">Scam Investigation Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown("### Navigation")

        pages = {
            "dashboard": "📊 Dashboard",
            "investigations": "🔍 Investigations",
            "evidence": "📁 Evidence",
            "graph": "🕸️ ScamGraph",
            "settings": "⚙️ Settings",
        }

        # Initialize session state for page selection
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        # Render navigation buttons
        for page_key, page_label in pages.items():
            is_active = st.session_state.current_page == page_key
            button_style = "primary" if is_active else "secondary"

            if st.button(page_label, key=f"nav_{page_key}", use_container_width=True, type=button_style):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        # Quick stats (placeholder for future)
        st.markdown("### Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Investigations", "0", delta="0")
        with col2:
            st.metric("Entities", "0", delta="0")

        st.divider()

        # System status
        st.markdown("### System Status")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background: {theme['surface']}; border-radius: 6px; border: 1px solid {theme['border']};">
                <span style="width: 8px; height: 8px; background: {theme['success']}; border-radius: 50%;"></span>
                <span style="color: {theme['text_secondary']}; font-size: 0.85rem;">System Operational</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Version info
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; color: {theme['text_muted']}; font-size: 0.75rem;">
                ScamGraph AI v1.0.0<br>
                Phase 1 - Foundation
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.current_page