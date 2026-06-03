"""Page 6 — EV Readiness segments, awareness, and likelihood to switch."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, hbar, heatmap_pct, stacked_bar_pct, LAYOUT_BASE,
)
from survey_utils import PT_ORDER, POWERTRAIN_COLORS
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Segments & EV Readiness", layout="wide")
apply_byd_theme()
page_header("Segments & EV Readiness", "Consumer readiness composite index, adoption likelihood, and technology familiarity")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── EV Readiness Index overview ────────────────────────────────────────────────
st.subheader("EV Readiness Index (1–10)")
st.caption("Composite of likelihood to switch in 3y (35%), charging convenience (35%), BEV/PHEV familiarity (30%)")

ev_ri = df["ev_readiness_index"].dropna()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean", f"{ev_ri.mean():.2f}")
c2.metric("Median", f"{ev_ri.median():.2f}")
c3.metric("High readiness (≥7)", f"{(ev_ri >= 7).sum():,}", f"{(ev_ri >= 7).mean()*100:.0f}%")
c4.metric("Low readiness (≤3)", f"{(ev_ri <= 3).sum():,}", f"{(ev_ri <= 3).mean()*100:.0f}%")

# Distribution histogram
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(
    x=ev_ri, nbinsx=18, marker_color="#2E86AB",
    name="All respondents",
))
fig_hist.update_layout(**LAYOUT_BASE, title="EV Readiness Index distribution",
                       xaxis_title="Index (1–10)", yaxis_title="Count", height=360)
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ── EV Readiness by segment ────────────────────────────────────────────────────
st.subheader("EV Readiness by segment")

tab_age, tab_income, tab_pt, tab_gender, tab_dd = st.tabs(
    ["By age", "By income", "By powertrain", "By gender", "By driving distance"]
)

def readiness_box(groups: dict, title: str) -> go.Figure:
    fig = go.Figure()
    colors = plc.qualitative.Set2
    for i, (label, subset) in enumerate(groups.items()):
        vals = subset["ev_readiness_index"].dropna()
        if vals.empty:
            continue
        fig.add_trace(go.Box(
            y=vals, name=f"{label}<br>(n={len(vals)})",
            marker_color=colors[i % len(colors)], boxmean=True,
        ))
    fig.update_layout(**LAYOUT_BASE, title=title, yaxis_title="EV Readiness (1–10)", height=420)
    return fig

with tab_age:
    groups = {str(a): df[df["age_range"] == a] for a in age_order if a in df["age_range"].values}
    st.plotly_chart(readiness_box(groups, "EV Readiness by age group"), use_container_width=True)

with tab_income:
    groups = {str(i): df[df["monthly_income"] == i] for i in income_order if i in df["monthly_income"].values}
    fig = readiness_box(groups, "EV Readiness by income band")
    fig.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)

with tab_pt:
    groups = {pt: df[df["powertrain_short"] == pt] for pt in PT_ORDER if pt in df["powertrain_short"].values}
    fig = readiness_box(groups, "EV Readiness by powertrain choice")
    # Override colors with POWERTRAIN_COLORS
    for trace in fig.data:
        pt_name = trace.name.split("<")[0]
        if pt_name in POWERTRAIN_COLORS:
            trace.marker.color = POWERTRAIN_COLORS[pt_name]
    st.plotly_chart(fig, use_container_width=True)

with tab_gender:
    genders = df["gender"].dropna().unique().tolist()
    groups = {g: df[df["gender"] == g] for g in genders}
    st.plotly_chart(readiness_box(groups, "EV Readiness by gender"), use_container_width=True)

with tab_dd:
    groups = {str(d): df[df["daily_driving_distance"] == d] for d in dd_order if d in df["daily_driving_distance"].values}
    st.plotly_chart(readiness_box(groups, "EV Readiness by daily driving distance"), use_container_width=True)

st.divider()

# ── Likelihood to switch ───────────────────────────────────────────────────────
st.subheader("Likelihood to switch to EV in 3 years")

lik_order = [
    "Definitely will not switch to EV",
    "Unlikely to switch to EV",
    "Not sure",
    "Likely to switch to EV",
    "Definitely will switch to EV",
    "Already in the process of purchasing / already own an EV",
]

lik_vc = df["likelihood_switch_ev_3y"].value_counts()
lik_vc_ordered = lik_vc.reindex([l for l in lik_order if l in lik_vc.index])
colors_lik = plc.sample_colorscale("RdYlGn", [i / max(1, len(lik_vc_ordered) - 1) for i in range(len(lik_vc_ordered))])

fig_lik = go.Figure(go.Bar(
    x=[str(l)[:45] for l in lik_vc_ordered.index],
    y=lik_vc_ordered.values,
    marker=dict(color=colors_lik),
    text=lik_vc_ordered.values, textposition="outside",
))
fig_lik.update_layout(**LAYOUT_BASE, title="Likelihood to switch to EV in 3 years",
                      yaxis_title="Count", xaxis_tickangle=-25, height=400)
st.plotly_chart(fig_lik, use_container_width=True)

# Likelihood by age
fig_lik_age = stacked_bar_pct(df, "age_range", "likelihood_switch_ev_3y",
                               "Likelihood to switch × Age group (row %)",
                               row_order=age_order)
st.plotly_chart(fig_lik_age, use_container_width=True)

st.divider()

# ── Brand awareness by age (phase 11) ─────────────────────────────────────────
st.subheader("Technology familiarity by age — awareness proxy")
st.caption("Average self-rated familiarity (1–5) per powertrain type, sliced by age group")

fam_cols = {
    "familiarity_ice": "ICE", "familiarity_hev": "HEV",
    "familiarity_phev": "PHEV", "familiarity_reev": "REEV", "familiarity_bev": "BEV",
}

rows = []
for age in age_order:
    sub = df[df["age_range"] == age]
    if sub.empty:
        continue
    for col, label in fam_cols.items():
        mean_val = pd.to_numeric(sub[col], errors="coerce").mean()
        rows.append({"age": str(age), "powertrain": label, "mean_familiarity": mean_val})

fam_df = pd.DataFrame(rows)

fig_fam = go.Figure()
for pt, col in zip(["ICE", "HEV", "PHEV", "REEV", "BEV"], [POWERTRAIN_COLORS.get(p, "#888") for p in ["ICE", "HEV", "PHEV", "REEV", "BEV"]]):
    sub_pt = fam_df[fam_df["powertrain"] == pt]
    fig_fam.add_trace(go.Scatter(
        x=sub_pt["age"].tolist(), y=sub_pt["mean_familiarity"].tolist(),
        mode="lines+markers", name=pt,
        line=dict(color=col, width=2), marker=dict(size=8),
    ))
fig_fam.update_layout(**LAYOUT_BASE,
                      title="Mean familiarity score (1–5) by age group",
                      yaxis_title="Mean familiarity", xaxis_title="Age group", height=420)
st.plotly_chart(fig_fam, use_container_width=True)

# Heatmap version
z_vals = fam_df.pivot(index="powertrain", columns="age", values="mean_familiarity")
z_vals = z_vals[[str(a) for a in age_order if str(a) in z_vals.columns]]

fig_heat = go.Figure(go.Heatmap(
    z=z_vals.values,
    x=z_vals.columns.tolist(),
    y=z_vals.index.tolist(),
    text=[[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in z_vals.values],
    texttemplate="%{text}",
    colorscale="Blues",
    colorbar=dict(title="Mean (1–5)"),
))
fig_heat.update_layout(**LAYOUT_BASE, title="Familiarity heatmap — powertrain × age",
                       height=300)
st.plotly_chart(fig_heat, use_container_width=True)
