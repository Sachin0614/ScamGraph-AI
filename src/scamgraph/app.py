"""
ScamGraph AI - Main Streamlit Application
Entry point for the ScamGraph AI dashboard.
"""

import streamlit as st

from scamgraph.config import get_logger, setup_logging
from scamgraph.ui import (
    inject_custom_css,
    render_dashboard,
    render_evidence,
    render_graph,
    render_investigations,
    render_settings,
    render_sidebar,
)

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="ScamGraph AI",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/scamgraph/scamgraph-ai",
        "Report a bug": "https://github.com/scamgraph/scamgraph-ai/issues",
        "About": "ScamGraph AI v1.0.0 - AI-powered scam investigation platform",
    },
)

# Inject custom CSS
st.markdown(inject_custom_css(), unsafe_allow_html=True)


def main() -> None:
    """Main application entry point."""
    logger.info("Starting ScamGraph AI application")

    # Render sidebar and get current page
    current_page = render_sidebar()

    # Route to appropriate page
    try:
        if current_page == "dashboard":
            render_dashboard()
        elif current_page == "investigations":
            render_investigations()
        elif current_page == "evidence":
            render_evidence()
        elif current_page == "graph":
            render_graph()
        elif current_page == "settings":
            render_settings()
        else:
            render_dashboard()
    except Exception as e:
        logger.exception("Error rendering page %s", current_page)
        st.error(f"An error occurred: {e!s}")
        st.info("Please check the logs for details.")


if __name__ == "__main__":
    main()