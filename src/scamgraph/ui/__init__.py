"""
ScamGraph AI - UI Package
"""

from scamgraph.ui.pages import (
    render_dashboard,
    render_evidence,
    render_graph,
    render_investigations,
    render_settings,
)
from scamgraph.ui.sidebar import render_sidebar
from scamgraph.ui.theme import (
    DARK_THEME,
    ENTITY_COLORS,
    RELATIONSHIP_COLORS,
    RISK_COLORS,
    get_risk_color,
    get_risk_level,
    get_theme,
    inject_custom_css,
)

__all__ = [
    "DARK_THEME",
    "ENTITY_COLORS",
    "RELATIONSHIP_COLORS",
    "RISK_COLORS",
    "get_risk_color",
    "get_risk_level",
    "get_theme",
    "inject_custom_css",
    "render_dashboard",
    "render_evidence",
    "render_graph",
    "render_investigations",
    "render_settings",
    "render_sidebar",
]