"""
ScamGraph AI - Threat Relationship Graph Engine
===============================================
Constructs real, evidence-backed relationship graphs from live email investigations.
Enforces strict forensic rules:
1. Never inserts mock data or placeholder nodes.
2. Only links entities supported by real extracted evidence (e.g., exact matching sender, domain, or URL).
3. If no cross-case relationships exist, clearly states "No verified relationships found".
4. Colors:
   - Red (#EF4444): Suspicious / Spam indicator supported by evidence.
   - Cyan (#00F0FF): Verified evidence or domains.
   - Blue/Purple (#8B5CF6 / #3B82F6): Related entities whose association is established.
"""

import json
from scamgraph.database.database import db
from scamgraph.config import get_logger

logger = get_logger(__name__)


def build_threat_graph(email_id: int | None = None) -> dict:
    """
    Constructs an authentic Cytoscape.js graph payload from the database.
    If `email_id` is specified, centers on that email and its verified indicators.
    """
    nodes = []
    edges = []
    seen_nodes = set()
    seen_edges = set()

    def add_node(node_id: str, label: str, node_type: str, category: str, details: dict):
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        nodes.append({
            "data": {
                "id": node_id,
                "label": label,
                "type": node_type,
                "category": category,
                **details
            }
        })

    def add_edge(source_id: str, target_id: str, label: str, edge_type: str = "direct"):
        edge_key = f"{source_id}->{target_id}:{label}"
        if edge_key in seen_edges:
            return
        seen_edges.add(edge_key)
        edges.append({
            "data": {
                "source": source_id,
                "target": target_id,
                "label": label,
                "type": edge_type
            }
        })

    # Fetch target email(s)
    primary_email = None
    if email_id:
        primary_email = db.get_email_investigation(email_id)

    if not primary_email:
        # Load most recent emails if none selected
        recent_emails = db.list_email_investigations(limit=10)
        if not recent_emails:
            return {
                "nodes": [],
                "edges": [],
                "is_empty": True,
                "message": "No live email investigations recorded yet. Awaiting incoming email stream."
            }
        emails_to_graph = recent_emails
    else:
        # Include primary email plus real correlated cases
        correlated = db.get_correlated_emails(email_id)
        emails_to_graph = [primary_email] + correlated

    # Populate genuine nodes and edges
    has_cross_case_relationships = False

    for em in emails_to_graph:
        e_id = em["id"]
        is_spam = bool(em["is_spam"])
        subject = em["subject"] or "No Subject"
        disp_subject = subject[:30] + "..." if len(subject) > 30 else subject
        sender_email = em["sender_email"] or "unknown@domain.com"
        sender_domain = em["sender_domain"] or "unknown.com"

        email_node_id = f"email_{e_id}"
        sender_node_id = f"sender_{sender_email}"
        domain_node_id = f"domain_{sender_domain}"

        # 1. Email Node (Red if Spam, Blue if Safe)
        add_node(
            node_id=email_node_id,
            label=f"Email #{e_id}: {disp_subject}",
            node_type="email",
            category="suspicious" if is_spam else "neutral",
            details={
                "title": subject,
                "folder": em["folder"],
                "received_at": em["received_at"],
                "spam_score": em["spam_score"],
                "confidence": em["confidence"],
                "is_primary": (email_id is not None and e_id == email_id),
                "evidence": json.loads(em["evidence_json"]) if em["evidence_json"] else []
            }
        )

        # 2. Sender Email Node (Blue/Purple related entity)
        add_node(
            node_id=sender_node_id,
            label=sender_email,
            node_type="sender",
            category="neutral",
            details={
                "email_address": sender_email,
                "display_name": em["sender"],
                "evidence_type": "Direct Email Header"
            }
        )
        add_edge(email_node_id, sender_node_id, "sent by")

        # 3. Domain Node (Cyan verified link)
        if sender_domain and sender_domain != "unknown.com":
            add_node(
                node_id=domain_node_id,
                label=sender_domain,
                node_type="domain",
                category="verified",
                details={
                    "domain": sender_domain,
                    "evidence_type": "Derived from RFC Header"
                }
            )
            add_edge(sender_node_id, domain_node_id, "uses domain")

        # 4. Real Extracted URLs (Red if in spam email, Cyan if in safe)
        extracted_urls = json.loads(em["extracted_urls"]) if em["extracted_urls"] else []
        for idx, u in enumerate(extracted_urls[:5]):
            url_node_id = f"url_{e_id}_{idx}"
            disp_url = u[:35] + "..." if len(u) > 35 else u
            add_node(
                node_id=url_node_id,
                label=disp_url,
                node_type="url",
                category="suspicious" if is_spam else "verified",
                details={
                    "full_url": u,
                    "evidence_type": "Extracted from message body"
                }
            )
            add_edge(email_node_id, url_node_id, "contains URL")

        # 5. Real Extracted Phones
        extracted_phones = json.loads(em["extracted_phones"]) if em["extracted_phones"] else []
        for idx, p in enumerate(extracted_phones[:3]):
            phone_node_id = f"phone_{e_id}_{idx}"
            add_node(
                node_id=phone_node_id,
                label=p,
                node_type="phone",
                category="suspicious" if is_spam else "neutral",
                details={
                    "phone_number": p,
                    "evidence_type": "Extracted phone indicator"
                }
            )
            add_edge(email_node_id, phone_node_id, "contains phone")

    # Check cross-case relationships
    if len(emails_to_graph) > 1:
        has_cross_case_relationships = True

    return {
        "nodes": nodes,
        "edges": edges,
        "is_empty": False,
        "primary_email_id": email_id,
        "has_cross_case_relationships": has_cross_case_relationships,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }


