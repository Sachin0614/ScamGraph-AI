"""
ScamGraph AI - UI Pages Package
"""

from scamgraph.ui.pages.dashboard import render_dashboard
from scamgraph.ui.pages.evidence import render_evidence
from scamgraph.ui.pages.graph import render_graph
from scamgraph.ui.pages.investigations import render_investigations
from scamgraph.ui.pages.settings import render_settings

__all__ = [
    "render_dashboard",
    "render_evidence",
    "render_graph",
    "render_investigations",
    "render_settings",
]