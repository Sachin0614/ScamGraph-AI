"""
ScamGraph AI - UI Theme Configuration
Dark theme styling for Streamlit application.
"""

# Dark theme color palette
DARK_THEME = {
    "primary": "#00D4AA",
    "primary_dark": "#00B894",
    "secondary": "#6C5CE7",
    "background": "#0E1117",
    "surface": "#1E2329",
    "surface_light": "#2D343C",
    "text_primary": "#FAFAFA",
    "text_secondary": "#A0AEC0",
    "text_muted": "#718096",
    "border": "#2D343C",
    "success": "#00D4AA",
    "warning": "#F6AD55",
    "danger": "#FC8181",
    "info": "#63B3ED",
}

# Light theme color palette (for reference)
LIGHT_THEME = {
    "primary": "#00B894",
    "primary_dark": "#00A085",
    "secondary": "#5A67D8",
    "background": "#FFFFFF",
    "surface": "#F7FAFC",
    "surface_light": "#EDF2F7",
    "text_primary": "#1A202C",
    "text_secondary": "#4A5568",
    "text_muted": "#718096",
    "border": "#E2E8F0",
    "success": "#00B894",
    "warning": "#DD6B20",
    "danger": "#E53E3E",
    "info": "#3182CE",
}

# Risk score color mapping
RISK_COLORS = {
    "critical": "#FC8181",    # Red
    "high": "#F6AD55",        # Orange
    "medium": "#63B3ED",      # Blue
    "low": "#00D4AA",         # Green
    "none": "#718096",        # Gray
}

# Entity type colors for graph visualization
ENTITY_COLORS = {
    "email": "#63B3ED",
    "phone": "#F6AD55",
    "domain": "#00D4AA",
    "url": "#FC8181",
    "ip": "#B794F4",
    "person": "#FC8181",
    "organization": "#00D4AA",
    "bitcoin": "#F6AD55",
    "wallet": "#F6AD55",
    "unknown": "#718096",
}

# Relationship type colors
RELATIONSHIP_COLORS = {
    "sent_to": "#63B3ED",
    "received_from": "#00D4AA",
    "linked_to": "#F6AD55",
    "hosted_on": "#B794F4",
    "registered_to": "#FC8181",
    "associated_with": "#718096",
}


def get_risk_level(score: float) -> str:
    """
    Get risk level label from score.

    Args:
        score: Risk score (0-100)

    Returns:
        Risk level string
    """
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "low"
    return "none"


def get_risk_color(score: float) -> str:
    """
    Get risk color from score.

    Args:
        score: Risk score (0-100)

    Returns:
        Hex color string
    """
    return RISK_COLORS[get_risk_level(score)]


def inject_custom_css() -> str:
    """
    Generate custom CSS for dark theme.

    Returns:
        CSS string
    """
    theme = DARK_THEME
    return f"""
    <style>
    /* Override Streamlit default theme */
    .stApp {{
        background-color: {theme["background"]};
        color: {theme["text_primary"]};
    }}

    /* Sidebar */
    .css-1d391kg {{
        background-color: {theme["surface"]};
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme["text_primary"]} !important;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {theme["primary"]};
        color: {theme["background"]};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: {theme["primary_dark"]};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }}
    .stButton > button:disabled {{
        background-color: {theme["text_muted"]};
        color: {theme["text_secondary"]};
    }}

    /* Secondary button */
    .stButton > button[kind="secondary"] {{
        background-color: {theme["surface_light"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background-color: {theme["surface"]};
        border-color: {theme["primary"]};
    }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        background-color: {theme["surface"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: 6px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {theme["primary"]};
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.2);
    }}

    /* Metrics */
    .stMetric {{
        background-color: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 8px;
        padding: 1rem;
    }}
    .stMetric label {{
        color: {theme["text_secondary"]} !important;
    }}
    .stMetric div[data-testid="stMetricValue"] {{
        color: {theme["text_primary"]} !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 6px;
        color: {theme["text_primary"]};
    }}
    .streamlit-expanderContent {{
        background-color: {theme["background"]};
        border: 1px solid {theme["border"]};
        border-top: none;
        border-radius: 0 0 6px 6px;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {theme["surface"]};
        border-radius: 8px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {theme["text_secondary"]};
        border-radius: 6px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {theme["primary"]} !important;
        color: {theme["background"]} !important;
    }}

    /* Dataframes */
    .stDataFrame {{
        background-color: {theme["surface"]};
    }}

    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: {theme["primary"]};
    }}

    /* Alert boxes */
    .stAlert {{
        border-radius: 8px;
        border: none;
    }}

    /* Custom card component */
    .scamgraph-card {{
        background-color: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }}
    .scamgraph-card:hover {{
        border-color: {theme["primary"]};
        box-shadow: 0 4px 20px rgba(0, 212, 170, 0.1);
    }}

    /* Risk badge */
    .risk-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .risk-critical {{ background-color: rgba(252, 129, 129, 0.2); color: #FC8181; }}
    .risk-high {{ background-color: rgba(246, 173, 85, 0.2); color: #F6AD55; }}
    .risk-medium {{ background-color: rgba(99, 179, 237, 0.2); color: #63B3ED; }}
    .risk-low {{ background-color: rgba(0, 212, 170, 0.2); color: #00D4AA; }}
    .risk-none {{ background-color: rgba(113, 128, 150, 0.2); color: #718096; }}

    /* Status indicator */
    .status-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
    }}
    .status-open {{ background-color: rgba(99, 179, 237, 0.15); color: #63B3ED; }}
    .status-in-progress {{ background-color: rgba(246, 173, 85, 0.15); color: #F6AD55; }}
    .status-closed {{ background-color: rgba(0, 212, 170, 0.15); color: #00D4AA; }}

    /* Hide Streamlit branding */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {theme["background"]};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {theme["surface_light"]};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {theme["text_muted"]};
    }}
    </style>
    """


def get_theme() -> dict:
    """Get the active theme (dark)."""
    return DARK_THEME