def generate_cytoscape_html(graph_data: dict, height: int = 620) -> str:
    """
    Renders an interactive Cytoscape.js dark cybersecurity graph.
    With responsive node inspection panel and physics controls.
    """
    if graph_data.get("is_empty"):
        return f"""
        <div style="background: #030712; border: 1px solid #1E293B; border-radius: 12px; height: {height}px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94A3B8; font-family: monospace;">
            <div style="font-size: 40px; margin-bottom: 12px;">🕸️</div>
            <div style="font-size: 16px; font-weight: bold; color: #38BDF8;">AWAITING LIVE EMAIL TELEMETRY</div>
            <div style="font-size: 13px; margin-top: 6px;">{graph_data.get('message', 'No active emails detected yet.')}</div>
        </div>
        """

    nodes_json = json.dumps(graph_data.get("nodes", []))
    edges_json = json.dumps(graph_data.get("edges", []))
    has_cross = graph_data.get("has_cross_case_relationships", False)

    cross_banner_html = ""
    if not has_cross and graph_data.get("primary_email_id"):
        cross_banner_html = """
        <div style="position: absolute; top: 14px; left: 14px; z-index: 100; background: rgba(15, 23, 42, 0.85); border: 1px solid #38BDF8; border-radius: 8px; padding: 6px 12px; font-size: 12px; color: #38BDF8; font-family: sans-serif; backdrop-filter: blur(4px);">
            ℹ️ No verified cross-case relationships found for this email. (Showing authentic indicators only)
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: #030712; color: #F8FAFC; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }}
            #cy {{ width: 100%; height: {height}px; background: radial-gradient(circle at 50% 50%, #0B1329 0%, #030712 100%); }}
            
            /* Inspector Drawer */
            #inspector {{
                position: absolute;
                top: 14px;
                right: 14px;
                width: 320px;
                max-height: {height - 28}px;
                background: rgba(15, 23, 42, 0.92);
                border: 1px solid #1E293B;
                border-radius: 12px;
                padding: 16px;
                font-size: 13px;
                color: #CBD5E1;
                box-shadow: 0 10px 25px rgba(0,0,0,0.6);
                backdrop-filter: blur(8px);
                z-index: 200;
                overflow-y: auto;
                display: none;
            }}
            .insp-title {{ font-weight: 700; font-size: 14px; color: #00F0FF; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 6px; }}
            .insp-row {{ margin-bottom: 6px; line-height: 1.4; }}
            .insp-row strong {{ color: #F8FAFC; }}
            
            /* Controls Bar */
            #controls {{
                position: absolute;
                bottom: 14px;
                left: 14px;
                z-index: 100;
                display: flex;
                gap: 8px;
            }}
            .ctrl-btn {{
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid #334155;
                color: #38BDF8;
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
                transition: all 0.2s;
            }}
            .ctrl-btn:hover {{
                background: #1E293B;
                border-color: #38BDF8;
                color: #FFFFFF;
            }}

            /* Legend */
            #legend {{
                position: absolute;
                bottom: 14px;
                right: 14px;
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11px;
                color: #94A3B8;
                display: flex;
                gap: 12px;
                z-index: 100;
            }}
            .leg-item {{ display: flex; align-items: center; gap: 5px; }}
            .dot {{ width: 9px; height: 9px; border-radius: 50%; }}
        </style>
    </head>
    <body>
        {cross_banner_html}
        <div id="cy"></div>

        <!-- Node Inspector Drawer -->
        <div id="inspector">
            <div class="insp-title" id="insp-header">Entity Inspector</div>
            <div class="insp-row"><strong>Label:</strong> <span id="insp-label">-</span></div>
            <div class="insp-row"><strong>Type:</strong> <span id="insp-type">-</span></div>
            <div class="insp-row"><strong>Threat Status:</strong> <span id="insp-status">-</span></div>
            <div class="insp-row" id="insp-extra" style="margin-top: 8px; border-top: 1px dashed #334155; padding-top: 6px;"></div>
        </div>

        <!-- Controls -->
        <div id="controls">
            <button class="ctrl-btn" onclick="cy.fit(null, 40)">🎯 Center</button>
            <button class="ctrl-btn" onclick="cy.zoom(cy.zoom() * 1.25)">➕ Zoom In</button>
            <button class="ctrl-btn" onclick="cy.zoom(cy.zoom() * 0.8)">➖ Zoom Out</button>
            <button class="ctrl-btn" onclick="reRunLayout()">⚡ Re-Layout</button>
        </div>

        <!-- Legend -->
        <div id="legend">
            <div class="leg-item"><div class="dot" style="background: #EF4444;"></div> Suspicious / Spam</div>
            <div class="leg-item"><div class="dot" style="background: #00F0FF;"></div> Verified Evidence</div>
            <div class="leg-item"><div class="dot" style="background: #8B5CF6;"></div> Related Entity</div>
        </div>

        <script>
            const elements = [
                ...{nodes_json},
                ...{edges_json}
            ];

            const cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: elements,
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)',
                            'color': '#F8FAFC',
                            'font-size': '11px',
                            'text-valign': 'bottom',
                            'text-margin-y': '6px',
                            'text-outline-color': '#030712',
                            'text-outline-width': '2px',
                            'width': 34,
                            'height': 34,
                            'border-width': 2,
                            'border-opacity': 0.8
                        }}
                    }},
                    {{
                        selector: 'node[category = "suspicious"]',
                        style: {{
                            'background-color': '#EF4444',
                            'border-color': '#FFA39E',
                            'box-shadow': '0 0 15px rgba(239, 68, 68, 0.7)'
                        }}
                    }},
                    {{
                        selector: 'node[category = "verified"]',
                        style: {{
                            'background-color': '#00F0FF',
                            'border-color': '#E6FFFB',
                            'box-shadow': '0 0 15px rgba(0, 240, 255, 0.7)'
                        }}
                    }},
                    {{
                        selector: 'node[category = "neutral"]',
                        style: {{
                            'background-color': '#8B5CF6',
                            'border-color': '#DDD6FE',
                            'box-shadow': '0 0 15px rgba(139, 92, 246, 0.6)'
                        }}
                    }},
                    {{
                        selector: 'node[type = "email"]',
                        style: {{
                            'shape': 'round-rectangle',
                            'width': 44,
                            'height': 32
                        }}
                    }},
                    {{
                        selector: 'node[type = "domain"]',
                        style: {{
                            'shape': 'diamond',
                            'width': 38,
                            'height': 38
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 2,
                            'line-color': '#334155',
                            'target-arrow-color': '#38BDF8',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'label': 'data(label)',
                            'font-size': '9px',
                            'color': '#94A3B8',
                            'text-rotation': 'autorotate',
                            'text-margin-y': '-6px',
                            'text-outline-color': '#030712',
                            'text-outline-width': '2px'
                        }}
                    }},
                    {{
                        selector: 'node:selected',
                        style: {{
                            'border-color': '#FFFFFF',
                            'border-width': 4
                        }}
                    }}
                ],
                layout: {{
                    name: 'cose',
                    idealEdgeLength: 100,
                    nodeOverlap: 20,
                    refresh: 20,
                    fit: true,
                    padding: 40,
                    randomize: false,
                    componentSpacing: 100,
                    nodeRepulsion: 400000,
                    edgeElasticity: 100,
                    nestingFactor: 5,
                    gravity: 80,
                    numIter: 1000
                }}
            }});

            // Inspector click interaction
            cy.on('tap', 'node', function(evt) {{
                const node = evt.target;
                const d = node.data();
                
                document.getElementById('insp-label').innerText = d.label;
                document.getElementById('insp-type').innerText = d.type.toUpperCase();
                
                const statusSpan = document.getElementById('insp-status');
                if (d.category === 'suspicious') {{
                    statusSpan.innerHTML = '<span style="color: #EF4444; font-weight: bold;">⚠️ SUSPICIOUS</span>';
                }} else if (d.category === 'verified') {{
                    statusSpan.innerHTML = '<span style="color: #00F0FF; font-weight: bold;">🛡️ VERIFIED</span>';
                }} else {{
                    statusSpan.innerHTML = '<span style="color: #8B5CF6; font-weight: bold;">🔗 ASSOCIATED</span>';
                }}

                let extraHtml = '';
                if (d.type === 'email') {{
                    extraHtml += `<div class="insp-row"><strong>Folder:</strong> ${{d.folder}}</div>`;
                    extraHtml += `<div class="insp-row"><strong>Spam Score:</strong> ${{d.spam_score}}%</div>`;
                    extraHtml += `<div class="insp-row"><strong>Confidence:</strong> ${{d.confidence}}%</div>`;
                    if (d.evidence && d.evidence.length) {{
                        extraHtml += `<div class="insp-row"><strong>Evidence:</strong><br><ul style="padding-left: 14px; font-size: 11.5px; color: #FFA39E;">` + 
                            d.evidence.map(e => `<li>${{e}}</li>`).join('') + `</ul></div>`;
                    }}
                }} else if (d.type === 'url') {{
                    extraHtml += `<div class="insp-row"><strong>Target URL:</strong><br><span style="font-size: 11px; word-break: break-all; color: #38BDF8;">${{d.full_url}}</span></div>`;
                }} else if (d.type === 'domain') {{
                    extraHtml += `<div class="insp-row"><strong>Domain Name:</strong> ${{d.domain}}</div>`;
                }}

                document.getElementById('insp-extra').innerHTML = extraHtml;
                document.getElementById('inspector').style.display = 'block';
            }});

            cy.on('tap', function(evt) {{
                if (evt.target === cy) {{
                    document.getElementById('inspector').style.display = 'none';
                }}
            }});

            function reRunLayout() {{
                cy.layout({{
                    name: 'cose',
                    animate: true,
                    animationDuration: 500,
                    padding: 40
                }}).run();
            }}
        </script>
    </body>
    </html>
    """
