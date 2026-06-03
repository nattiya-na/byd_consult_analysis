"""Page 2 — Powertrain preferences by segment."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, hbar, heatmap_pct, stacked_bar_pct,
    explode_and_count, LAYOUT_BASE,
)
from survey_utils import PT_ORDER, POWERTRAIN_COLORS
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Powertrain Preferences", layout="wide")
apply_byd_theme()
page_header("Powertrain Preferences", "BEV / PHEV / HEV / ICE adoption patterns across consumer segments")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Top-line metrics ───────────────────────────────────────────────────────────
st.subheader("What would you choose today?")

pt_today = df["powertrain_short"].value_counts()
cols = st.columns(len(pt_today))
for col, (pt, cnt) in zip(cols, pt_today.items()):
    col.metric(pt, f"{cnt:,}", f"{cnt/len(df)*100:.0f}%")

# ── Considering vs. choose today ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["Considering (multi-select)", "Would choose today (single)"])

with tab1:
    vc_cons = explode_and_count(df, "powertrain_considering")
    colors_list = [POWERTRAIN_COLORS.get(p, "#888") for p in vc_cons.index]
    fig = go.Figure(go.Bar(
        x=vc_cons.values[::-1], y=vc_cons.index[::-1].tolist(),
        orientation="h", marker=dict(color=colors_list[::-1]),
        text=vc_cons.values[::-1], textposition="outside",
    ))
    fig.update_layout(**LAYOUT_BASE, title="Powertrains under consideration (multi-select, exploded)",
                      xaxis_title="Mentions", height=320)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    vc_today = df["powertrain_short"].value_counts().reindex(
        [p for p in PT_ORDER if p in df["powertrain_short"].dropna().unique()]
    )
    colors_list2 = [POWERTRAIN_COLORS.get(p, "#888") for p in vc_today.index]
    fig2 = go.Figure(go.Bar(
        x=vc_today.values, y=vc_today.index.tolist(),
        orientation="h", marker=dict(color=colors_list2),
        text=vc_today.values, textposition="outside",
    ))
    fig2.update_layout(**LAYOUT_BASE, title="Powertrain would choose today",
                       xaxis_title="Count", height=320)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Powertrain by demographic breakdown ───────────────────────────────────────
st.subheader("Powertrain choice by demographic")

tab_age, tab_income, tab_gender, tab_source = st.tabs(["By age", "By income", "By gender", "By source"])

with tab_age:
    fig = stacked_bar_pct(df, "age_range", "powertrain_short",
                          "Powertrain choice by age group (row %)",
                          row_order=age_order, col_order=PT_ORDER, color_map=POWERTRAIN_COLORS)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Each bar = 100% within that age group")

with tab_income:
    fig = stacked_bar_pct(df, "monthly_income", "powertrain_short",
                          "Powertrain choice by income (row %)",
                          row_order=income_order, col_order=PT_ORDER, color_map=POWERTRAIN_COLORS)
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

with tab_gender:
    fig = stacked_bar_pct(df, "gender", "powertrain_short",
                          "Powertrain choice by gender (row %)",
                          col_order=PT_ORDER, color_map=POWERTRAIN_COLORS)
    st.plotly_chart(fig, use_container_width=True)

with tab_source:
    fig = stacked_bar_pct(df, "data_source", "powertrain_short",
                          "Powertrain choice by survey cohort (row %)",
                          col_order=PT_ORDER, color_map=POWERTRAIN_COLORS)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Heatmaps ──────────────────────────────────────────────────────────────────
st.subheader("Powertrain concentration heatmaps")
c1, c2 = st.columns(2)

with c1:
    fig = heatmap_pct(df, "age_range", "powertrain_short",
                      "Age × Powertrain (row %)",
                      row_order=age_order, col_order=PT_ORDER, colorscale="Blues")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = heatmap_pct(df, "monthly_income", "powertrain_short",
                      "Income × Powertrain (row %)",
                      row_order=income_order, col_order=PT_ORDER, colorscale="Purples")
    st.plotly_chart(fig, use_container_width=True)

# ── Familiarity scores ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Technology familiarity (1–5 self-rated)")

fam_cols = {
    "familiarity_ice": "ICE",
    "familiarity_hev": "HEV",
    "familiarity_phev": "PHEV",
    "familiarity_reev": "REEV",
    "familiarity_bev": "BEV",
}

fig_fam = go.Figure()
for col, label in fam_cols.items():
    vals = pd.to_numeric(df[col], errors="coerce").dropna()
    fig_fam.add_trace(go.Box(
        y=vals, name=label,
        marker_color=POWERTRAIN_COLORS.get(label, "#888"),
        boxmean=True,
    ))
fig_fam.update_layout(**LAYOUT_BASE,
                      title="Self-rated familiarity by powertrain type (1=not familiar, 5=very familiar)",
                      yaxis_title="Familiarity score", height=400)
st.plotly_chart(fig_fam, use_container_width=True)
