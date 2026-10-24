"""
ScamGraph AI - Settings Page
Application configuration and integration management.
"""

import streamlit as st

from scamgraph.config import config
from scamgraph.ui.theme import get_theme


def render_settings() -> None:
    """Render the settings page."""
    theme = get_theme()

    # Page header
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0;">Settings</h1>
            <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Configure ScamGraph AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # General settings
    st.markdown("### General")
    with st.container():
        st.markdown(
            f"""
            <div class="scamgraph-card">
                <h3 style="margin-top: 0;">Application</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">App Name</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0;">{config.app.name}</p>
                    </div>
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Version</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0;">{config.app.version}</p>
                    </div>
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Debug Mode</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0;">{'Enabled' if config.app.debug else 'Disabled'}</p>
                    </div>
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Log Level</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0;">{config.app.log_level}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Database settings
    st.markdown("### Database")
    with st.container():
        st.markdown(
            f"""
            <div class="scamgraph-card">
                <h3 style="margin-top: 0;">SQLite Database</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Path</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0; font-family: monospace; font-size: 0.85rem;">{config.database.path}</p>
                    </div>
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Status</label>
                        <p style="color: {theme['success']}; margin: 0.25rem 0 0;">Connected ✓</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Integrations
    st.markdown("### Integrations (Future)")
    st.caption("These integrations will be implemented in future phases. Configure API keys in your .env file.")

    integrations = [
        {
            "name": "Gmail API",
            "description": "Fetch emails directly from Gmail for investigation",
            "configured": config.gmail.is_configured,
            "keys": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REDIRECT_URI"],
        },
        {
            "name": "OpenAI",
            "description": "GPT models for evidence analysis and report generation",
            "configured": config.ai.openai_api_key is not None,
            "keys": ["OPENAI_API_KEY"],
        },
        {
            "name": "Anthropic",
            "description": "Claude models for advanced reasoning and analysis",
            "configured": config.ai.anthropic_api_key is not None,
            "keys": ["ANTHROPIC_API_KEY"],
        },
        {
            "name": "TinyFish Research",
            "description": "Threat intelligence and reputation data",
            "configured": config.tinyfish.api_key is not None,
            "keys": ["TINYFISH_API_KEY"],
        },
    ]

    for integration in integrations:
        status_color = theme["success"] if integration["configured"] else theme["warning"]
        status_text = "Configured" if integration["configured"] else "Not Configured"

        with st.expander(f"{integration['name']} - {status_text}", expanded=not integration["configured"]):
            st.markdown(f"**Description:** {integration['description']}")
            st.markdown(f"**Status:** <span style='color: {status_color};'>{status_text}</span>", unsafe_allow_html=True)
            st.markdown("**Required Environment Variables:**")
            for key in integration["keys"]:
                value = "✅ Set" if (key == "GMAIL_CLIENT_ID" and config.gmail.client_id) or \
                                 (key == "GMAIL_CLIENT_SECRET" and config.gmail.client_secret) or \
                                 (key == "GMAIL_REDIRECT_URI" and config.gmail.redirect_uri) or \
                                 (key == "OPENAI_API_KEY" and config.ai.openai_api_key) or \
                                 (key == "ANTHROPIC_API_KEY" and config.ai.anthropic_api_key) or \
                                 (key == "TINYFISH_API_KEY" and config.tinyfish.api_key) else "❌ Missing"
                st.markdown(f"  - `{key}`: {value}")

    # Security settings
    st.markdown("### Security")
    with st.container():
        st.markdown(
            f"""
            <div class="scamgraph-card">
                <h3 style="margin-top: 0;">Session & Security</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Session Timeout</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0;">{config.security.session_timeout_minutes} minutes</p>
                    </div>
                    <div>
                        <label style="color: {theme['text_secondary']}; font-size: 0.85rem;">Secret Key</label>
                        <p style="color: {theme['text_primary']}; margin: 0.25rem 0 0; font-family: monospace; font-size: 0.75rem;">{'*' * 20}...{config.security.secret_key[-4:] if len(config.security.secret_key) > 4 else '****'}</p>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: {theme['surface_light']}; border-radius: 6px; border: 1px solid {theme['border']};">
                    <strong style="color: {theme['text_primary']};">⚠️ Security Notes:</strong>
                    <ul style="color: {theme['text_secondary']}; margin: 0.5rem 0 0; padding-left: 1.5rem;">
                        <li>Change SECRET_KEY in .env for production use</li>
                        <li>Never commit .env file to version control</li>
                        <li>Use strong, unique API keys for each integration</li>
                        <li>Regularly rotate credentials</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # About
    st.markdown("### About")
    with st.container():
        st.markdown(
            f"""
            <div class="scamgraph-card">
                <h3 style="margin-top: 0;">ScamGraph AI</h3>
                <p style="color: {theme['text_secondary']};">
                    A modern AI-powered scam investigation platform built with Python and Streamlit.
                    Designed for security researchers, fraud analysts, and cybersecurity professionals.
                </p>
                <div style="margin-top: 1rem;">
                    <strong style="color: {theme['text_primary']};">Phase 1 - Foundation</strong>
                    <ul style="color: {theme['text_secondary']}; margin: 0.5rem 0 0; padding-left: 1.5rem;">
                        <li>✅ Project structure & configuration</li>
                        <li>✅ Dark theme dashboard UI</li>
                        <li>✅ SQLite database with schema</li>
                        <li>✅ Logging & error handling</li>
                        <li>✅ Modular architecture for future features</li>
                    </ul>
                </div>
                <div style="margin-top: 1rem;">
                    <strong style="color: {theme['text_primary']};">Planned Phases:</strong>
                    <ul style="color: {theme['text_secondary']}; margin: 0.5rem 0 0; padding-left: 1.5rem;">
                        <li>Phase 2: Gmail integration & evidence ingestion</li>
                        <li>Phase 3: Supervisor Agent & specialist agents</li>
                        <li>Phase 4: TinyFish research & risk scoring</li>
                        <li>Phase 5: Interactive ScamGraph visualization</li>
                        <li>Phase 6: Safe email actions (report, block, archive)</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )