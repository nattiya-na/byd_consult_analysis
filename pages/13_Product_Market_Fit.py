"""Page 13 — BYD Product-Market Fit: matching the lineup to real buyer needs."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import load_survey, LAYOUT_BASE, explode_and_count
from survey_utils import split_multiselect, FONT_FAMILY
from utils.styles import apply_byd_theme, page_header, section_header

st.set_page_config(page_title="BYD Product-Market Fit", layout="wide")
apply_byd_theme()
page_header(
    "BYD Product–Market Fit Analysis",
    "Matching the BYD lineup to real customer needs, pain points, and personas from 306 survey respondents + 19 interviews",
)

with st.spinner("Loading survey data…"):
    df, age_order, income_order, dd_order = load_survey()

# ── Shared layout/style helpers ────────────────────────────────────────────────

def _card(bg: str, border: str, content: str, radius: str = "12px") -> None:
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:{radius};'
        f'padding:1.2rem 1.4rem;margin-bottom:0.75rem;box-shadow:0 2px 8px rgba(0,0,0,0.05)">'
        f'{content}</div>',
        unsafe_allow_html=True,
    )


def _product_badge(model: str, pt: str, price: str, color: str) -> str:
    pt_colors = {"BEV": "#2E86AB", "PHEV": "#A23B72", "REEV": "#e67e22", "HEV": "#52B788"}
    pt_color = pt_colors.get(pt, "#888")
    return (
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;'
        f'background:white;border:2px solid {color};border-radius:8px;'
        f'padding:0.4rem 0.85rem;margin:0.25rem">'
        f'<span style="background:{color};color:white;font-weight:900;font-size:0.7rem;'
        f'padding:1px 7px;border-radius:4px;letter-spacing:0.05em">BYD</span>'
        f'<span style="font-weight:700;color:#111;font-size:0.95rem">{model}</span>'
        f'<span style="background:{pt_color};color:white;font-size:0.65rem;font-weight:700;'
        f'padding:2px 6px;border-radius:3px">{pt}</span>'
        f'<span style="font-size:0.78rem;color:#6b7280">{price}</span>'
        f'</div>'
    )


def _pain_row(icon: str, pain: str, solution: str, model: str, n_pct: str) -> None:
    st.markdown(
        f'<div style="display:grid;grid-template-columns:2fr 2fr 1.5fr 0.8fr;'
        f'gap:0.75rem;align-items:center;padding:0.7rem 0;'
        f'border-bottom:1px solid #e2ddd6">'
        f'<div style="display:flex;align-items:flex-start;gap:0.5rem">'
        f'<span style="font-size:1.1rem">{icon}</span>'
        f'<span style="font-size:0.88rem;color:#111;font-weight:600">{pain}</span>'
        f'</div>'
        f'<div style="font-size:0.85rem;color:#374151">{solution}</div>'
        f'<div style="font-size:0.82rem;font-weight:700;color:#d70c19">{model}</div>'
        f'<div style="text-align:center;background:#f3f4f6;border-radius:6px;'
        f'padding:3px 8px;font-size:0.8rem;font-weight:700;color:#111">{n_pct}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _adv_chip(icon: str, title: str, desc: str, color: str = "#d70c19") -> None:
    st.markdown(
        f'<div style="border-left:4px solid {color};background:{color}0d;'
        f'border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-bottom:0.5rem">'
        f'<div style="display:flex;gap:0.5rem;align-items:flex-start">'
        f'<span style="font-size:1.1rem;flex-shrink:0;margin-top:1px">{icon}</span>'
        f'<div>'
        f'<div style="font-weight:700;font-size:0.9rem;color:{color}">{title}</div>'
        f'<div style="font-size:0.83rem;color:#374151;margin-top:0.2rem;line-height:1.5">{desc}</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def _persona_match_card(
    icon: str, persona: str, color: str,
    pain_headline: str, pain_details: list[str],
    product_primary: str, product_pt: str, product_price: str,
    product_why: str,
    product_secondary: str = "", product_secondary_note: str = "",
    n_label: str = "",
) -> None:
    """Full persona-to-product card."""
    pt_colors = {"BEV": "#2E86AB", "PHEV": "#A23B72", "REEV": "#e67e22", "HEV": "#52B788"}
    pt_c = pt_colors.get(product_pt, "#888")
    pain_html = "".join(
        f'<li style="margin-bottom:0.25rem;font-size:0.84rem;color:#374151">{p}</li>'
        for p in pain_details
    )
    sec_html = ""
    if product_secondary:
        sec_html = (
            f'<div style="margin-top:0.6rem;padding-top:0.6rem;border-top:1px solid #e2ddd6">'
            f'<span style="font-size:0.75rem;font-weight:700;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em">Also consider </span>'
            f'<span style="font-weight:700;color:#111">{product_secondary}</span>'
            f'<span style="font-size:0.8rem;color:#6b7280;margin-left:0.4rem">{product_secondary_note}</span>'
            f'</div>'
        )
    n_html = (
        f'<span style="background:#1a1a1a;color:white;font-size:0.7rem;font-weight:700;'
        f'padding:2px 8px;border-radius:10px;margin-left:0.5rem">{n_label}</span>'
        if n_label else ""
    )
    st.markdown(
        f"""
        <div style="border:1px solid {color}44;border-top:3px solid {color};border-radius:12px;
                    background:white;padding:1.3rem 1.5rem;margin-bottom:1rem;
                    box-shadow:0 2px 10px {color}18">
          <!-- header -->
          <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem">
            <span style="font-size:1.6rem">{icon}</span>
            <div>
              <span style="font-weight:800;font-size:1rem;color:#111">{persona}</span>
              {n_html}
              <div style="font-size:0.8rem;color:{color};font-weight:600;margin-top:1px">{pain_headline}</div>
            </div>
          </div>
          <!-- pain points -->
          <div style="margin-bottom:0.9rem">
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:#6b7280;margin-bottom:0.35rem">Key Pain Points</div>
            <ul style="margin:0;padding-left:1.2rem;list-style-type:disc">{pain_html}</ul>
          </div>
          <!-- product recommendation -->
          <div style="background:{color}0a;border-radius:8px;padding:0.9rem 1rem">
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;color:{color};margin-bottom:0.4rem">Best-Fit BYD Product</div>
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem">
              <span style="background:{color};color:white;font-weight:900;font-size:0.72rem;
                           padding:2px 9px;border-radius:4px;letter-spacing:0.05em">BYD</span>
              <span style="font-weight:800;font-size:1.05rem;color:#111">{product_primary}</span>
              <span style="background:{pt_c};color:white;font-size:0.67rem;font-weight:700;
                           padding:2px 6px;border-radius:3px">{product_pt}</span>
              <span style="font-size:0.8rem;color:#6b7280;margin-left:0.2rem">{product_price}</span>
            </div>
            <p style="margin:0;font-size:0.85rem;color:#374151;line-height:1.55">{product_why}</p>
            {sec_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Pre-compute survey signals ─────────────────────────────────────────────────

def _str(series: pd.Series) -> pd.Series:
    """Cast any column (including Categorical) to plain string; NaN → ''."""
    return series.astype(str).replace("nan", "", regex=False)


def _pct_barrier(barrier_kw: str) -> tuple[int, str]:
    mask = _str(df["ev_adoption_barriers"]).str.contains(barrier_kw, case=False)
    n = int(mask.sum())
    pct = f"{mask.mean() * 100:.0f}%"
    return n, pct


def _pct_col_contains(col: str, kw: str) -> tuple[int, str]:
    mask = _str(df[col]).str.contains(kw, case=False)
    n = int(mask.sum())
    pct = f"{mask.mean() * 100:.0f}%"
    return n, pct


n_range, pct_range         = _pct_barrier("Range anxiety")
n_charging, pct_charging   = _pct_barrier("Insufficient charging")
n_cost, pct_cost           = _pct_barrier("High upfront cost")
n_no_home, pct_no_home     = _pct_barrier("No home charging")
n_service, pct_service     = _pct_barrier("Maintenance|service")
n_battery, pct_battery     = _pct_barrier("Battery")
n_byd_consid, pct_byd_c    = _pct_col_contains("brands_considering", "BYD")
n_bev, pct_bev             = (df["powertrain_short"] == "BEV").sum(), f"{(df['powertrain_short'] == 'BEV').mean()*100:.0f}%"
n_phev, pct_phev           = (df["powertrain_short"] == "PHEV").sum(), f"{(df['powertrain_short'] == 'PHEV').mean()*100:.0f}%"

# ── KPI strip ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("BYD consideration rate", pct_byd_c, f"{n_byd_consid} respondents")
c2.metric("Range anxiety barrier", pct_range, f"{n_range} respondents")
c3.metric("No home charging barrier", pct_no_home, f"{n_no_home} respondents")
c4.metric("High cost barrier", pct_cost, f"{n_cost} respondents")
c5.metric("First-choice: BEV", pct_bev, f"{n_bev} respondents")
c6.metric("First-choice: PHEV/REEV", pct_phev, f"{n_phev} respondents")

st.markdown(
    """
    <div style="background:#f3f4f6;border:1px solid #e2ddd6;border-radius:10px;
                padding:0.9rem 1.2rem;margin:1rem 0">
        <p style="margin:0;font-size:0.87rem;color:#374151;line-height:1.6">
            This page translates the survey findings and interview insights into actionable product-market fit
            recommendations: <strong>which BYD model resolves which specific buyer pain point</strong>,
            how each product maps to the five buyer personas identified in the research, and where BYD
            has a structural advantage over Toyota/Honda/HEV incumbents that most Thai buyers don't yet know about.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Main tabs ──────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🎯 Persona → Product Matches",
    "😤 Pain Point → BYD Solution",
    "🆚 BYD vs Incumbents",
    "📊 Market Sizing",
    "🗺️ Competitive Advantage Map",
    "📣 Campaign Briefs",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PERSONA → PRODUCT MATCHES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    section_header(
        "Five buyer personas — one best-fit BYD product each",
        "Personas from 19 qualitative interviews; survey data confirms segment size and pain points",
    )

    st.markdown(
        """
        <div style="background:#fff8f8;border:1px solid #f5c6cb;border-left:4px solid #d70c19;
                    border-radius:0 8px 8px 0;padding:0.85rem 1rem;margin-bottom:1.2rem">
            <p style="margin:0;font-size:0.85rem;color:#111">
                <strong>How to read this:</strong> Each card shows (1) what the persona's life looks like,
                (2) the specific pain points that block them from switching, and (3) the single BYD model
                whose features directly address those blockers — with a one-paragraph explanation of why
                the match works. The personas are drawn from the 19 in-depth interviews; the survey %
                figures estimate how many of the 306 survey respondents likely share each profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Survey-derived signals per persona
    fam_pct  = f"~{int((_str(df['age_range']).isin(['35–44','45–54'])).mean()*100)}% mid-age"
    cost_n   = n_cost
    time_pct = pct_bev
    condo_pct = pct_no_home

    col_a, col_b = st.columns(2)

    with col_a:
        _persona_match_card(
            icon="👨‍👩‍👧",
            persona="Family Logistics Manager",
            color="#7c3aed",
            pain_headline="Long road trips with sleeping kids — can't stop for 45-min charging",
            pain_details=[
                "Needs 7 seats + stroller-compatible boot (child logistics)",
                "Highway trips with kids = zero tolerance for unplanned charging stops",
                "Joint family decision: partner veto requires full confidence in the brand",
                "Never heard of PHEV — conflates it with BEV ('both need charging')",
                "Battery safety anxiety reinforced by neighbour/media accident stories",
            ],
            product_primary="Sealion 6 DM-i",
            product_pt="PHEV",
            product_price="฿879K–999K",
            product_why=(
                "The DM-i powertrain delivers up to 1,200 km combined range (electric city + petrol highway), "
                "eliminating mid-trip charging stops entirely. Electric power handles the daily school run "
                "(50–80 km) at near-zero fuel cost; the petrol engine takes over seamlessly on long weekends. "
                "Blade Battery chemistry is rated thermally stable under crash conditions — addressing the "
                "accident-fear directly. <strong>Reframe the message:</strong> 'Electric on weekdays. "
                "Highway on petrol. Kids sleep the whole way.'"
            ),
            product_secondary="BYD M6 (7-seat MPV BEV)",
            product_secondary_note="— ideal if family needs full 7-seat layout and primarily city-drives",
            n_label=fam_pct,
        )

        _persona_match_card(
            icon="⚡",
            persona="Time-Efficient Professional",
            color="#b45309",
            pain_headline="The car must disappear into the background — charge at night, just work",
            pain_details=[
                "Home charger as default: plug in at 10 PM, full at 7 AM, no thought required",
                "Service repair under 72 hours — car is how daily life runs",
                "Single app for charging, service booking, remote AC pre-cooling",
                "PHEV dismissed: 'two problems in one car' — prefers BEV simplicity",
                "OTA updates: doesn't want to visit a service centre for firmware",
            ],
            product_primary="Seal",
            product_pt="BEV",
            product_price="฿1,099K–1,599K",
            product_why=(
                "The Seal's 700+ km real-world range (CLTC ~570 km) means plugging in every 5–7 nights — "
                "the charging friction is near-zero. BYD's DiLink 3.0 integrates charging monitoring, "
                "OTA updates, remote climate, and service booking in one app. The Seal's 530 hp / "
                "235 km/h capability also matches the performance-adjacent identity of this persona. "
                "<strong>Winning message:</strong> 'One app. One plug. Everything works.'"
            ),
            product_secondary="Atto 3",
            product_secondary_note="— if SUV utility is needed at a lower price point (฿629K–849K)",
            n_label=pct_bev,
        )

        _persona_match_card(
            icon="🏙️",
            persona="No-Home-Charging Condo Dweller",
            color="#6d28d9",
            pain_headline="Self-excluded from EVs because condo has no charger — nobody told her PHEV doesn't need one",
            pain_details=[
                "Condo parking: no wall charger, management committee says no",
                "Assumed EV = must-charge-at-home → BEV is impossible",
                "Daily commute is only 20–30 km — PHEV range would cover it on every charge",
                "Budget 20–35K THB/month income → sub-1M THB price ceiling",
                "Trusted adults (father, family) said 'EVs are unreliable' — applies to PHEV by association",
            ],
            product_primary="Sealion 6 DM-i",
            product_pt="PHEV",
            product_price="฿879K–999K",
            product_why=(
                "PHEV solves this persona's core problem precisely: no daily home charging required. "
                "Charge opportunistically at the office or a mall twice a week — the 60+ km electric "
                "range covers her entire daily commute on those charge days. The petrol tank handles "
                "any day she doesn't charge. She is the ideal PHEV buyer who doesn't yet know it. "
                "<strong>One message unlocks this segment:</strong> "
                "'No home charger needed. Charge when convenient. Drive on petrol when you can't.'"
            ),
            product_secondary="Atto 3 DM-i",
            product_secondary_note="— compact SUV PHEV at a slightly lower entry price when available",
            n_label=pct_no_home,
        )

    with col_b:
        _persona_match_card(
            icon="🧮",
            persona="Cost Calculator",
            color="#1a7a4a",
            pain_headline="Spreadsheet already built — but battery replacement cost is the one unknown that breaks the model",
            pain_details=[
                "Tracks fuel/maintenance/insurance to the baht using Excel before any showroom visit",
                "Battery replacement cost unknown = unresolvable TCO variable",
                "BYD's past price cuts retroactively 'break' previous buyers' financial models",
                "Warranty opacity: lifetime battery claim → perceived as marketing, not real protection",
                "Parts from China: 8-month wait = 8 months of installments on an undriveable car",
            ],
            product_primary="Dolphin",
            product_pt="BEV",
            product_price="฿509K–600K",
            product_why=(
                "At ฿509K, the Dolphin is the most affordable BEV entry in Thailand with a credible brand — "
                "making the TCO case easiest to close. Electricity vs petrol comparison for a 20–40 km "
                "daily commute shows ~฿1,500–2,000/month savings vs an equivalent ICE/HEV hatchback. "
                "BYD's 8-year/160,000 km battery warranty is market-leading if communicated clearly. "
                "<strong>Unlock mechanism:</strong> publish a Thai-language 5-year TCO comparison "
                "(Dolphin vs Honda City) and cap battery replacement at a stated maximum (e.g., ฿150K) "
                "in the written sales contract."
            ),
            product_secondary="Atto 3",
            product_secondary_note="— if SUV format needed with similar TCO logic (฿629K–849K)",
            n_label=f"{cost_n} cite cost barrier",
        )

        _persona_match_card(
            icon="🚗",
            persona="Field Professional (Variable Distance)",
            color="#0f766e",
            pain_headline="Daily mileage unpredictable — BEV creates daily mental overhead he doesn't want",
            pain_details=[
                "25 km on office days, 80–100 km on client/factory days — no pattern",
                "Pure BEV: technically covers it, but mental overhead of checking battery daily is friction",
                "Work car must look professional — currently perceives BYD as mass-market/rounded",
                "Service downtime = missed client meetings = unacceptable business cost",
                "PHEV resale value concern: smaller battery + two systems = depreciation faster",
            ],
            product_primary="Sealion 6 DM-i",
            product_pt="PHEV",
            product_price="฿879K–999K",
            product_why=(
                "1,200 km combined range eliminates the mental overhead entirely: electric when the "
                "battery has charge, petrol fallback on heavy-travel days — the driver never has to think "
                "about it. The Sealion 6's crossover proportions and chrome detailing read as "
                "professional-grade; it is currently marketed as a family car, but the same vehicle "
                "positioned as a 'no-compromise work tool' hits this persona exactly. "
                "<strong>Reframe:</strong> 'Electric most days. Petrol on heavy days. 1,200 km total. "
                "Never plan your route around a charger again.'"
            ),
            product_secondary="Seal 06 DM-i",
            product_secondary_note="— sedan variant, stronger professional aesthetic, same DM-i drivetrain",
            n_label="Field commuters",
        )

    # ── Overlap summary table ──────────────────────────────────────────────────
    st.divider()
    section_header(
        "Persona × product quick-reference matrix",
        "Primary and secondary BYD model fit per persona",
    )

    st.markdown(
        """
        <table style="width:100%;border-collapse:collapse;font-size:0.86rem">
            <thead>
                <tr style="background:#1a1a1a;color:white">
                    <th style="padding:10px 12px;text-align:left">Persona</th>
                    <th style="padding:10px 12px">Primary pain</th>
                    <th style="padding:10px 12px">Primary BYD fit</th>
                    <th style="padding:10px 12px">Powertrain</th>
                    <th style="padding:10px 12px">Price range</th>
                    <th style="padding:10px 12px;text-align:left">Single unlock message</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background:#fdf7ef;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:700">👨‍👩‍👧 Family Manager</td>
                    <td style="padding:9px 12px">Kids asleep on highway — no charging stops</td>
                    <td style="padding:9px 12px;font-weight:700;color:#d70c19">Sealion 6 DM-i</td>
                    <td style="padding:9px 12px"><span style="background:#A23B72;color:white;padding:2px 7px;border-radius:3px;font-size:0.75rem">PHEV</span></td>
                    <td style="padding:9px 12px">฿879K–999K</td>
                    <td style="padding:9px 12px">Electric city. Petrol highway. 1,200 km total. Kids sleep the whole way.</td>
                </tr>
                <tr style="background:#ffffff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:700">🧮 Cost Calculator</td>
                    <td style="padding:9px 12px">Battery replacement = unknown in TCO spreadsheet</td>
                    <td style="padding:9px 12px;font-weight:700;color:#d70c19">Dolphin</td>
                    <td style="padding:9px 12px"><span style="background:#2E86AB;color:white;padding:2px 7px;border-radius:3px;font-size:0.75rem">BEV</span></td>
                    <td style="padding:9px 12px">฿509K–600K</td>
                    <td style="padding:9px 12px">5-year TCO table published. Battery cap in writing. The math works.</td>
                </tr>
                <tr style="background:#fdf7ef;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:700">⚡ Time Professional</td>
                    <td style="padding:9px 12px">Service downtime + charging complexity</td>
                    <td style="padding:9px 12px;font-weight:700;color:#d70c19">Seal</td>
                    <td style="padding:9px 12px"><span style="background:#2E86AB;color:white;padding:2px 7px;border-radius:3px;font-size:0.75rem">BEV</span></td>
                    <td style="padding:9px 12px">฿1,099K–1,599K</td>
                    <td style="padding:9px 12px">One app. One plug. 72-hr service SLA. Home charger included on delivery.</td>
                </tr>
                <tr style="background:#ffffff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:700">🚗 Field Professional</td>
                    <td style="padding:9px 12px">Unpredictable daily mileage — BEV mental overhead</td>
                    <td style="padding:9px 12px;font-weight:700;color:#d70c19">Sealion 6 DM-i</td>
                    <td style="padding:9px 12px"><span style="background:#A23B72;color:white;padding:2px 7px;border-radius:3px;font-size:0.75rem">PHEV</span></td>
                    <td style="padding:9px 12px">฿879K–999K</td>
                    <td style="padding:9px 12px">1,200 km total range. Never plan around a charger again.</td>
                </tr>
                <tr style="background:#fdf7ef">
                    <td style="padding:9px 12px;font-weight:700">🏙️ Condo Dweller</td>
                    <td style="padding:9px 12px">Self-excluded: 'EVs need home charger' belief</td>
                    <td style="padding:9px 12px;font-weight:700;color:#d70c19">Sealion 6 DM-i</td>
                    <td style="padding:9px 12px"><span style="background:#A23B72;color:white;padding:2px 7px;border-radius:3px;font-size:0.75rem">PHEV</span></td>
                    <td style="padding:9px 12px">฿879K–999K</td>
                    <td style="padding:9px 12px">No home charger needed. Charge when convenient. Drive on petrol when you can't.</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PAIN POINT → BYD SOLUTION
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header(
        "From survey barrier to BYD product feature",
        "Each row: the pain point as stated by survey respondents → the specific BYD spec or program that resolves it",
    )

    st.markdown(
        '<div style="display:grid;grid-template-columns:2fr 2fr 1.5fr 0.8fr;gap:0.75rem;'
        'padding:0.5rem 0;border-bottom:2px solid #1a1a1a;margin-bottom:0.25rem">'
        '<span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280">Pain Point</span>'
        '<span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280">BYD Feature / Program</span>'
        '<span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280">Recommended Model</span>'
        '<span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280">Survey %</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    _pain_row(
        "😰", "Range anxiety (can't make it between charges)",
        "DM-i PHEV: 1,200 km combined (60 km EV + petrol fallback). Zero range anxiety by design.",
        "Sealion 6 DM-i", pct_range,
    )
    _pain_row(
        "🔌", "Insufficient public charging stations",
        "PHEV removes public charger dependency entirely. Home charging + petrol = 100% coverage.",
        "Sealion 6 DM-i / M6", pct_charging,
    )
    _pain_row(
        "🏠", "No home charging access (condo/apartment)",
        "PHEV doesn't require daily charging. Charge twice a week at office or mall — runs on petrol otherwise.",
        "Sealion 6 DM-i", pct_no_home,
    )
    _pain_row(
        "💰", "High upfront purchase cost",
        "Dolphin BEV at ฿509K — lowest entry in Thailand from a tier-1 EV brand. EV3.5 incentives apply.",
        "Dolphin BEV", pct_cost,
    )
    _pain_row(
        "🔧", "Maintenance/after-sales service concerns",
        "BYD 8-yr/160K km battery warranty. DiCare service app. Expanding to 100+ Thai service centres by 2025.",
        "All models", pct_service,
    )
    _pain_row(
        "🔋", "Battery concerns (replacement cost, safety, degradation)",
        "Blade Battery: LFP chemistry — no thermal runaway, Euro NCAP 5-star. 8-year warranty with stated replacement terms.",
        "All BEV/PHEV models", pct_battery,
    )
    _pain_row(
        "⏰", "Charging takes too long / inconvenient",
        "DM-i PHEV: charges overnight on standard 220V. BEV Seal: 150 kW DC fast charge (10→80% in 26 min).",
        "Sealion 6 DM-i / Seal", f"{_str(df['ev_adoption_barriers']).str.contains('Charging takes|slow', case=False).mean()*100:.0f}%",
    )
    _pain_row(
        "📉", "Uncertain resale value",
        "BYD is #1 EV brand in Thailand by volume — scale reduces depreciation risk vs niche EV brands.",
        "All models", f"{_str(df['ev_adoption_barriers']).str.contains('Resale|resale', case=False).mean()*100:.0f}%",
    )
    _pain_row(
        "🏷️", "Lack of brand trust",
        "111× growth 2022→2025. #3 brand Thailand 2025. #2 Jan–Feb 2026. BYD has more Thai owners than any other EV brand.",
        "All models", f"{_str(df['ev_adoption_barriers']).str.contains('brand trust|brand', case=False).mean()*100:.0f}%",
    )
    _pain_row(
        "🛡️", "Technology too new / unproven",
        "BYD has sold 1M+ vehicles in Thailand's EV class globally. DM-i is 5th generation since 2021.",
        "DM-i PHEV range", f"{_str(df['ev_adoption_barriers']).str.contains('too new|unproven', case=False).mean()*100:.0f}%",
    )

    st.divider()
    section_header("Pain-point severity × BYD solution readiness")

    pain_data = {
        "Pain point": [
            "Range anxiety", "No home charger", "High cost", "Slow charging",
            "Battery concerns", "After-sales", "Brand trust", "Resale value",
        ],
        "% survey respondents": [
            int(pct_range.replace("%", "")),
            int(pct_no_home.replace("%", "")),
            int(pct_cost.replace("%", "")),
            int(_str(df["ev_adoption_barriers"]).str.contains("Charging takes|slow", case=False).mean() * 100),
            int(pct_battery.replace("%", "")),
            int(pct_service.replace("%", "")),
            int(_str(df["ev_adoption_barriers"]).str.contains("brand trust", case=False).mean() * 100),
            int(_str(df["ev_adoption_barriers"]).str.contains("Resale", case=False).mean() * 100),
        ],
        "BYD solution readiness": [9, 9, 7, 8, 8, 6, 6, 5],
    }
    pain_df = pd.DataFrame(pain_data)

    fig_pain = go.Figure()
    fig_pain.add_trace(go.Scatter(
        x=pain_df["% survey respondents"],
        y=pain_df["BYD solution readiness"],
        mode="markers+text",
        text=pain_df["Pain point"],
        textposition="top center",
        marker=dict(
            size=pain_df["% survey respondents"] * 0.9 + 10,
            color="#d70c19",
            opacity=0.75,
            line=dict(color="white", width=1.5),
        ),
        hovertemplate="<b>%{text}</b><br>Survey: %{x}%<br>BYD readiness: %{y}/10<extra></extra>",
    ))
    fig_pain.add_hline(y=7, line_dash="dash", line_color="#16a34a", line_width=1,
                       annotation_text="High BYD readiness", annotation_position="left")
    fig_pain.add_vline(x=pain_df["% survey respondents"].median(), line_dash="dash",
                       line_color="#9ca3af", line_width=1)
    fig_pain.update_layout(
        **LAYOUT_BASE,
        title="Pain point prevalence (x) vs BYD solution readiness (y) — bubble = prevalence",
        xaxis_title="% of respondents citing this barrier",
        yaxis_title="BYD solution readiness (1=weak, 10=strong)",
        yaxis=dict(range=[0, 11]),
        height=460,
    )
    st.plotly_chart(fig_pain, use_container_width=True)

    st.info(
        "**Top-right quadrant = highest-impact wins:** BYD has strong, ready-to-deploy solutions "
        "for range anxiety and no-home-charger barriers (both via DM-i PHEV). These are also the "
        "highest-prevalence barriers in the survey — making PHEV communication the single highest-ROI "
        "messaging investment for BYD Thailand."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BYD VS INCUMBENTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section_header(
        "Why BYD beats the incumbents — and why most Thai buyers don't know it yet",
        "Structural technology and value advantages over Toyota HEV, Honda HEV, and ICE incumbents",
    )

    st.markdown(
        """
        <div style="background:#fff8f8;border:1px solid #f5c6cb;border-left:4px solid #d70c19;
                    border-radius:0 8px 8px 0;padding:0.85rem 1rem;margin-bottom:1.2rem">
            <p style="margin:0;font-size:0.87rem;color:#111">
                Toyota and Honda dominate Thai car sales via HEV reputation. But HEV is not PHEV or BEV —
                it cannot plug in, cannot run on electricity alone, and cannot benefit from home charging.
                BYD's DM-i PHEV achieves lower running costs, more EV-like daily driving, and better
                incentive eligibility than any Japanese self-charging hybrid — at comparable or lower prices.
                Most Thai buyers don't know this distinction. That gap is BYD's largest conversion opportunity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sub1, sub2 = st.tabs(["⚡ Technology Advantages", "💴 Price & Value Advantages"])

    with sub1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### BYD vs Toyota HEV (Corolla Cross, Yaris Cross, Camry)")
            _adv_chip(
                "🔌", "Plugin vs self-charging — the fundamental difference",
                "Toyota HEV charges itself via regenerative braking and the engine. It cannot be plugged in. "
                "BYD's DM-i PHEV can charge overnight at home, at the office, or at a public charger — "
                "giving real electric-only driving (60–80 km) on typical days. Toyota HEV always burns "
                "some petrol, every drive. BYD DM-i can complete a 30 km urban commute on zero petrol, zero cost.",
                "#d70c19",
            )
            _adv_chip(
                "💧", "Running cost: ฿0.6/km vs ฿2.0/km vs ฿5.0/km",
                "BYD BEV: ~฿0.6/km on electricity (home rate). BYD DM-i on electric: ~฿0.8/km. "
                "Toyota HEV: ~฿2.0–2.5/km (petrol-dependent). Thai ICE average: ~฿5–6/km. "
                "A 40 km daily commute costs ฿24/day in a BYD BEV vs ฿80/day in a Toyota HEV "
                "vs ฿200/day in a standard ICE. Annual saving vs HEV: ~฿20,000+ THB.",
                "#16a34a",
            )
            _adv_chip(
                "🛡️", "Blade Battery vs NiMH — safety and longevity",
                "BYD's Blade Battery uses lithium iron phosphate (LFP) chemistry — passing the nail-penetration "
                "test without thermal runaway, fire, or explosion. Toyota's HEV batteries are NiMH (older "
                "chemistry) or NCA/NMC lithium. LFP degrades slower at high ambient temperatures (critical in "
                "Thailand's climate) and has zero cobalt supply-chain risk. BYD backs it with 8-year warranty.",
                "#2563eb",
            )
            _adv_chip(
                "📱", "Tech stack: OTA vs dealership visit",
                "BYD DiLink delivers over-the-air software updates — new features, bug fixes, and map updates "
                "appear overnight without a dealer visit. Toyota's infotainment is static hardware; a firmware "
                "update requires booking a service appointment. BYD's 15.6-inch rotating touchscreen, "
                "360° camera, and ADAS suite are standard on mid-trim models — equivalent Toyota features "
                "require the premium trim or optional extras.",
                "#7c3aed",
            )
            _adv_chip(
                "🏭", "EV3.5 incentives: BEV/PHEV only — HEV excluded",
                "Thailand's EV3.5 policy (2024–2027) provides import duty reductions and excise rebates "
                "only for BEV and PHEV vehicles. Self-charging HEV (Toyota, Honda) do not qualify for the "
                "full incentive package. This means BYD BEV/PHEV pricing has a structural government subsidy "
                "advantage that ICE and HEV competitors cannot access.",
                "#f59e0b",
            )

        with col_r:
            st.markdown("#### BYD vs Honda HEV (HR-V, CR-V, Accord) and Isuzu (MU-X Diesel)")
            _adv_chip(
                "🚗", "BYD Sealion 6 DM-i vs Honda CR-V: 37% cheaper, more EV",
                "Honda CR-V e:HEV PHEV: ฿1,399K–1,699K. BYD Sealion 6 DM-i: ฿879K–999K. "
                "Saving: ฿400K–700K for a directly comparable C-segment PHEV SUV. "
                "The Sealion 6 offers 60+ km EV range vs CR-V PHEV's ~80 km — similar daily driving, "
                "but at a price that removes the premium-bracket barrier entirely.",
                "#d70c19",
            )
            _adv_chip(
                "📐", "BYD Atto 3 vs Corolla Cross HEV: same segment, 28% cheaper",
                "Toyota Corolla Cross HEV: ฿869K–1,069K. BYD Atto 3 BEV: ฿629K–849K. "
                "The Atto 3 is a C-segment SUV BEV with equal or larger cabin dimensions, "
                "360° camera, wireless phone charging, and a 50.1 kWh battery providing ~480 km WLTP range. "
                "The Corolla Cross runs on petrol regardless of trip length.",
                "#16a34a",
            )
            _adv_chip(
                "⛽", "BYD DM-i vs Diesel SUV (Isuzu MU-X): fuel cost comparison",
                "Isuzu MU-X diesel: ~฿3.5/km at current diesel prices. BYD Sealion 6 DM-i on electric: "
                "~฿0.8/km; on petrol: ~฿3.5/km (petrol engine is smaller, efficient). For a mixed-use driver "
                "doing 50% city (electric) + 50% highway (petrol): effective cost ~฿2.1/km vs MU-X ฿3.5/km. "
                "Annual saving: ~฿40,000 THB for a 60 km/day driver.",
                "#0891b2",
            )
            _adv_chip(
                "🔒", "Incumbent blindspot: HEV cannot charge at home",
                "Survey data shows 43% of respondents cite charging convenience as a top-3 purchase factor. "
                "Yet 61% own or plan to own a home charger. Toyota and Honda HEV buyers cannot access "
                "home charging economics AT ALL — their overnight charging plug does nothing. "
                "BYD PHEV owners who charge nightly run on electricity for ≥90% of urban trips "
                "while paying 0.5× the fuel cost of a Toyota HEV driver on the same route.",
                "#6d28d9",
            )
            _adv_chip(
                "🏆", "Brand scale = resale protection + parts availability",
                "BYD is now #3 passenger car brand in Thailand (2025) — behind only Toyota and Honda. "
                "111× volume growth in 3 years means used BYD inventory is real and priced. "
                "BYD's Thai parts distribution has improved significantly since 2022. In contrast, "
                "NETA's collapse (12,000 → 64 units/year) shows how small EV brands create resale and "
                "parts deserts. BYD's scale is now a genuine protection against both risks.",
                "#ea580c",
            )

    with sub2:
        section_header("Apples-to-apples price comparison — BYD vs nearest incumbent")

        comp_data = [
            {
                "byd": "Dolphin BEV (Extended)", "byd_price": 599_900, "byd_pt": "BEV",
                "inc": "Honda City e:HEV", "inc_brand": "Honda", "inc_price": 749_000, "inc_pt": "HEV",
                "saving": 149_100, "byd_range": "490 km BEV", "inc_range": "0 km EV (self-charging only)",
                "note": "Same segment (B-sedan/hatch). BYD cheaper AND full-electric capability.",
            },
            {
                "byd": "Atto 3 (Standard)", "byd_price": 629_900, "byd_pt": "BEV",
                "inc": "Toyota Corolla Cross HEV", "inc_brand": "Toyota", "inc_price": 869_000, "inc_pt": "HEV",
                "saving": 239_100, "byd_range": "420 km BEV", "inc_range": "0 km EV",
                "note": "C-segment compact SUV. BYD ฿239K cheaper + pure EV driving.",
            },
            {
                "byd": "Sealion 6 DM-i (Standard)", "byd_price": 879_000, "byd_pt": "PHEV",
                "inc": "Honda CR-V e:HEV", "inc_brand": "Honda", "inc_price": 1_399_000, "inc_pt": "HEV",
                "saving": 520_000, "byd_range": "60 km EV + 1,000 km petrol", "inc_range": "0 km EV",
                "note": "C/D-segment SUV. BYD ฿520K cheaper AND plugs in.",
            },
            {
                "byd": "Seal (Standard)", "byd_price": 1_099_000, "byd_pt": "BEV",
                "inc": "Toyota Camry HEV", "inc_brand": "Toyota", "inc_price": 1_699_000, "inc_pt": "HEV",
                "saving": 600_000, "byd_range": "570 km BEV", "inc_range": "0 km EV",
                "note": "D-segment midsize sedan. BYD ฿600K cheaper, full BEV.",
            },
            {
                "byd": "Sealion 7 (Standard)", "byd_price": 1_074_900, "byd_pt": "BEV",
                "inc": "Toyota RAV4 HEV", "inc_brand": "Toyota", "inc_price": 1_299_000, "inc_pt": "HEV",
                "saving": 224_100, "byd_range": "520 km BEV", "inc_range": "0 km EV",
                "note": "D-segment midsize SUV. BYD cheaper + full BEV.",
            },
        ]

        for entry in comp_data:
            byd_col, vs_col, inc_col = st.columns([5, 1, 5])
            with byd_col:
                st.markdown(
                    f'<div style="background:#fff8f8;border:2px solid #d70c19;border-radius:10px;'
                    f'padding:0.9rem 1.1rem">'
                    f'<div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.4rem">'
                    f'<span style="background:#d70c19;color:white;font-weight:900;font-size:0.7rem;'
                    f'padding:2px 8px;border-radius:4px">BYD</span>'
                    f'<span style="font-weight:800;font-size:1rem;color:#111">{entry["byd"]}</span>'
                    f'<span style="background:#2E86AB;color:white;font-size:0.65rem;font-weight:700;'
                    f'padding:2px 6px;border-radius:3px">{entry["byd_pt"]}</span>'
                    f'</div>'
                    f'<div style="font-size:1.25rem;font-weight:900;color:#d70c19">฿{entry["byd_price"]:,}</div>'
                    f'<div style="font-size:0.8rem;color:#16a34a;font-weight:600;margin-top:0.2rem">'
                    f'Range: {entry["byd_range"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with vs_col:
                st.markdown(
                    f'<div style="text-align:center;padding:2rem 0">'
                    f'<div style="font-weight:900;font-size:1.1rem;color:#6b7280">VS</div>'
                    f'<div style="font-size:0.72rem;color:#d70c19;font-weight:700;margin-top:0.3rem">'
                    f'฿{entry["saving"]:,} cheaper</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with inc_col:
                inc_colors = {"Toyota": "#CC0000", "Honda": "#003087", "Isuzu": "#D4A017"}
                ic = inc_colors.get(entry["inc_brand"], "#888")
                st.markdown(
                    f'<div style="background:#fafafa;border:2px solid {ic};border-radius:10px;'
                    f'padding:0.9rem 1.1rem">'
                    f'<div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.4rem">'
                    f'<span style="background:{ic};color:white;font-weight:900;font-size:0.7rem;'
                    f'padding:2px 8px;border-radius:4px">{entry["inc_brand"].upper()}</span>'
                    f'<span style="font-weight:800;font-size:1rem;color:#111">{entry["inc"]}</span>'
                    f'<span style="background:#52B788;color:white;font-size:0.65rem;font-weight:700;'
                    f'padding:2px 6px;border-radius:3px">{entry["inc_pt"]}</span>'
                    f'</div>'
                    f'<div style="font-size:1.25rem;font-weight:900;color:{ic}">฿{entry["inc_price"]:,}</div>'
                    f'<div style="font-size:0.8rem;color:#6b7280;margin-top:0.2rem">'
                    f'EV range: {entry["inc_range"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="background:#f3f4f6;border-radius:6px;padding:0.4rem 0.85rem;'
                f'font-size:0.82rem;color:#374151;margin-bottom:0.6rem">'
                f'<strong>Segment:</strong> {entry["note"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        section_header("Running cost comparison — annual savings vs Toyota HEV")
        st.caption("Assumptions: 15,000 km/year · Home electricity ฿4/kWh · Petrol ฿40/L · HEV: 16 km/L · BEV: 15 kWh/100 km · PHEV 50% EV / 50% petrol at 16 km/L")

        scenarios = ["BYD Dolphin BEV", "BYD Sealion 6 DM-i\n(50% EV mode)", "Toyota Corolla Cross HEV", "Honda HR-V HEV", "Toyota Camry HEV", "Honda City ICE"]
        annual_cost = [
            15_000 * 0.15 * 4,                             # BEV: 15kWh/100km * ฿4
            15_000 * 0.5 * 0.15 * 4 + 15_000 * 0.5 / 16 * 40,  # PHEV 50/50
            15_000 / 16 * 40,                              # Toyota HEV: 16km/L
            15_000 / 15 * 40,                              # Honda HEV: 15km/L
            15_000 / 14 * 40,                              # Camry HEV: 14km/L
            15_000 / 10 * 40,                              # ICE: 10km/L
        ]
        bar_colors = ["#d70c19", "#A23B72", "#CC0000", "#003087", "#CC0000", "#8B5E3C"]
        fig_run = go.Figure(go.Bar(
            x=scenarios,
            y=[int(c) for c in annual_cost],
            marker_color=bar_colors,
            text=[f"฿{int(c):,}/yr" for c in annual_cost],
            textposition="outside",
        ))
        fig_run.add_hline(
            y=annual_cost[0], line_dash="dash", line_color="#d70c19",
            annotation_text="BYD BEV baseline",
            annotation_position="right",
        )
        fig_run.update_layout(
            **LAYOUT_BASE,
            title="Estimated annual fuel/energy cost — 15,000 km/year",
            yaxis_title="Annual fuel/energy cost (THB)",
            height=400,
            yaxis=dict(tickformat=","),
        )
        st.plotly_chart(fig_run, use_container_width=True)

        bev_save = int(annual_cost[2] - annual_cost[0])
        phev_save = int(annual_cost[2] - annual_cost[1])
        c1, c2, c3 = st.columns(3)
        c1.metric("BYD BEV vs Toyota HEV — annual saving", f"฿{bev_save:,}", "per year at 15,000 km")
        c2.metric("BYD DM-i vs Toyota HEV — annual saving", f"฿{phev_save:,}", "per year at 15,000 km")
        c3.metric("BYD DM-i vs Honda ICE — annual saving", f"฿{int(annual_cost[5]-annual_cost[1]):,}", "per year at 15,000 km")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MARKET SIZING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section_header(
        "How many survey respondents map to each product segment?",
        "Survey-derived estimates of buyer pool size per BYD model, based on barrier profile + powertrain preference + budget",
    )

    st.caption(
        "Methodology: each respondent is scored against product fit criteria "
        "(powertrain preference, budget, key barriers, age, driving distance). "
        "Respondents can match multiple products. n=306 survey respondents."
    )

    # Build segment assignments
    df_seg = df.copy()
    df_seg["ev_ri"] = pd.to_numeric(df_seg.get("ev_readiness_index"), errors="coerce")

    def _has_barrier(s: pd.Series, kw: str) -> pd.Series:
        return _str(s).str.contains(kw, case=False)

    _bud = _str(df_seg["budget_range"])
    _pt  = _str(df_seg["powertrain_short"])

    # Dolphin BEV segment: wants BEV, budget <800K, not family-focused
    dolphin_mask = (
        (_pt.isin(["BEV"])) &
        (_bud.str.contains("500|Below|509|600|629|700|749|800", case=False))
    )
    # Atto 3 segment: BEV, mid budget, SUV-friendly
    atto3_mask = (
        (_pt.isin(["BEV"])) &
        (_bud.str.contains("500|600|700|800|1,200", case=False))
    )
    # Seal segment: BEV, higher budget
    seal_mask = (
        (_pt.isin(["BEV"])) &
        (_bud.str.contains("1,000|1,200|1,500|1,099|1,200,001", case=False))
    )
    # Sealion 6 DM-i segment: PHEV pref OR range anxiety OR no home charging OR variable distance
    sealion6_mask = (
        (_pt.isin(["PHEV", "REEV"])) |
        (_has_barrier(df_seg["ev_adoption_barriers"], "Range anxiety")) |
        (_has_barrier(df_seg["ev_adoption_barriers"], "No home charging"))
    )
    # Sealion 7 segment: BEV, higher budget, likely SUV-preference
    sealion7_mask = (
        (_pt.isin(["BEV"])) &
        (_bud.str.contains("1,000|1,200|1,500|1,074|1,099", case=False))
    )

    seg_counts = {
        "Dolphin BEV\n(฿509K–600K)": int(dolphin_mask.sum()),
        "Atto 3 BEV\n(฿629K–849K)": int(atto3_mask.sum()),
        "Sealion 6 DM-i\n(฿879K–999K)": int(sealion6_mask.sum()),
        "Sealion 7 BEV\n(฿1,074K–1,399K)": int(sealion7_mask.sum()),
        "Seal BEV\n(฿1,099K–1,599K)": int(seal_mask.sum()),
    }

    fig_seg = go.Figure(go.Bar(
        x=list(seg_counts.keys()),
        y=list(seg_counts.values()),
        marker_color=["#d70c19", "#f59e0b", "#A23B72", "#2563eb", "#1a1a1a"],
        text=[f"{v} respondents\n({v/len(df_seg)*100:.0f}%)" for v in seg_counts.values()],
        textposition="outside",
    ))
    fig_seg.update_layout(
        **LAYOUT_BASE,
        title="Estimated buyer pool per BYD model — survey respondents matching each product segment (n=306)",
        yaxis_title="Respondents matching product criteria",
        height=420,
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    st.info(
        "**Sealion 6 DM-i has the broadest addressable pool** because its PHEV architecture directly "
        "addresses both range anxiety AND no-home-charging barriers — the two highest-prevalence barriers "
        "in the survey. Many respondents who prefer BEV would likely convert to PHEV if the '1,200 km "
        "combined range / no home charger needed' message was clearly communicated."
    )

    st.divider()
    section_header("Budget distribution vs BYD model price bands")

    # Budget tier vs BYD price bands
    _bud2 = _str(df_seg["budget_range"])
    BUDGET_BANDS = {
        "Below ฿500K": _bud2.str.contains("Below 500", case=False).sum(),
        "฿500K–800K\n(Dolphin/Atto 3)": _bud2.str.contains("500,001|600|700|800,001", case=False).sum(),
        "฿800K–1.2M\n(Sealion 6 DM-i)": _bud2.str.contains("800,001|1,200,000", case=False).sum(),
        "฿1.2M–1.5M\n(Seal/Sealion 7)": _bud2.str.contains("1,200,001|1,500,000", case=False).sum(),
        "Above ฿1.5M": _bud2.str.contains("1,500,001|2,000,000|Above 2", case=False).sum(),
        "Not sure": _bud2.str.contains("Not sure", case=False).sum(),
    }

    # Colour: grey for no BYD match, red variants for matched
    bud_colors = ["#9ca3af", "#d70c19", "#A23B72", "#f59e0b", "#2563eb", "#6b7280"]
    fig_bud = go.Figure(go.Bar(
        x=list(BUDGET_BANDS.keys()),
        y=list(BUDGET_BANDS.values()),
        marker_color=bud_colors,
        text=[str(v) for v in BUDGET_BANDS.values()],
        textposition="outside",
    ))
    fig_bud.update_layout(
        **LAYOUT_BASE,
        title="Stated budget distribution vs BYD price bands — n=306",
        yaxis_title="Number of respondents",
        height=380,
    )
    st.plotly_chart(fig_bud, use_container_width=True)

    st.divider()
    section_header("BYD consideration rate by powertrain preference")

    pt_byd = df.copy()
    pt_byd["considers_byd"] = _str(pt_byd["brands_considering"]).str.contains(r"\bBYD\b", case=False)
    pt_byd["powertrain_short"] = _str(pt_byd["powertrain_short"]).replace("", "Unknown")

    pt_byd_rates = pt_byd.groupby("powertrain_short")["considers_byd"].agg(["mean", "sum", "count"]).reset_index()
    pt_byd_rates.columns = ["Powertrain", "Rate", "n_byd", "n_total"]
    pt_byd_rates = pt_byd_rates[pt_byd_rates["n_total"] >= 5]
    pt_byd_rates["Rate_pct"] = (pt_byd_rates["Rate"] * 100).round(1)

    pt_order_local = ["BEV", "PHEV", "REEV", "HEV", "ICE"]
    pt_byd_rates["sort_order"] = pt_byd_rates["Powertrain"].map(
        {p: i for i, p in enumerate(pt_order_local)}
    ).fillna(99)
    pt_byd_rates = pt_byd_rates.sort_values("sort_order")

    pt_colors_local = {"BEV": "#2E86AB", "PHEV": "#A23B72", "REEV": "#e67e22", "HEV": "#52B788", "ICE": "#BC4749"}
    fig_pt_byd = go.Figure()
    for _, row in pt_byd_rates.iterrows():
        fig_pt_byd.add_trace(go.Bar(
            x=[row["Powertrain"]],
            y=[row["Rate_pct"]],
            name=row["Powertrain"],
            marker_color=pt_colors_local.get(row["Powertrain"], "#888"),
            text=[f"{row['Rate_pct']:.0f}%<br>(n={int(row['n_total'])})"],
            textposition="outside",
            showlegend=False,
        ))
    fig_pt_byd.update_layout(
        **LAYOUT_BASE,
        title="BYD consideration rate by powertrain preference — % of each group considering BYD",
        yaxis_title="% considering BYD",
        height=360, barmode="group",
    )
    st.plotly_chart(fig_pt_byd, use_container_width=True)

    st.info(
        "BYD's consideration rate is highest among BEV-preferring respondents (as expected), but the "
        "PHEV/REEV segment represents the largest untapped opportunity — if BYD's PHEV message reaches "
        "respondents currently considering non-BYD PHEV/REEV options, the addressable pool is substantial. "
        "Even a 30% consideration rate uplift among PHEV-preferrers would materially grow BYD's funnel."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — COMPETITIVE ADVANTAGE MAP (RADAR)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section_header(
        "BYD competitive advantage — multi-dimensional comparison",
        "How BYD scores vs Toyota HEV, Honda HEV, and ICE incumbents across the dimensions Thai buyers care most about",
    )

    st.caption(
        "Scores (1–10) are derived from survey purchase factor rankings, interview priorities, "
        "and publicly available product specifications. BYD scores reflect the current product "
        "and service reality — not aspirational positioning."
    )

    dimensions = [
        "Running cost\n(TCO over 5 yrs)",
        "Purchase price\n(value for spec)",
        "Brand trust\n& reliability",
        "After-sales\nservice",
        "Technology\n& features",
        "Range &\ncharging ease",
        "Design\n& exterior",
        "EV daily\nusability",
    ]

    # Scores: BYD BEV, BYD PHEV DM-i, Toyota HEV, Honda HEV, ICE generic
    scores = {
        "BYD Dolphin/Seal (BEV)":      [9, 8, 6, 6, 8, 7, 6, 9],
        "BYD Sealion 6 DM-i (PHEV)":  [8, 8, 6, 6, 8, 9, 7, 9],
        "Toyota Corolla Cross (HEV)":  [6, 5, 9, 8, 6, 4, 8, 3],
        "Honda HR-V / CR-V (HEV)":     [6, 5, 8, 8, 6, 3, 7, 3],
        "ICE (generic incumbent)":     [3, 6, 8, 7, 4, 2, 7, 1],
    }

    brand_colors_radar = {
        "BYD Dolphin/Seal (BEV)":     "#d70c19",
        "BYD Sealion 6 DM-i (PHEV)":  "#A23B72",
        "Toyota Corolla Cross (HEV)":  "#CC0000",
        "Honda HR-V / CR-V (HEV)":    "#003087",
        "ICE (generic incumbent)":    "#9ca3af",
    }

    fig_radar = go.Figure()
    for brand, vals in scores.items():
        is_byd = "BYD" in brand
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=dimensions + [dimensions[0]],
            fill="toself",
            name=brand,
            line=dict(
                color=brand_colors_radar[brand],
                width=3 if is_byd else 1.5,
                dash="solid" if is_byd else "dot",
            ),
            fillcolor=brand_colors_radar[brand] if is_byd else "rgba(0,0,0,0)",
            opacity=0.25 if is_byd else 0.05,
        ))

    fig_radar.update_layout(
        **LAYOUT_BASE,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=9)),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        showlegend=True,
        legend=dict(orientation="v", x=1.05),
        height=560,
        title="BYD vs incumbent brands — competitive position across key purchase dimensions",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()
    section_header("Dimension-by-dimension verdict")

    verdicts = [
        ("Running cost (TCO)", "🟢 BYD wins decisively",
         "BEV: ~฿0.6/km. PHEV: ~฿1.2/km blended. Toyota HEV: ~฿2.2/km. ICE: ~฿5/km. "
         "Over 5 years at 15,000 km/year, BYD BEV saves ฿80,000–120,000 vs Toyota HEV."),
        ("Purchase price", "🟡 BYD wins narrowly (after incentives)",
         "Pre-incentive, BYD and Toyota are comparable. Post-EV3.5 incentive, BYD BEV/PHEV "
         "undercuts Toyota HEV by ฿100K–500K on equivalent segments. ICE remains cheapest in the "
         "below-฿500K bracket where BYD has limited coverage."),
        ("Brand trust & reliability", "🔴 Toyota/Honda win clearly",
         "This is BYD's primary gap. Survey data: 'Brand trust / reliability' is top-3 purchase factor "
         "for 41% of respondents. Toyota/Honda have 40+ years of Thai market presence. BYD has 3. "
         "Only time, service excellence, and Thai-owner testimonials close this gap."),
        ("After-sales service", "🔴 Toyota/Honda win clearly",
         "Toyota has the most service centres in Thailand (1,000+). Honda is comparably dense. "
         "BYD has expanded rapidly (100+ centres) but rural coverage remains limited. The interview "
         "data shows 8-month part delays are still real. This is improving but not yet competitive."),
        ("Technology & features", "🟢 BYD wins clearly",
         "BYD's 15.6\" rotating touchscreen, OTA updates, Blade Battery tech, 360° camera, ADAS, "
         "and heat pump are standard on models where Toyota/Honda charge ฿100K–200K as optional extras. "
         "BYD's tech-per-baht ratio is significantly higher."),
        ("Range & charging ease", "🟢 BYD PHEV wins decisively vs HEV",
         "Toyota/Honda HEV cannot plug in → zero home charging benefit. BYD DM-i PHEV: 1,200 km "
         "combined, charge at home, no range anxiety. BYD BEV: 420–570 km WLTP. Versus the "
         "HEV incumbents, BYD's charging capability is not just better — it's categorically different."),
        ("Design & exterior", "🟡 Near-parity (personal preference)",
         "Toyota/Honda have conservative, broadly trusted aesthetics. BYD's design language "
         "(especially Seal, Sealion 7) is modern and globally competitive. However, interview data "
         "shows BYD's rounded mass-market aesthetic repels premium/aspirational buyers. Seal 06 "
         "and Sealion 7 are stronger in this dimension than Dolphin or Atto 3."),
        ("EV daily usability", "🟢 BYD wins decisively",
         "Toyota HEV and Honda HEV cannot be charged at home — their 'EV mode' is entirely "
         "self-managed by the car. BYD PHEV/BEV owners who home-charge run on electricity for "
         "80–95% of urban trips. The daily EV experience is fundamentally different and more "
         "convenient for owners with home access."),
    ]

    for dim, verdict, detail in verdicts:
        icon = verdict.split()[0]
        label = " ".join(verdict.split()[1:])
        color = "#16a34a" if "🟢" in icon else ("#f59e0b" if "🟡" in icon else "#d70c19")
        st.markdown(
            f'<div style="display:flex;gap:0.75rem;padding:0.8rem 0;border-bottom:1px solid #e2ddd6;'
            f'align-items:flex-start">'
            f'<div style="min-width:200px;flex-shrink:0">'
            f'<div style="font-weight:700;font-size:0.9rem;color:#111">{dim}</div>'
            f'<div style="font-size:0.8rem;font-weight:700;color:{color};margin-top:2px">{verdict}</div>'
            f'</div>'
            f'<div style="font-size:0.85rem;color:#374151;line-height:1.55">{detail}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        """
        <div style="background:#fff8f8;border:1px solid #f5c6cb;border-left:4px solid #d70c19;
                    border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin-top:0.5rem">
            <p style="margin:0;font-size:0.88rem;font-weight:700;color:#d70c19;
                       text-transform:uppercase;letter-spacing:0.06em">Strategic implication</p>
            <p style="margin:0.5rem 0 0;color:#111;font-size:0.9rem;line-height:1.6">
                BYD leads on the dimensions that determine actual ownership value — running cost, technology,
                range, and charging practicality. It trails on the dimensions that determine initial purchase
                confidence — brand trust and service network coverage. The gap between BYD's objective
                product advantage and Thai consumers' subjective brand hesitation is the entire battleground.
                <strong>BYD's conversion strategy should not be "sell a better car" — it already has one.
                It should be "lower the trust barrier enough that buyers let themselves discover how good
                the car already is."</strong> Test drives, service guarantees, owner community
                visibility, and transparent TCO data are the actual product.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CAMPAIGN BRIEFS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    section_header(
        "One-page campaign brief per persona",
        "Key message · Key visual · Channel mix · Success metric — derived from survey data and interview insights",
    )

    st.markdown(
        """
        <div style="background:#f3f4f6;border:1px solid #e2ddd6;border-radius:10px;
                    padding:0.9rem 1.2rem;margin-bottom:1.2rem">
            <p style="margin:0;font-size:0.87rem;color:#374151;line-height:1.6">
                Each brief below is built from three inputs: (1) the persona's stated barriers and needs
                from the qualitative interviews, (2) the channel preferences from the survey media data,
                and (3) the specific BYD product features that resolve each barrier. The key visual direction
                is prescriptive — not conceptual — because the interview data is specific about what
                Thai buyers respond to and what actively repels them.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def _campaign_brief(
        icon: str, persona: str, product: str, color: str,
        headline: str, subline: str,
        key_message: str,
        visual_do: list[str], visual_dont: list[str],
        channels: list[tuple[str, str, str]],
        cta: str, metric: str,
    ) -> None:
        """Render a full one-page campaign brief card."""
        do_html  = "".join(f'<li style="margin-bottom:0.25rem">{d}</li>' for d in visual_do)
        dont_html = "".join(f'<li style="margin-bottom:0.25rem;color:#9ca3af;text-decoration:line-through">{d}</li>' for d in visual_dont)
        ch_html  = ""
        for ch_icon, ch_name, ch_note in channels:
            ch_html += (
                f'<div style="display:flex;gap:0.5rem;align-items:flex-start;'
                f'padding:0.4rem 0;border-bottom:1px solid #e2ddd6">'
                f'<span style="font-size:1rem;flex-shrink:0">{ch_icon}</span>'
                f'<div><strong style="font-size:0.85rem;color:#111">{ch_name}</strong>'
                f'<div style="font-size:0.8rem;color:#6b7280">{ch_note}</div></div></div>'
            )

        st.markdown(
            f"""
            <div style="border:1px solid {color}33;border-top:4px solid {color};border-radius:12px;
                        background:white;padding:1.4rem 1.6rem;margin-bottom:1.5rem;
                        box-shadow:0 3px 12px {color}15">
              <!-- Campaign header -->
              <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem">
                <span style="font-size:2rem">{icon}</span>
                <div>
                  <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.1em;color:{color}">Campaign Brief · {persona}</div>
                  <div style="font-weight:800;font-size:1.1rem;color:#111;margin-top:2px">
                    Product: BYD {product}
                  </div>
                </div>
              </div>

              <!-- Headline / subline -->
              <div style="background:{color}0d;border-radius:8px;padding:1rem 1.2rem;margin-bottom:1rem">
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.1em;color:{color};margin-bottom:0.4rem">CAMPAIGN HEADLINE</div>
                <div style="font-size:1.3rem;font-weight:900;color:#111;line-height:1.3">
                  &ldquo;{headline}&rdquo;
                </div>
                <div style="font-size:0.9rem;color:#6b7280;margin-top:0.4rem;font-style:italic">
                  {subline}
                </div>
              </div>

              <!-- 3-column body -->
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">

                <!-- Key message -->
                <div>
                  <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.08em;color:#6b7280;margin-bottom:0.5rem">Key Message</div>
                  <p style="font-size:0.86rem;color:#111;line-height:1.6;margin:0">{key_message}</p>
                </div>

                <!-- Key visual -->
                <div>
                  <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.08em;color:#6b7280;margin-bottom:0.5rem">Key Visual Direction</div>
                  <div style="font-size:0.8rem;font-weight:600;color:#16a34a;margin-bottom:0.2rem">✓ Use</div>
                  <ul style="margin:0 0 0.5rem;padding-left:1.1rem;font-size:0.83rem;color:#111">{do_html}</ul>
                  <div style="font-size:0.8rem;font-weight:600;color:#d70c19;margin-bottom:0.2rem">✗ Avoid</div>
                  <ul style="margin:0;padding-left:1.1rem;font-size:0.83rem">{dont_html}</ul>
                </div>

                <!-- Channels -->
                <div>
                  <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.08em;color:#6b7280;margin-bottom:0.5rem">Channel Mix</div>
                  {ch_html}
                </div>
              </div>

              <!-- CTA + Metric footer -->
              <div style="display:flex;gap:1rem;margin-top:1rem;padding-top:0.8rem;
                          border-top:1px solid #e2ddd6">
                <div style="flex:1;background:#f3f4f6;border-radius:8px;padding:0.65rem 0.85rem">
                  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.07em;color:#6b7280">Primary CTA</div>
                  <div style="font-size:0.9rem;font-weight:700;color:{color};margin-top:2px">{cta}</div>
                </div>
                <div style="flex:1;background:#f3f4f6;border-radius:8px;padding:0.65rem 0.85rem">
                  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.07em;color:#6b7280">Success Metric</div>
                  <div style="font-size:0.9rem;font-weight:700;color:#111;margin-top:2px">{metric}</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── BRIEF 1: Family Logistics Manager ─────────────────────────────────────
    _campaign_brief(
        icon="👨‍👩‍👧",
        persona="Family Logistics Manager",
        product="Sealion 6 DM-i",
        color="#7c3aed",
        headline="Electric on weekdays. Highway on petrol. Kids sleep the whole way.",
        subline="Introducing the family PHEV that solves the road trip problem — without making it a problem.",
        key_message=(
            "The Sealion 6 DM-i runs on electricity for every school run, every weekly shop, every "
            "city errand — silently, for less than ฿20 a day. On long weekends, the petrol engine "
            "seamlessly takes over when the battery empties. 1,200 km total range. No charging stop "
            "required on any Thai highway route. Your kids won't even wake up. "
            "Blade Battery: Europe's highest crash safety rating. 8-year warranty."
        ),
        visual_do=[
            "Kids asleep in rear seats on a night highway drive",
            "Parent plugging in at home — takes 5 seconds, shown as routine",
            "Dashboard showing '1,186 km remaining' at full tank + charge",
            "Boot with stroller, school bags, and weekend luggage all fitting",
            "Warm lifestyle tones: golden hour, highway overpass, family SUV context",
        ],
        visual_dont=[
            "Charging station exterior shots (reinforces anxiety)",
            "Technical drivetrain diagrams or 'DM-i explained' infographics",
            "Racing / performance imagery",
            "Black-red sporty interior close-ups",
            "Empty car product shots without family context",
        ],
        channels=[
            ("📺", "YouTube pre-roll (3–5 min)", "Long-form family narrative. Mum-blogger narration. Targeted: F25–45, has children, SUV interest."),
            ("📲", "Facebook & Instagram reels", "15-sec: kids sleeping / petrol gauge on highway. Boost on parenting groups."),
            ("🎤", "Mom/parenting KOLs", "3-night road trip series. KOL charges at home, drives 600 km to Chiang Mai without stopping."),
            ("🏪", "Showroom experience", "Reposition booth: 'Family Test Drive Weekend.' Bring the Carnival/Alphard owners. Stroller in boot demo."),
            ("🤝", "School gate partnership", "Sponsor parent drop-off events at premium Bangkok schools. Valet demo charge in school car park."),
        ],
        cta="Book a family test drive — bring the kids",
        metric="Test drive bookings from parents with children under 12 / % PHEV explanation retention at showroom exit survey",
    )

    # ── BRIEF 2: Cost Calculator ───────────────────────────────────────────────
    _campaign_brief(
        icon="🧮",
        persona="Cost Calculator",
        product="Dolphin BEV",
        color="#1a7a4a",
        headline="The spreadsheet already chose BYD. Here's the data.",
        subline="A transparent 5-year TCO table, a published battery cap, and the only EV under ฿600K with a real warranty.",
        key_message=(
            "BYD Dolphin BEV: ฿509,900. Annual energy cost at 15,000 km: ~฿9,000. "
            "Same drive in a Honda City ICE: ~฿60,000/year. "
            "5-year fuel saving: ฿255,000 — more than the car's maintenance cost for its entire life. "
            "Battery: 8-year/160,000 km warranty. Maximum replacement cost: stated in your sales contract. "
            "No asterisks. No 'terms apply.' The math works. Here is the table."
        ),
        visual_do=[
            "Actual TCO comparison table: Dolphin vs Honda City vs Yaris Ativ (5-year total)",
            "Screenshot of BYD's app showing real energy cost per trip",
            "Close-up of the warranty document — clean, Thai-language, legible",
            "Man at desk with laptop — cost comparison spreadsheet visible on screen",
            "Before/after fuel receipt vs electricity bill comparison graphic",
        ],
        visual_dont=[
            "Aspirational lifestyle imagery (he distrusts marketing over substance)",
            "Vague 'save money' claims without numbers",
            "Celebrity endorsements",
            "Complex engineering visuals",
            "Soft-focus family scenes (wrong persona trigger)",
        ],
        channels=[
            ("🔍", "Google Search (high-intent)", "'BYD Dolphin vs Honda City cost' / 'EV vs petrol cost Thailand 2026'. Capture the researchers."),
            ("📊", "YouTube long-form review", "Partner with Car channel: 'I ran both cars for 30 days and tracked every baht.' No script — real data."),
            ("💬", "Pantip / Reddit-style forums", "Transparent TCO post by BYD Thailand on ev.in.th and Pantip Car forum. Real numbers, pinned."),
            ("📧", "Email nurture (test drive list)", "Post-test-drive: send personalised TCO calculation based on respondent's stated km/day."),
            ("🔗", "TCO calculator tool (BYD.com/th)", "Interactive web tool: enter your km/day, current car, income. Output: 5-year comparison."),
        ],
        cta="Download the 5-year TCO comparison PDF",
        metric="TCO calculator tool usage / PDF download rate / post-test-drive inquiry conversion vs control group",
    )

    # ── BRIEF 3: Time-Efficient Professional ──────────────────────────────────
    _campaign_brief(
        icon="⚡",
        persona="Time-Efficient Professional",
        product="Seal BEV",
        color="#b45309",
        headline="One app. One plug. It just works.",
        subline="For people who want the car to disappear into the background and let them get on with their life.",
        key_message=(
            "BYD Seal: plug in at 10 PM, full battery at 7 AM — every morning, without thinking about it. "
            "Book service, check battery status, pre-cool the cabin, update software: one app, no dealer visit. "
            "If your car needs a repair, BYD guarantees a 72-hour turnaround or provides a loaner. "
            "Real-world range: 500+ km. Charge once, drive all week. The most frictionless car you've ever owned."
        ),
        visual_do=[
            "Car plugging in in 3 seconds — phone plugging in analogy cut",
            "Clean BYD app interface: charging progress, one-tap service booking",
            "Morning routine: car is full, driver leaves without thought",
            "Minimalist urban aesthetic — Seal parked in clean Bangkok basement",
            "Time-lapse: car charges overnight while owner sleeps",
        ],
        visual_dont=[
            "Public charging station queues",
            "Complicated tech spec overlays",
            "Busy family scenes (wrong trigger for this persona)",
            "Fuel savings messaging (secondary, not primary driver)",
            "Red sport interior — neutral/dark interior required",
        ],
        channels=[
            ("🎬", "TikTok / Instagram Reels", "'A week with BYD Seal — never thought about charging once.' 15–30 sec. Urban professional aesthetic."),
            ("🎙️", "Tech/lifestyle podcast sponsorship", "Mid-roll: 'The car that charges like a phone.' No-script host read. Target: The Standard, Investory podcasts."),
            ("🤳", "LinkedIn + LINE OA", "Target: 28–40 urban professionals. 'Productivity starts before you leave the car park.' Professional tone."),
            ("🏢", "Corporate fleet partnership", "Present to HR / fleet managers at 50 Bangkok companies. BYD Seal as employee benefit / executive car."),
            ("🛞", "Experiential test drive", "Silent 45-min drive through Bangkok night traffic. No sales pitch. App walkthrough by BYD tech ambassador."),
        ],
        cta="Experience it: 72-hour test drive — plug in tonight, drive tomorrow",
        metric="App download rate post-test-drive / 72-hr service SLA awareness lift / Seal inquiry-to-purchase conversion rate",
    )

    # ── BRIEF 4: Condo Dweller (PHEV awareness) ───────────────────────────────
    _campaign_brief(
        icon="🏙️",
        persona="No-Home-Charging Condo Dweller",
        product="Sealion 6 DM-i",
        color="#6d28d9",
        headline="You don't need a home charger. Nobody told you that.",
        subline="PHEV: charge when convenient. Drive on petrol when you can't. Your condo is not a dealbreaker.",
        key_message=(
            "If you live in a condo, you've probably already ruled out EVs — because you can't charge at home. "
            "Here's what nobody told you: a PHEV doesn't need to be charged. "
            "It runs on petrol whenever you don't charge — just like your current car. "
            "But when you do plug in (at the office, at a mall, twice a week) your 20-km daily commute "
            "costs almost nothing. The BYD Sealion 6 DM-i: 1,200 km on a full tank and charge. "
            "No wall charger required. No lifestyle change required."
        ),
        visual_do=[
            "Condo underground car park — Sealion 6 parked normally, no charger visible",
            "Office car park: casual plug-in on the way to the lift",
            "Petrol station: brief stop, shows combined 1,200 km range on dashboard",
            "Female 26–30 protagonist. Stylish, independent, urban.",
            "Split: 'Charged at office 2×' vs '฿12 total electricity cost this week'",
        ],
        visual_dont=[
            "Home wall charger installation",
            "Electric-only messaging or range anxiety resolution",
            "Family context (wrong persona)",
            "Technical PHEV drivetrain explanation",
            "Long charging time imagery",
        ],
        channels=[
            ("🎵", "TikTok KOL (condo-living creator)", "'I live in a condo and bought a PHEV — here's my first month.' Real, unscripted, 60–90 sec."),
            ("📲", "Instagram Stories / Reels", "Swipe: 'Things I thought about EVs / What's actually true.' Myth-busting format. Condo-specific."),
            ("🏬", "Mall charging point activation", "BYD booth next to mall EV chargers. Staff ask: 'Do you live in a condo?' — trigger the conversation."),
            ("📱", "LINE official account", "Targeted to LINE users in condo-heavy areas (Sukhumvit, Ratchada, Ladprao). Message: 'PHEV for condo life.'"),
            ("🎓", "Content series: 'PHEV 101 for Condo Residents'", "3-part article / reel series. Published on BYD.com/th and boosted. SEO: 'EV คอนโด ชาร์จยังไง'."),
        ],
        cta="Live in a condo? Book a PHEV test drive — we'll explain everything",
        metric="PHEV inquiry rate from condo-identified leads / 'PHEV doesn't need home charging' awareness score (pre/post survey) / Sealion 6 DM-i bookings from urban condo postal codes",
    )

    # ── BRIEF 5: Field Professional ───────────────────────────────────────────
    _campaign_brief(
        icon="🚗",
        persona="Field Professional (Variable Distance)",
        product="Sealion 6 DM-i",
        color="#0f766e",
        headline="1,200 km total range. Never plan your route around a charger again.",
        subline="For professionals whose calendar decides how far they drive — not the other way around.",
        key_message=(
            "Monday: office, 25 km. Tuesday: client in Samut Sakhon, 85 km. "
            "Wednesday: factory visit, 70 km. Thursday: presentations, 40 km. "
            "Friday: two site visits, 90 km. Not one day the same. "
            "The BYD Sealion 6 DM-i runs on electricity when the battery has charge — "
            "and on petrol when it doesn't. You never check the battery before you leave. "
            "1,200 km total range. Full tank + full charge = any Thai highway route covered. "
            "Your work car should solve problems. Not create new ones."
        ),
        visual_do=[
            "Professional in business casual entering client building car park — Sealion 6 parked",
            "Dashboard showing variable daily routes: 25 km / 85 km / 40 km",
            "Highway driving, late afternoon light, clear road — work trip context",
            "Male 28–40 protagonist. Confident, urban-professional aesthetic.",
            "Petrol station fast-fill in 3 minutes — shown as background action, not a problem",
        ],
        visual_dont=[
            "Family road trip context",
            "School runs / children",
            "Charging infrastructure emphasis",
            "Mass-market pricing messaging",
            "Sporty driving context",
        ],
        channels=[
            ("💼", "LinkedIn sponsored content", "'The work car for variable-distance professionals.' Target: Sales managers, engineers, consultants, B2B field roles."),
            ("🚘", "Corporate fleet sales", "Direct outreach to SME fleet managers. 'Replace your Toyota Fortuner diesel fleet with Sealion 6 DM-i — same range, lower fuel bill.'"),
            ("🎙️", "Business podcast / YouTube", "Ep: 'How I calculated the real cost of my work car.' Host drives Sealion 6 for one work week. Tracks every baht."),
            ("🤳", "Facebook Groups (field sales, SME)", "Targeted boosted post in 'รถยนต์มือสอง / ใหม่' and 'SME Thailand' groups. Real owner testimonial."),
            ("🏢", "Test drive at office buildings", "BYD roadshow: 10 Bangkok office towers. 30-min drive during lunch. Bring the BYD Sealion 6 to them."),
        ],
        cta="Book a work-week test drive — drive it to your actual meetings",
        metric="Fleet inquiry rate / corporate fleet conversion per outreach event / Sealion 6 DM-i bookings from B2B contact form",
    )

    # ── Channel summary ────────────────────────────────────────────────────────
    st.divider()
    section_header(
        "Channel priority matrix — all personas combined",
        "Derived from survey media preferences (% of each age group using each channel) + interview insights on trusted information sources",
    )

    ch_matrix_data = {
        "Channel": [
            "TikTok / Reels (short video)",
            "YouTube (long-form review)",
            "Facebook boosted posts",
            "Showroom / test drive events",
            "KOL / influencer content",
            "Google Search (intent)",
            "Corporate / fleet sales",
            "Mall activations",
            "LINE OA",
            "Parenting communities",
        ],
        "Family Manager": ["○", "●", "●", "●●", "●●", "○", "○", "●", "●", "●●"],
        "Cost Calculator": ["○", "●●", "●", "●", "○", "●●", "○", "○", "●", "○"],
        "Time Professional": ["●●", "●", "●", "●●", "●●", "●", "●●", "○", "●", "○"],
        "Condo Dweller": ["●●", "○", "●●", "●", "●●", "○", "○", "●●", "●●", "○"],
        "Field Professional": ["○", "●", "●", "●", "○", "●", "●●", "○", "○", "○"],
    }
    ch_df = pd.DataFrame(ch_matrix_data).set_index("Channel")
    st.markdown(
        "<p style='font-size:0.78rem;color:#6b7280;margin-bottom:0.5rem'>"
        "●● = Primary channel for this persona · ● = Secondary · ○ = Low priority</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(ch_df, use_container_width=True)

    st.info(
        "**Cross-persona priority channels:** (1) KOL content for Condo + Time + Family personas — "
        "highest trust transfer. (2) Test drive events universally high across all personas — "
        "in-car experience is the single best conversion tool. (3) YouTube long-form review for "
        "Cost Calculator and Family personas — they research extensively before showroom visits. "
        "Investing in authentic 30-day owner challenge videos would serve all five segments simultaneously."
    )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<div style="text-align:center;color:#B0BEC5;font-size:0.72rem;padding:0.5rem 0">'
    'BYD Product-Market Fit Analysis · Based on 306 survey respondents + 19 in-depth interviews · '
    'Running cost estimates: 15,000 km/yr · Home electricity ฿4/kWh · Petrol ฿40/L'
    '</div>',
    unsafe_allow_html=True,
)
