"""
ScamGraph AI - Settings & Integration Management
================================================
Configure connected Gmail account, TinyFish API key, and system parameters.
"""

import json
import os
from pathlib import Path
import streamlit as st

from scamgraph.config import config
from scamgraph.services.email_monitor import email_monitor
from scamgraph.services.tinyfish_service import is_tinyfish_active, get_tinyfish_key
from scamgraph.ui.theme import get_theme

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
ENV_FILE = BASE_DIR / ".env"


def render_settings() -> None:
    """Render the settings page."""
    theme = get_theme()

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0; font-size: 26px;">⚙️ System Settings & Integrations</h1>
            <p style="color: {theme['text_secondary']}; margin: 0.3rem 0 0; font-size: 14px;">
                Manage connected email accounts, TinyFish threat intelligence, and monitoring daemon
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Gmail Real-Time Monitoring Integration
    st.markdown("### 📧 Gmail Real-Time Integration")
    saved_email = os.getenv("GMAIL_ADDRESS", "")
    saved_pwd = os.getenv("GMAIL_APP_PASSWORD", "")

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                c = json.load(f)
                saved_email = c.get("email", saved_email)
                saved_pwd = c.get("app_password", saved_pwd)
        except Exception:
            pass

    with st.container():
        st.markdown(f"""
        <div class="scamgraph-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <strong style="font-size: 15px; color: #F8FAFC;">Connected Gmail Account</strong>
                <span style="background: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">
                    {email_monitor.connection_status.upper()}
                </span>
            </div>
            <p style="color: #94A3B8; font-size: 13px; margin-bottom: 12px;">
                Monitoring both <strong>INBOX</strong> and <strong>SPAM</strong> folders continuously.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_em, col_pw = st.columns(2)
        with col_em:
            new_email = st.text_input("Gmail Address:", value=saved_email)
        with col_pw:
            new_pwd = st.text_input("16-char Google App Password:", value=saved_pwd, type="password")

        if st.button("💾 Save Gmail Credentials"):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"email": new_email.strip(), "app_password": new_pwd.strip().replace(" ", "")}, f, indent=4)
            st.success("Credentials saved to config.json! Email monitor will use these on next poll.")
            st.rerun()

    st.markdown("---")

    # 2. TinyFish AI Threat Intelligence
    st.markdown("### 🐟 TinyFish AI Web Intelligence")
    tf_active = is_tinyfish_active()
    tf_status = "Connected ✓" if tf_active else "Pending Key"
    tf_color = theme["success"] if tf_active else theme["warning"]

    st.markdown(f"""
    <div class="scamgraph-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="color: #F8FAFC;">TinyFish AI Agent Status</strong>
            <span style="color: {tf_color}; font-weight: bold;">{tf_status}</span>
        </div>
        <p style="color: #94A3B8; font-size: 13px; margin: 6px 0 0 0;">
            Used for automated OSINT verification of suspicious URLs and domains discovered in incoming emails.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tf_key_input = st.text_input("TinyFish API Key (stored in .env):", value=get_tinyfish_key() or "", type="password")
    if st.button("💾 Update TinyFish API Key"):
        # Update .env file
        env_lines = []
        if ENV_FILE.exists():
            with open(ENV_FILE, "r") as f:
                env_lines = f.readlines()

        new_lines = []
        found_key = False
        for line in env_lines:
            if line.startswith("TINYFISH_API_KEY="):
                new_lines.append(f"TINYFISH_API_KEY={tf_key_input.strip()}\n")
                found_key = True
            else:
                new_lines.append(line)
        if not found_key:
            new_lines.append(f"TINYFISH_API_KEY={tf_key_input.strip()}\n")

        with open(ENV_FILE, "w") as f:
            f.writelines(new_lines)

        os.environ["TINYFISH_API_KEY"] = tf_key_input.strip()
        st.success("TinyFish API Key updated in .env!")
        st.rerun()

    st.markdown("---")

    # 3. Database Telemetry
    st.markdown("### 🗄️ Database Information")
    st.markdown(f"""
    <div class="scamgraph-card">
        <div style="font-size: 13.5px; color: #CBD5E1; line-height: 1.6;">
            <strong>Database Path:</strong> <code>{config.database.full_path}</code><br>
            <strong>Mode:</strong> SQLite WAL (Write-Ahead Logging enabled)<br>
            <strong>Storage:</strong> Investigations, Entities, Relationships, and Real-Time Email Forensics
        </div>
    </div>
    """, unsafe_allow_html=True)
