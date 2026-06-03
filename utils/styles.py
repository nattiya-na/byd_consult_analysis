"""BYD-branded Streamlit theme — CSS injection and layout helpers."""
from __future__ import annotations
import streamlit as st

ACCENT     = "#d70c19"   # BYD red
ACCENT_DARK= "#9b0712"   # darker red for hover / depth
BG_WARM    = "#fdf7ef"   # cream background start
BG_WHITE   = "#ffffff"   # background end
TEXT_MAIN  = "#111111"   # near-black body text
TEXT_MUTED = "#6b7280"   # grey muted text
GREY_BOX   = "#f3f4f6"   # light grey for callout / text boxes
BORDER     = "#e2ddd6"   # warm grey border
SIDEBAR_BG = "#1a1a1a"   # dark sidebar base

# Chart colour palette
BYD_PALETTE = [
    "#d70c19",  # BYD red
    "#1a1a1a",  # charcoal
    "#f59e0b",  # amber
    "#2563eb",  # blue
    "#16a34a",  # green
    "#7c3aed",  # violet
    "#0891b2",  # cyan
    "#ea580c",  # orange
]

# Legacy aliases kept so other modules that import them don't break
BYD_GREEN  = "#d70c19"
BYD_NAVY   = "#1a1a1a"
BYD_TEAL   = "#9b0712"
BYD_LIGHT  = GREY_BOX
BYD_GRAY   = GREY_BOX
BYD_TEXT   = TEXT_MAIN
BYD_BORDER = BORDER
BYD_MUTED  = TEXT_MUTED

_CSS = """
<style>
/* ── Global & body background ────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    color: #111111;
}

/* Main content area — warm cream → white gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(90deg, #fdf7ef 0%, #ffffff 100%) !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}
[data-testid="block-container"] {
    padding-top: 1rem !important;
    background: transparent !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a1a 0%, #2a0a0d 100%) !important;
}

/* All sidebar text → light grey */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * { color: #e5e5e5 !important; }

/* Section heading */
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .sidebar-section-label {
    color: #ff6b7a !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 700 !important;
}

/* Widget labels above multiselects */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] div,
[data-testid="stSidebar"] label { color: #d4d4d4 !important; }

/* Caption / respondent count */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #9ca3af !important; }

/* Multiselect/selectbox INPUT BOX in sidebar — dark theme
   Higher specificity (3 attr selectors) beats global 2-attr rule that forces white. */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"]   [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.25) !important;
    color: #e5e5e5 !important;
}

/* Placeholder text inside select box */
[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="select"] input { color: #e5e5e5 !important; }

/* Selected tag chips */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: rgba(215,12,25,0.30) !important;
    color: #ffb3b8 !important;
}

/* Navigation links — multiple selectors for different Streamlit versions */
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p,
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p { color: #cccccc !important; }

[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNav"] a[aria-current="page"] p,
[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] p {
    color: #ff6b7a !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

/* ── Headings ─────────────────────────────────────────────────────────────── */
h1 {
    color: #d70c19 !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}
h2 {
    color: #d70c19 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #d70c19;
    padding-bottom: 0.3rem;
    margin-top: 1.5rem !important;
}
h3 {
    color: #111111 !important;
    font-weight: 600 !important;
}
p, li, td, th, label, span {
    color: #111111;
}

/* ── Metric cards ─────────────────────────────────────────────────────────── */
[data-testid="metric-container"],
[data-testid="stMetric"] {
    background: #f3f4f6 !important;
    border: 1px solid #e2ddd6 !important;
    border-left: 4px solid #d70c19 !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricLabel"] > div {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] > div {
    color: #111111 !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
button[role="tab"] {
    font-weight: 500 !important;
    color: #6b7280 !important;
    border-bottom: 3px solid transparent !important;
    background: transparent !important;
}
button[role="tab"][aria-selected="true"] {
    color: #d70c19 !important;
    font-weight: 700 !important;
    border-bottom-color: #d70c19 !important;
}

/* ── Info callout boxes — light grey ──────────────────────────────────────── */
[data-testid="stInfo"] {
    background: #f3f4f6 !important;
    border-left: 4px solid #9b9b9b !important;
    color: #111111 !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="stInfo"] p { color: #111111 !important; }

/* ── Warning / success boxes ─────────────────────────────────────────────── */
[data-testid="stWarning"] {
    background: #fff7ed !important;
    border-left: 4px solid #f59e0b !important;
}
[data-testid="stSuccess"] {
    background: #f3f4f6 !important;
    border-left: 4px solid #6b7280 !important;
}

/* ── Expanders ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e2ddd6 !important;
    border-radius: 10px !important;
    margin-bottom: 0.75rem !important;
    background: #f3f4f6 !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #111111 !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
    background: #ede8e0 !important;
    border-radius: 10px !important;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr { border-color: #e2ddd6 !important; margin: 1.25rem 0 !important; }

/* ── Dataframe header ─────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] table thead th {
    background-color: #1a1a1a !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ── Selectbox / multiselect (main content only) ──────────────────────────── */
/* Sidebar widgets are themed separately above with higher-specificity rules. */
[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child {
    border-color: #e2ddd6 !important;
    border-radius: 6px !important;
}

/* ── Caption text ─────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: #6b7280 !important;
    font-size: 0.8rem !important;
}

/* ── General text inside markdown ─────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] p {
    color: #111111 !important;
}
</style>
"""


