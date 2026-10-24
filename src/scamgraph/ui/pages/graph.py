"""
ScamGraph AI - Threat Relationship Graph Page (Network Action)
==============================================================
Interactive real-time threat relationship network powered by Cytoscape.js.
Strictly renders verified forensic evidence from live Gmail accounts without mock data.
"""

import streamlit as st
import streamlit.components.v1 as components

from scamgraph.database.database import db
from scamgraph.services.graph_service import build_threat_graph, generate_cytoscape_html
from scamgraph.ui.theme import get_theme


def render_graph() -> None:
    """Render the ScamGraph interactive threat network."""
    theme = get_theme()

    # Read selected email ID from query parameters or session state
    params = st.query_params
    selected_id = None
    if "id" in params:
        try:
            selected_id = int(params.get("id"))
        except Exception:
            pass

    if selected_id:
        st.session_state.selected_email_id = selected_id

    current_email_id = st.session_state.get("selected_email_id")

    # Page Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 0.8rem;">
            <h1 style="color: {theme['text_primary']}; margin: 0; font-size: 24px;">🕸️ Threat Relationship Network</h1>
            <p style="color: {theme['text_secondary']}; margin: 0.3rem 0 0; font-size: 13.5px;">
                Evidence-backed indicator relationships and cross-campaign correlations (Live Telemetry)
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh Graph", use_container_width=True):
            st.rerun()

    # Email Selector Bar
    recent_emails = db.list_email_investigations(limit=30)
    email_options = {None: "🌐 Entire Threat Network (Recent Cases)"}
    for em in recent_emails:
        badge = "🔴 SPAM" if em["is_spam"] else "🟢 SAFE"
        sub = em["subject"] or "No Subject"
        disp = sub[:35] + "..." if len(sub) > 35 else sub
        email_options[em["id"]] = f"Case #{em['id']} | {badge} | {disp} ({em['sender_email']})"

    current_index = 0
    if current_email_id in email_options:
        current_index = list(email_options.keys()).index(current_email_id)

    selected_target = st.selectbox(
        "Focus Investigation Case:",
        options=list(email_options.keys()),
        format_func=lambda x: email_options.get(x, "Unknown"),
        index=current_index
    )

    if selected_target != current_email_id:
        st.session_state.selected_email_id = selected_target
        st.rerun()

    # Build Authentic Graph Data (Zero mock data!)
    graph_data = build_threat_graph(email_id=selected_target)

    # Status & Context Bar
    if not graph_data.get("is_empty"):
        has_cross = graph_data.get("has_cross_case_relationships", False)
        t_nodes = graph_data.get("total_nodes", 0)
        t_edges = graph_data.get("total_edges", 0)

        meta_c1, meta_c2, meta_c3 = st.columns(3)
        with meta_c1:
            st.metric("Graph Nodes", t_nodes)
        with meta_c2:
            st.metric("Evidence Edges", t_edges)
        with meta_c3:
            status_text = "🔗 Multi-Case Syndicate" if has_cross else "🟢 Isolated Single Case"
            st.metric("Correlation Status", status_text)

        if not has_cross and selected_target:
            st.info("ℹ️ **No verified relationships found:** This email does not share an exact sender address, domain, or URL with any other recorded case. Showing verified indicators only.")

    # Render Interactive Cytoscape.js Component
    cytoscape_html = generate_cytoscape_html(graph_data, height=620)
    components.html(cytoscape_html, height=640, scrolling=False)

    # Detailed Correlated Cases Table (if multiple cases connected)
    if selected_target:
        correlated_cases = db.get_correlated_emails(selected_target)
        if correlated_cases:
            st.markdown("### 🔗 Correlated Evidence Across Investigations")
            st.caption("These cases were linked exclusively due to matching sender addresses or shared infrastructure:")
            for c_em in correlated_cases:
                with st.expander(f"Case #{c_em['id']}: {c_em['subject']} (From: {c_em['sender_email']})"):
                    st.write(f"**Verdict:** {'⚠️ SPAM' if c_em['is_spam'] else '📩 SAFE'} ({c_em['confidence']}%)")
                    st.write(f"**Domain:** `{c_em['sender_domain']}`")
                    st.write(f"**Received:** {c_em['received_at']}")
                    if st.button("Inspect This Correlated Case", key=f"corr_{c_em['id']}"):
                        st.session_state.selected_email_id = c_em['id']
                        st.session_state.current_page = "investigations"
                        st.rerun()
