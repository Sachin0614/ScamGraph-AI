"""
ScamGraph AI - Graph Visualization Page
Interactive network graph of scam entities and relationships.
"""

import json

import streamlit as st

from scamgraph.ui.theme import ENTITY_COLORS, get_theme


def render_graph() -> None:
    """Render the ScamGraph visualization page."""
    theme = get_theme()

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1rem;">
                <h1 style="color: {theme['text_primary']}; margin: 0;">ScamGraph</h1>
                <p style="color: {theme['text_secondary']}; margin: 0.5rem 0 0;">Visualize entity relationships and attack patterns</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Graph", use_container_width=True):
            st.rerun()

    # Graph controls
    with st.expander("Graph Controls", expanded=True):
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
        with ctrl_col1:
            st.selectbox("Layout", ["Force Directed", "Hierarchical", "Circular", "Grid"])
        with ctrl_col2:
            filter_type = st.multiselect(
                "Entity Types",
                list(ENTITY_COLORS.keys()),
                default=list(ENTITY_COLORS.keys()),
            )
        with ctrl_col3:
            min_confidence = st.slider("Min Confidence", 0.0, 1.0, 0.5, 0.1)
        with ctrl_col4:
            st.number_input("Max Nodes", 10, 500, 100, 10)

    # Placeholder for graph visualization
    st.markdown("### Network Graph")

    # Sample graph data for demonstration
    sample_nodes = [
        {"id": "1", "label": "attacker@evil.com", "type": "email", "risk": 95},
        {"id": "2", "label": "victim@company.com", "type": "email", "risk": 10},
        {"id": "3", "label": "phishing-site.com", "type": "domain", "risk": 90},
        {"id": "4", "label": "+1 (555) 123-4567", "type": "phone", "risk": 80},
        {"id": "5", "label": "fake-support@scam.net", "type": "email", "risk": 85},
        {"id": "6", "label": "malware.exe", "type": "file", "risk": 98},
        {"id": "7", "label": "192.168.1.100", "type": "ip", "risk": 70},
        {"id": "8", "label": "bitcoin:1A2b3C...", "type": "wallet", "risk": 60},
    ]

    sample_edges = [
        {"source": "1", "target": "2", "type": "sent_to", "confidence": 0.95},
        {"source": "1", "target": "3", "type": "hosted_on", "confidence": 0.90},
        {"source": "3", "target": "4", "type": "registered_to", "confidence": 0.75},
        {"source": "1", "target": "5", "type": "associated_with", "confidence": 0.85},
        {"source": "5", "target": "6", "type": "delivered", "confidence": 0.80},
        {"source": "6", "target": "7", "type": "connected_to", "confidence": 0.70},
        {"source": "2", "target": "8", "type": "paid_to", "confidence": 0.60},
    ]

    # Filter by entity types
    filtered_nodes = [n for n in sample_nodes if n["type"] in filter_type]
    filtered_edges = [e for e in sample_edges if e["confidence"] >= min_confidence]

    # Display as interactive table for now (Plotly network graph in Phase 2)
    tab1, tab2 = st.tabs(["📊 Network View", "📋 Data Tables"])

    with tab1:
        st.info("Interactive Plotly network graph coming in Phase 2. Showing data preview below.")

        # Show graph stats
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Nodes", len(filtered_nodes))
        with stat_col2:
            st.metric("Edges", len(filtered_edges))
        with stat_col3:
            high_risk = sum(1 for n in filtered_nodes if n["risk"] >= 70)
            st.metric("High Risk Nodes", high_risk)
        with stat_col4:
            avg_risk = sum(n["risk"] for n in filtered_nodes) / len(filtered_nodes) if filtered_nodes else 0
            st.metric("Avg Risk Score", f"{avg_risk:.0f}")

        # Node legend
        st.markdown("#### Entity Types")
        legend_cols = st.columns(len(ENTITY_COLORS))
        for idx, (etype, color) in enumerate(ENTITY_COLORS.items()):
            with legend_cols[idx % len(legend_cols)]:
                count = sum(1 for n in filtered_nodes if n["type"] == etype)
                if count > 0:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background: {theme['surface']}; border-radius: 6px; border: 1px solid {theme['border']};">
                            <span style="width: 12px; height: 12px; background: {color}; border-radius: 50%;"></span>
                            <span style="font-size: 0.85rem;">{etype.title()} ({count})</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Nodes (Entities)**")
            st.dataframe(
                filtered_nodes,
                column_config={
                    "id": "ID",
                    "label": "Label",
                    "type": "Type",
                    "risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=100),
                },
                hide_index=True,
                use_container_width=True,
            )

        with col2:
            st.markdown("**Edges (Relationships)**")
            st.dataframe(
                filtered_edges,
                column_config={
                    "source": "Source",
                    "target": "Target",
                    "type": "Relationship",
                    "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1),
                },
                hide_index=True,
                use_container_width=True,
            )

    # Export options
    st.divider()
    st.markdown("### Export")
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        if st.button("📥 Export JSON", use_container_width=True):
            graph_data = {"nodes": filtered_nodes, "edges": filtered_edges}
            st.download_button(
                "Download Graph JSON",
                data=json.dumps(graph_data, indent=2),
                file_name="scamgraph_export.json",
                mime="application/json",
            )
    with exp_col2:
        if st.button("📊 Export CSV (Nodes)", use_container_width=True):
            import pandas as pd
            df = pd.DataFrame(filtered_nodes)
            st.download_button(
                "Download Nodes CSV",
                data=df.to_csv(index=False),
                file_name="scamgraph_nodes.csv",
                mime="text/csv",
            )
    with exp_col3:
        if st.button("🔗 Export CSV (Edges)", use_container_width=True):
            import pandas as pd
            df = pd.DataFrame(filtered_edges)
            st.download_button(
                "Download Edges CSV",
                data=df.to_csv(index=False),
                file_name="scamgraph_edges.csv",
                mime="text/csv",
            )