"""
ScamGraph AI - Evidence Page
Manage and analyze collected evidence.
"""

import sqlite3
from dataclasses import asdict

import streamlit as st

from scamgraph.config import get_logger
from scamgraph.database import get_db
from scamgraph.ui.theme import get_theme
from scamgraph.utils.evidence_import import (
    EVIDENCE_TYPES,
    EvidenceImportRecord,
    parse_evidence_csv,
)
from scamgraph.utils.helpers import (
    extract_domains,
    extract_emails,
    extract_phones,
    extract_urls,
)

logger = get_logger(__name__)


def render_evidence() -> None:
    """Render the evidence management page."""
    theme = get_theme()
    database = get_db()
    investigations = database.list_investigations()
    investigation_titles = {row["id"]: row["title"] for row in investigations}

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

    if st.session_state.get("show_add_evidence", False):
        with st.form("add_evidence_form"):
            st.markdown("### Add New Evidence")
            evidence_type = st.selectbox("Evidence Type*", EVIDENCE_TYPES)
            source = st.text_input("Source", placeholder="e.g., Gmail, SMS, Manual Entry")
            content = st.text_area(
                "Content*", placeholder="Paste the evidence content here...", height=150
            )
            investigation_id = None
            if investigations:
                investigation_id = st.selectbox(
                    "Investigation*",
                    options=list(investigation_titles),
                    format_func=lambda value: investigation_titles[value],
                )
            else:
                st.info("Import a CSV and create an investigation before adding evidence.")

            if content:
                with st.expander("Auto-Detected Indicators", expanded=True):
                    emails = extract_emails(content)
                    phones = extract_phones(content)
                    domains = extract_domains(content)
                    urls = extract_urls(content)

                    cols = st.columns(4)
                    for col, label, values in zip(
                        cols,
                        ("Emails", "Phones", "Domains", "URLs"),
                        (emails, phones, domains, urls),
                    ):
                        with col:
                            st.metric(label, len(values))
                            if values:
                                st.caption(", ".join(values[:3]))

            submit_col1, submit_col2 = st.columns(2)
            with submit_col1:
                submitted = st.form_submit_button(
                    "Add Evidence", type="primary", use_container_width=True
                )
            with submit_col2:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not content.strip():
                    st.error("Content is required.")
                elif investigation_id is None:
                    st.error("Select an investigation before adding evidence.")
                else:
                    record = EvidenceImportRecord(
                        type=evidence_type,
                        source=source.strip() or None,
                        content=content.strip(),
                    )
                    try:
                        database.import_evidence(
                            [asdict(record)],
                            investigation_id=investigation_id,
                        )
                    except (sqlite3.Error, ValueError):
                        logger.exception("Could not save evidence")
                        st.error("Evidence could not be saved. Check the application logs.")
                    else:
                        st.success("Evidence added.")
                        st.session_state.show_add_evidence = False
                        st.rerun()

            if cancelled:
                st.session_state.show_add_evidence = False
                st.rerun()

    st.divider()

    with st.expander("Import evidence from CSV"):
        st.caption(
            "CSV files must include type and content columns. The source column is optional."
        )
        uploaded_file = st.file_uploader(
            "Choose a UTF-8 CSV file",
            type=["csv"],
            key="evidence_csv_upload",
        )
        create_investigation = st.checkbox(
            "Create a new investigation for this import",
            value=not investigations,
            key="create_import_investigation",
        )
        new_investigation_title = None
        investigation_id = None
        if create_investigation or not investigations:
            new_investigation_title = st.text_input(
                "New investigation title",
                key="import_investigation_title",
            )
        else:
            investigation_id = st.selectbox(
                "Import into investigation",
                options=list(investigation_titles),
                format_func=lambda value: investigation_titles[value],
                key="import_investigation_id",
            )

        if st.button("Import CSV", type="primary", disabled=uploaded_file is None):
            try:
                records = parse_evidence_csv(uploaded_file.getvalue())
            except ValueError as error:
                st.error(str(error))
            else:
                if (
                    new_investigation_title is not None
                    and not new_investigation_title.strip()
                ):
                    st.error("Enter a title for the new investigation.")
                else:
                    try:
                        database.import_evidence(
                            [asdict(record) for record in records],
                            investigation_id=investigation_id,
                            new_investigation_title=new_investigation_title,
                        )
                    except (sqlite3.Error, ValueError):
                        logger.exception("Could not import evidence CSV")
                        st.error(
                            "Evidence could not be imported. Check the application logs."
                        )
                    else:
                        st.success(f"Imported {len(records)} evidence item(s).")
                        st.rerun()

    st.markdown("### Evidence Items")
    evidence_items = database.fetch_all(
        """
        SELECT evidence.type, evidence.source, evidence.content, evidence.collected_at,
               investigations.title AS investigation_title
        FROM evidence
        JOIN investigations ON investigations.id = evidence.investigation_id
        ORDER BY evidence.collected_at DESC, evidence.id DESC
        """
    )

    for evidence in evidence_items:
        st.markdown(f"**{evidence['type']}** · {evidence['investigation_title']}")
        st.caption(
            f"Source: {evidence['source'] or 'Not specified'} · "
            f"Collected: {evidence['collected_at']}"
        )
        st.text(evidence["content"])
        st.divider()

    if not evidence_items:
        st.info("No evidence items yet. Click 'Add Evidence' to start collecting evidence.")