def apply_byd_theme() -> None:
    """Inject the BYD theme CSS. Call once per page after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Full-width BYD-branded page header with red gradient banner."""
    sub_html = (
        f'<p style="margin:0.5rem 0 0;font-size:0.9rem;color:#f8b4b8;font-weight:400;'
        f'letter-spacing:0.01em">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#d70c19 0%,#7a0510 100%);
                    padding:1.4rem 2rem 1.3rem;border-radius:12px;margin-bottom:1.5rem;
                    box-shadow:0 4px 20px rgba(215,12,25,0.18)">
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem">
                <span style="background:white;color:#d70c19;font-weight:900;font-size:0.85rem;
                             padding:2px 9px;border-radius:4px;letter-spacing:0.08em">BYD</span>
                <span style="color:#f8b4b8;font-size:0.7rem;text-transform:uppercase;
                             letter-spacing:0.12em;font-weight:500">Thailand EV Research</span>
            </div>
            <h2 style="margin:0;color:white;font-size:1.55rem;font-weight:700;line-height:1.25;
                       border:none;padding:0">{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(metrics: list[tuple[str, str, str]]) -> None:
    """Render a row of KPI tiles. Each tuple: (label, value, delta_or_note)."""
    cols = st.columns(len(metrics))
    for col, (label, value, note) in zip(cols, metrics):
        col.metric(label, value, note)


def section_header(title: str, caption: str = "") -> None:
    """Styled section subheader with red accent bar."""
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:0.6rem;margin:1.25rem 0 0.4rem">'
        f'<span style="display:inline-block;width:4px;height:1.1em;background:#d70c19;'
        f'border-radius:2px;flex-shrink:0;align-self:center"></span>'
        f'<span style="font-size:1.05rem;font-weight:700;color:#111111">{title}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.caption(caption)


def sidebar_brand() -> None:
    """Render BYD brand mark at the top of the sidebar."""
    st.sidebar.markdown(
        """
        <div style="text-align:center;padding:1.2rem 0.5rem 0.8rem">
            <div style="background:white;display:inline-block;padding:5px 14px;
                        border-radius:6px;margin-bottom:0.4rem">
                <span style="color:#d70c19;font-weight:900;font-size:1.3rem;
                             letter-spacing:0.06em">BYD</span>
            </div>
            <p style="color:#f8b4b8;font-size:0.62rem;text-transform:uppercase;
                      letter-spacing:0.14em;margin:0;font-weight:500">
                Thailand EV Research
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0.2rem 0 0.8rem"/>',
        unsafe_allow_html=True,
    )
