"""BYD Thailand EV Research Hub — executive landing page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from utils.data_loader import load_survey
from utils.styles import apply_byd_theme, sidebar_brand

st.set_page_config(
    page_title="BYD Thailand EV Research",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_byd_theme()

with st.spinner("Loading data…"):
    df, age_order, income_order, dd_order = load_survey()

# ── Sidebar brand ──────────────────────────────────────────────────────────────
sidebar_brand()
st.sidebar.markdown(
    "<p style='color:#A8C8E8;font-size:0.78rem;padding:0 0.25rem'>"
    "Select a section from the navigation above to begin analysis.</p>",
    unsafe_allow_html=True,
)

# ── Hero banner ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:linear-gradient(90deg,#d70c19 0%,#7a0510 100%);
                padding:2.5rem 2.5rem 2rem;border-radius:14px;margin-bottom:2rem;
                box-shadow:0 6px 30px rgba(215,12,25,0.2)">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.6rem">
            <div style="background:white;padding:4px 14px;border-radius:6px">
                <span style="color:#d70c19;font-weight:900;font-size:1.4rem;letter-spacing:0.06em">BYD</span>
            </div>
            <span style="color:#f8b4b8;font-size:0.75rem;text-transform:uppercase;
                         letter-spacing:0.14em;font-weight:500">Thailand Market Intelligence</span>
        </div>
        <h1 style="margin:0;color:white;font-size:2rem;font-weight:800;line-height:1.2;border:none;padding:0">
            EV Consumer Research Hub
        </h1>
        <p style="margin:0.6rem 0 0;color:#f8b4b8;font-size:1rem;max-width:680px">
            Combined quantitative survey (306 respondents, 3 data sources), qualitative
            consumer interviews (19 respondents), and BYD sales staff interviews (5 dealerships) — analysed for IMC strategy development.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI strip ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total respondents", f"{len(df):,}")
c2.metric("General online", f"{(df['data_source'] == 'general').sum():,}")
c3.metric("Motor show", f"{(df['data_source'] == 'motor_show').sum():,}")
c4.metric("China survey", f"{(df['data_source'] == 'survey_china').sum():,}")
c5.metric("Consumer interviews", "19")
c6.metric("Sales staff interviews", "5")

st.markdown("<br>", unsafe_allow_html=True)

# ── Two-column overview ────────────────────────────────────────────────────────
col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.markdown(
        """
        <div style="background:white;border:1px solid #e2ddd6;border-radius:12px;
                    padding:1.5rem 1.75rem;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
            <h3 style="margin-top:0;color:#111111;border:none;padding:0">Research Sections</h3>
        """,
        unsafe_allow_html=True,
    )

    sections = [
        ("Survey Analysis", [
            ("01", "Demographics", "Who responded: age, gender, income, location, driving distance"),
            ("02", "Powertrain Preferences", "BEV / PHEV / HEV / ICE adoption by segment"),
            ("03", "Purchase Factors", "Decision drivers, top-3 factors, EV barriers"),
            ("04", "Cross Analysis", "Demographics × EV readiness, income, driving distance"),
            ("05", "Brand Positioning", "BYD vs. Toyota / Honda / Tesla consideration maps"),
            ("06", "Segments & EV Readiness", "Persona clusters, likelihood to switch timeline"),
        ]),
        ("Qualitative Research", [
            ("07", "Key Findings", "Survey data + interview quotes aligned by theme"),
            ("08", "Interview Deep Dive", "19 consumer profiles, 4 personas, barriers heatmap, + 5 sales staff interviews"),
        ]),
        ("Strategy", [
            ("09", "IMC Strategy Dashboard", "Gen Z (BEV) vs. Middle Age (PHEV) channel & message guide"),
        ]),
        ("Deep Dive", [
            ("10", "Deep Dive — PMF Analysis", "Age/income × barriers, sweet spots, budget fit, BYD consideration map"),
            ("11", "Needs-Based Personas", "Family, Cost, and Time personas built from 19 in-depth interviews"),
            ("13", "Product-Market Fit", "BYD model × persona matching, pain-point solutions, BYD vs incumbents, campaign briefs"),
        ]),
    ]

    for group, items in sections:
        st.markdown(
            f'<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;'
            f'color:#d70c19;font-weight:700;margin:1rem 0 0.4rem">{group}</p>',
            unsafe_allow_html=True,
        )
        for num, name, desc in items:
            st.markdown(
                f'<div style="display:flex;gap:0.75rem;padding:0.45rem 0;'
                f'border-bottom:1px solid #e2ddd6">'
                f'<span style="background:#d70c19;color:white;font-size:0.68rem;font-weight:700;'
                f'padding:2px 7px;border-radius:4px;align-self:flex-start;flex-shrink:0;margin-top:2px">{num}</span>'
                f'<div><strong style="color:#111111;font-size:0.9rem">{name}</strong>'
                f'<br><span style="color:#6b7280;font-size:0.78rem">{desc}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    st.markdown(
        """
        <div style="background:white;border:1px solid #e2ddd6;border-radius:12px;
                    padding:1.5rem 1.75rem;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
            <h3 style="margin-top:0;color:#111111;border:none;padding:0">Data Sources</h3>
        """,
        unsafe_allow_html=True,
    )

    sources = [
        ("General online survey", f"{(df['data_source'] == 'general').sum():,}", "Google Forms · Thai / English"),
        ("Motor show survey", f"{(df['data_source'] == 'motor_show').sum():,}", "Booth intercept · Thai"),
        ("China survey", f"{(df['data_source'] == 'survey_china').sum():,}", "Administered · Chinese / English"),
        ("Consumer in-depth interviews", "19", "Semi-structured · Thai + English"),
        ("Sales staff interviews", "5", "BYD dealership staff · Thai + English"),
    ]

    for name, n, note in sources:
        st.markdown(
            f'<div style="border-left:3px solid #d70c19;padding:0.5rem 0.75rem;'
            f'margin-bottom:0.6rem;background:#f3f4f6;border-radius:0 6px 6px 0">'
            f'<strong style="color:#111111;font-size:0.88rem">{name}</strong>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.1rem">'
            f'<span style="color:#6b7280;font-size:0.75rem">{note}</span>'
            f'<span style="background:#1a1a1a;color:white;font-size:0.75rem;font-weight:700;'
            f'padding:1px 7px;border-radius:10px">n = {n}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <hr style="border-color:#e2ddd6;margin:1rem 0"/>
        <p style="font-size:0.8rem;color:#6b7280;margin:0">
            <strong style="color:#111111">EV Readiness Index (1–10)</strong> — composite score:<br>
            Likelihood to switch in 3y&nbsp; <span style="color:#d70c19;font-weight:700">35%</span> ·
            Charging convenience&nbsp; <span style="color:#d70c19;font-weight:700">35%</span> ·
            BEV/PHEV familiarity&nbsp; <span style="color:#d70c19;font-weight:700">30%</span>
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#B0BEC5;font-size:0.72rem;padding:0.5rem 0">'
    'BYD Thailand EV Research · Confidential · Use filters on each page to slice by source, age, or gender'
    '</div>',
    unsafe_allow_html=True,
)
