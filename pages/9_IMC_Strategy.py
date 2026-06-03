"""Page 9 — IMC Strategy Dashboard: Gen Z (BEV) vs. Middle Age (PHEV/REEV)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import load_survey, sidebar_filters, hbar, LAYOUT_BASE
from survey_utils import PT_ORDER, POWERTRAIN_COLORS, split_multiselect
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="IMC Strategy", layout="wide")
apply_byd_theme()
page_header(
    "IMC Strategy Dashboard",
    "Integrated Marketing Communication channel mix and message framing — Gen Z (BEV) vs. Middle Age (PHEV/REEV)",
)
st.info("**Objective:** Identify the right IMC channel mix per powertrain segment.  "
        "**Primary targets:** Gen Z (18–24) → BEV · Middle Age (35–54) → PHEV/REEV")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# Feature engineering
GEN_MAP = {
    "18–24": "Gen Z", "25–34": "Millennial",
    "35–44": "Gen X", "45–54": "Boomer", "55+": "Boomer+",
}
GEN_ORDER = ["Gen Z", "Millennial", "Gen X", "Boomer", "Boomer+"]
GEN_COLORS = {
    "Gen Z": "#2E86AB", "Millennial": "#52B788", "Gen X": "#E07A5F",
    "Boomer": "#C77DFF", "Boomer+": "#F18F01",
}

df["generation"] = df["age_range"].map(GEN_MAP)
df["is_genz"] = df["age_range"].isin(["18–24"])
df["is_midage"] = df["age_range"].isin(["35–44", "45–54"])
df["persona_imc"] = df.apply(
    lambda r: "Gen Z" if r["is_genz"] else ("Middle Age" if r["is_midage"] else "Other"), axis=1
)

PC = {"Gen Z": "#2E86AB", "Middle Age": "#E07A5F", "Other": "#95A3A6", "All": "#6C757D"}

def explode_col(series, sep=";"):
    rows = []
    for val in series.dropna():
        for tok in str(val).split(sep):
            tok = tok.strip()
            if tok:
                rows.append(tok)
    return pd.Series(rows)

# ── Persona overview ───────────────────────────────────────────────────────────
st.subheader("Persona overview")
c1, c2, c3 = st.columns(3)
c1.metric("Gen Z (18–24)", f"{df['is_genz'].sum():,}", f"{df['is_genz'].mean()*100:.0f}% of sample")
c2.metric("Middle Age (35–54)", f"{df['is_midage'].sum():,}", f"{df['is_midage'].mean()*100:.0f}% of sample")
c3.metric("Other / Millennial", f"{(~df['is_genz'] & ~df['is_midage']).sum():,}", "")

st.divider()

# ── Powertrain by generation ───────────────────────────────────────────────────
st.subheader("Powertrain choice by generation")

pt_cols = [c for c in PT_ORDER if c in df["powertrain_short"].dropna().unique()]
gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
ct = pd.crosstab(df["generation"], df["powertrain_short"], normalize="index") * 100
ct = ct.reindex(index=gen_rows, columns=pt_cols, fill_value=0)

fig_pt_gen = go.Figure()
for pt in pt_cols:
    vals = ct[pt].values
    fig_pt_gen.add_trace(go.Bar(
        name=pt, x=[str(g) for g in ct.index], y=vals,
        marker_color=POWERTRAIN_COLORS.get(pt, "#888"),
        text=[f"{v:.0f}%" if v >= 4 else "" for v in vals],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=10),
    ))
fig_pt_gen.update_layout(**LAYOUT_BASE, barmode="stack",
                         title="Powertrain choice by generation (row %)",
                         yaxis_title="% within generation", height=380)
st.plotly_chart(fig_pt_gen, use_container_width=True)

# ── EV Readiness by generation ─────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    fig_ri = go.Figure()
    for i, gen in enumerate(gen_rows):
        sub = df.loc[df["generation"] == gen, "ev_readiness_index"].dropna()
        if sub.empty:
            continue
        fig_ri.add_trace(go.Box(
            y=sub, name=f"{gen}<br>(n={len(sub)})",
            marker_color=GEN_COLORS.get(gen, "#888"), boxmean=True,
        ))
    fig_ri.update_layout(**LAYOUT_BASE, title="EV Readiness Index by generation",
                         yaxis_title="Index (1–10)", height=380)
    st.plotly_chart(fig_ri, use_container_width=True)

with col2:
    # Charging convenience by persona
    chg_order_short = ["Home charging", "Somewhat convenient", "Mostly public charging", "Not convenient at all"]
    CHARGING_MAP = {
        "Very convenient — I can likely charge at home": "Home charging",
        "Somewhat convenient — condo/workplace/shared charging may be available": "Somewhat convenient",
        "Not very convenient — I would mostly depend on public charging": "Mostly public charging",
        "Not convenient at all": "Not convenient at all",
    }
    df["charging_short"] = df["charging_convenience"].map(
        lambda x: next((v for k, v in CHARGING_MAP.items() if pd.notna(x) and str(x).startswith(k[:20])), None)
    )
    sub2 = df.dropna(subset=["persona_imc", "charging_short"])
    ct_chg = pd.crosstab(sub2["persona_imc"], sub2["charging_short"], normalize="index") * 100
    ct_chg = ct_chg.reindex(columns=[c for c in chg_order_short if c in ct_chg.columns], fill_value=0)

    fig_chg = go.Figure()
    chg_colors = ["#2E86AB", "#52B788", "#F18F01", "#BC4749"]
    for j, chg in enumerate(ct_chg.columns):
        fig_chg.add_trace(go.Bar(
            name=chg, x=ct_chg.index.tolist(), y=ct_chg[chg].values,
            marker_color=chg_colors[j % len(chg_colors)],
            text=[f"{v:.0f}%" if v >= 4 else "" for v in ct_chg[chg].values],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_chg.update_layout(**LAYOUT_BASE, barmode="stack",
                          title="Charging convenience by IMC persona (row %)",
                          yaxis_title="% within group", height=380)
    st.plotly_chart(fig_chg, use_container_width=True)

st.divider()

# ── Purchase factors comparison ────────────────────────────────────────────────
st.subheader("What matters most — Gen Z vs. Middle Age vs. All")

groups_imc = {
    "Gen Z": df["is_genz"],
    "Middle Age": df["is_midage"],
    "All": pd.Series(True, index=df.index),
}
factor_pcts = {}
for label, mask in groups_imc.items():
    top_factors = explode_col(df.loc[mask, "purchase_factors_top3"])
    if top_factors.empty:
        continue
    factor_pcts[label] = (top_factors.value_counts(normalize=True) * 100).head(10)

all_factors = factor_pcts.get("All", pd.Series(dtype=float)).head(10).index.tolist()
fig_pf_gen = go.Figure()
for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"]), ("All", PC["All"])]:
    if label not in factor_pcts:
        continue
    vals = [factor_pcts[label].get(f, 0) for f in all_factors]
    fig_pf_gen.add_trace(go.Bar(
        name=label, x=vals, y=all_factors, orientation="h",
        marker_color=color, opacity=0.85,
    ))
fig_pf_gen.update_layout(**LAYOUT_BASE, barmode="group",
                         title="Top purchase factors — Gen Z vs. Middle Age vs. All (%)",
                         xaxis_title="% of mentions", height=440,
                         legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_pf_gen, use_container_width=True)

st.divider()

# ── Information sources ────────────────────────────────────────────────────────
st.subheader("IMC channel priority — information sources by persona")
st.caption("Where each segment goes for car research = where to allocate media spend")

INFO_NORM = {
    "TikTok": "TikTok / Social media",
    "Social media": "TikTok / Social media",
    "Facebook": "Facebook",
    "YouTube": "YouTube",
}
INFO_ORDER = [
    "TikTok / Social media", "YouTube", "Auto shows", "Friends / family",
    "Automotive websites / forums", "Influencers / KOLs / reviewers",
    "Test-drive events", "Dealers / showrooms", "TV / radio",
]

def norm_sources(series):
    rows = []
    for val in series.dropna():
        for tok in str(val).split(";"):
            tok = tok.strip()
            tok = INFO_NORM.get(tok, tok)
            if tok and len(tok) > 2:
                rows.append(tok)
    return pd.Series(rows)

ns = {k: int(mask.sum()) for k, mask in groups_imc.items() if k != "All"}
source_pcts = {}
for label, mask in groups_imc.items():
    if label == "All":
        continue
    src = norm_sources(df.loc[mask, "info_sources"])
    if src.empty:
        continue
    source_pcts[label] = (src.value_counts(normalize=True) * 100)

all_srcs_raw = norm_sources(df["info_sources"])
top_srcs = [s for s in INFO_ORDER if s in all_srcs_raw.value_counts().index]
extra = [s for s in all_srcs_raw.value_counts().head(12).index if s not in top_srcs]
display_srcs = (top_srcs + extra)[:10]

fig_info_imc = go.Figure()
for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"])]:
    if label not in source_pcts:
        continue
    vals = [source_pcts[label].get(s, 0) for s in display_srcs]
    fig_info_imc.add_trace(go.Bar(
        name=f"{label} (n={ns.get(label, 0)})", x=vals, y=display_srcs,
        orientation="h", marker_color=color, opacity=0.85,
    ))
fig_info_imc.update_layout(**LAYOUT_BASE, barmode="group",
                           title="Information sources — IMC channel priority by persona (%)",
                           xaxis_title="% of respondents in group", height=420,
                           legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_info_imc, use_container_width=True)

st.divider()

# ── Barriers by persona ────────────────────────────────────────────────────────
st.subheader("EV adoption barriers — Gen Z vs. Middle Age")

barrier_pcts = {}
for label, mask in groups_imc.items():
    barriers = explode_col(df.loc[mask, "ev_adoption_barriers"])
    if barriers.empty:
        continue
    barrier_pcts[label] = (barriers.value_counts(normalize=True) * 100).head(8)

all_barriers = barrier_pcts.get("All", pd.Series(dtype=float)).head(8).index.tolist() if "All" in barrier_pcts else []
if not all_barriers and barrier_pcts:
    first_key = list(barrier_pcts.keys())[0]
    all_barriers = barrier_pcts[first_key].head(8).index.tolist()

fig_bar_imc = go.Figure()
for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"]), ("All", PC["All"])]:
    if label not in barrier_pcts:
        continue
    vals = [barrier_pcts[label].get(b, 0) for b in all_barriers]
    fig_bar_imc.add_trace(go.Bar(
        name=label, x=vals, y=[b[:45] for b in all_barriers], orientation="h",
        marker_color=color, opacity=0.85,
    ))
fig_bar_imc.update_layout(**LAYOUT_BASE, barmode="group",
                          title="EV barriers — Gen Z vs. Middle Age vs. All (%)",
                          xaxis_title="% mentions", height=440,
                          legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_bar_imc, use_container_width=True)

st.divider()

# ── Budget by persona ──────────────────────────────────────────────────────────
st.subheader("Budget range by IMC persona")

BUDGET_ORDER = [
    "Below 500,000 THB", "500,001 – 800,000 THB",
    "800,001 – 1,200,000 THB", "1,200,001 – 1,500,000 THB",
    "1,500,001 – 2,000,000 THB", "Above 2,000,000 THB", "Not sure",
]
fig_budget = go.Figure()
for label, mask in [("Gen Z", df["is_genz"]), ("Middle Age", df["is_midage"])]:
    bvc = df.loc[mask, "budget_range"].value_counts(normalize=True) * 100
    bvc_ordered = bvc.reindex([b for b in BUDGET_ORDER if b in bvc.index], fill_value=0)
    fig_budget.add_trace(go.Bar(
        name=label, x=[b[:30] for b in bvc_ordered.index], y=bvc_ordered.values,
        marker_color=PC[label], opacity=0.85,
    ))
fig_budget.update_layout(**LAYOUT_BASE, barmode="group",
                         title="Budget range — Gen Z vs. Middle Age",
                         yaxis_title="% within group", xaxis_tickangle=-25, height=400)
st.plotly_chart(fig_budget, use_container_width=True)

st.divider()

# ── IMC recommendations summary ────────────────────────────────────────────────
st.subheader("IMC strategy summary")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#002D62 0%,#003D7A 100%);
                    padding:1.5rem 1.75rem;border-radius:12px;color:white;height:100%">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem">
                <span style="background:#00A851;padding:2px 10px;border-radius:4px;
                             font-weight:700;font-size:0.8rem">GEN Z</span>
                <span style="font-size:1.05rem;font-weight:700">BEV Focus</span>
            </div>
            <p style="color:#A8D8C0;font-size:0.82rem;margin:0 0 0.8rem">
                <strong style="color:white">Message:</strong> Performance, technology, and environmental credentials.
                Social proof from young Thai BEV owners.
            </p>
            <p style="color:#00A851;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;
                      font-weight:700;margin:0.8rem 0 0.35rem">Priority channels</p>
            <ul style="margin:0;padding-left:1.1rem;color:#DDE8F5;font-size:0.83rem;line-height:1.7">
                <li>TikTok / short-form video (15–30s)</li>
                <li>YouTube reviews and long-form comparisons</li>
                <li>Influencer / KOL partnerships (auto + lifestyle)</li>
                <li>Test-drive events and motor shows</li>
            </ul>
            <p style="color:#00A851;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;
                      font-weight:700;margin:0.8rem 0 0.35rem">Creative hooks</p>
            <ul style="margin:0;padding-left:1.1rem;color:#DDE8F5;font-size:0.83rem;line-height:1.7">
                <li>"Your first car is electric" — normalise BEV as default</li>
                <li>Monthly savings calculator vs. petrol</li>
                <li>Peer testimonials: 1-year BYD owner stories</li>
                <li>Showcase Lunar Gray / neutral interior options</li>
            </ul>
            <p style="background:rgba(0,168,81,0.2);border-radius:6px;padding:0.5rem 0.75rem;
                      margin:0.8rem 0 0;font-size:0.82rem;color:#A8FFD0">
                <strong>Price message:</strong> Transparent TCO, not just sticker price.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b:
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#3D1A00 0%,#6B3200 100%);
                    padding:1.5rem 1.75rem;border-radius:12px;color:white;height:100%">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem">
                <span style="background:#F59E0B;color:#1A1A2E;padding:2px 10px;border-radius:4px;
                             font-weight:700;font-size:0.8rem">MIDDLE AGE</span>
                <span style="font-size:1.05rem;font-weight:700">PHEV / REEV Focus</span>
            </div>
            <p style="color:#FFD8A8;font-size:0.82rem;margin:0 0 0.8rem">
                <strong style="color:white">Message:</strong> Reliability, family safety, and
                no-compromise practicality. PHEV education first.
            </p>
            <p style="color:#F59E0B;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;
                      font-weight:700;margin:0.8rem 0 0.35rem">Priority channels</p>
            <ul style="margin:0;padding-left:1.1rem;color:#FFE8CC;font-size:0.83rem;line-height:1.7">
                <li>Family-oriented Facebook content + community groups</li>
                <li>Automotive review websites and forums</li>
                <li>Dealer showroom — test drive, family demo day</li>
                <li>TV / traditional media (builds stability perception)</li>
                <li>Friends / family word-of-mouth activation</li>
            </ul>
            <p style="color:#F59E0B;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;
                      font-weight:700;margin:0.8rem 0 0.35rem">Creative hooks</p>
            <ul style="margin:0;padding-left:1.1rem;color:#FFE8CC;font-size:0.83rem;line-height:1.7">
                <li>"Charge at home. Refuel on long trips. Zero compromise."</li>
                <li>Family road-trip content — PHEV + petrol fallback</li>
                <li>Service center map + SLA commitment</li>
                <li>"Thai families trust BYD" — long-term owner testimonials</li>
            </ul>
            <p style="background:rgba(245,158,11,0.2);border-radius:6px;padding:0.5rem 0.75rem;
                      margin:0.8rem 0 0;font-size:0.82rem;color:#FFD8A8">
                <strong>Price message:</strong> Total cost vs. HEV Toyota over 5 years.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
