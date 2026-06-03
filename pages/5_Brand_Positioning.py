"""Page 5 — Brand positioning and BYD vs. competitors."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, hbar, heatmap_pct, stacked_bar_pct,
    explode_and_count, LAYOUT_BASE,
)
from survey_utils import PT_ORDER, POWERTRAIN_COLORS, split_brand_segments
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Brand Positioning", layout="wide")
apply_byd_theme()
page_header("Brand Positioning & Competitive Landscape", "BYD consideration rates vs. Toyota, Honda and Tesla across demographics")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Brand consideration landscape ─────────────────────────────────────────────
st.subheader("Brands under consideration")

all_brands = []
for val in df["brands_considering"].dropna():
    for b in split_brand_segments(str(val)):
        clean = b.strip()
        if clean:
            all_brands.append(clean.upper() if len(clean) <= 4 else clean.title())

brand_vc = pd.Series(all_brands).value_counts().head(20)
fig_brand = go.Figure(go.Bar(
    x=brand_vc.values[::-1], y=brand_vc.index[::-1].tolist(),
    orientation="h",
    marker=dict(
        color=["#2E86AB" if "BYD" in b.upper() else "#BC4749" if b.upper() in ["TOYOTA", "HONDA"]
               else "#F18F01" if b.upper() == "TESLA" else "#95A3A6"
               for b in brand_vc.index[::-1]]
    ),
    text=brand_vc.values[::-1], textposition="outside",
))
fig_brand.update_layout(**LAYOUT_BASE, title="Brands under consideration (all respondents)",
                        xaxis_title="Mentions", height=max(400, 32 * len(brand_vc)))
st.plotly_chart(fig_brand, use_container_width=True)

# BYD consideration rate
byd_mask = df["brands_considering"].fillna("").str.contains(r"\bBYD\b", case=False, regex=True)
toyota_honda_mask = (
    df["brands_considering"].fillna("").str.contains(r"\btoyota\b", case=False, regex=True) |
    df["brands_considering"].fillna("").str.contains(r"\bhonda\b", case=False, regex=True)
)
tesla_mask = df["brands_considering"].fillna("").str.contains(r"\btesla\b", case=False, regex=True)

c1, c2, c3 = st.columns(3)
c1.metric("BYD consideration rate", f"{byd_mask.mean()*100:.1f}%", f"{byd_mask.sum()} respondents")
c2.metric("Toyota / Honda rate", f"{toyota_honda_mask.mean()*100:.1f}%", f"{toyota_honda_mask.sum()} respondents")
c3.metric("Tesla consideration rate", f"{tesla_mask.mean()*100:.1f}%", f"{tesla_mask.sum()} respondents")

st.divider()

# ── BYD cohort analysis ────────────────────────────────────────────────────────
st.subheader("BYD vs. Toyota/Honda — powertrain profile")
st.caption("Respondents who consider BYD differ in powertrain preference vs. Toyota/Honda loyalists.")

cohort_data = {
    "BYD": df.loc[byd_mask, "powertrain_short"].value_counts(normalize=True),
    "Toyota/Honda": df.loc[toyota_honda_mask, "powertrain_short"].value_counts(normalize=True),
    "Tesla": df.loc[tesla_mask, "powertrain_short"].value_counts(normalize=True),
    "All": df["powertrain_short"].value_counts(normalize=True),
}
comp_df = pd.DataFrame(cohort_data).T.fillna(0)
bar_cols = [c for c in PT_ORDER if c in comp_df.columns]
comp_df = comp_df.reindex(columns=bar_cols, fill_value=0)

fig_comp = go.Figure()
for pt in bar_cols:
    vals = comp_df[pt].values * 100
    fig_comp.add_trace(go.Bar(
        name=pt, x=comp_df.index.tolist(), y=vals,
        marker_color=POWERTRAIN_COLORS.get(pt, "#888"),
        text=[f"{v:.0f}%" if v >= 3 else "" for v in vals],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=10),
    ))
fig_comp.update_layout(**LAYOUT_BASE, barmode="stack",
                       title="Powertrain preference — brand consideration cohorts",
                       yaxis_title="% within cohort", height=400)
st.plotly_chart(fig_comp, use_container_width=True)

st.divider()

# ── BYD reasons ───────────────────────────────────────────────────────────────
st.subheader("Why (and why not) BYD")

col_a, col_b = st.columns(2)
with col_a:
    fig_yes = hbar(df["byd_considering_reason"], "Reasons FOR considering BYD", color="Blues")
    st.plotly_chart(fig_yes, use_container_width=True)

with col_b:
    fig_no = hbar(df["byd_not_considering_reason"], "Reasons for NOT considering BYD", color="Reds")
    st.plotly_chart(fig_no, use_container_width=True)

st.divider()

# ── BYD view factors ──────────────────────────────────────────────────────────
st.subheader("What factors shape BYD's image?")
fig_view = hbar(df["byd_view_factor"], "BYD view factors (how respondents describe BYD)", color="Purples")
st.plotly_chart(fig_view, use_container_width=True)

st.divider()

# ── BYD consideration by age and income ───────────────────────────────────────
st.subheader("BYD consideration rate by demographic")

df["considers_byd"] = byd_mask

c1, c2 = st.columns(2)
with c1:
    byd_by_age = df.groupby("age_range")["considers_byd"].mean() * 100
    byd_by_age = byd_by_age.reindex([a for a in age_order if a in byd_by_age.index])
    fig_ba = go.Figure(go.Bar(
        x=[str(a) for a in byd_by_age.index], y=byd_by_age.values,
        marker_color="#2E86AB",
        text=[f"{v:.0f}%" for v in byd_by_age.values], textposition="outside",
    ))
    fig_ba.update_layout(**LAYOUT_BASE, title="BYD consideration rate by age group",
                         yaxis_title="% considering BYD", height=380)
    st.plotly_chart(fig_ba, use_container_width=True)

with c2:
    byd_by_inc = df.groupby("monthly_income")["considers_byd"].mean() * 100
    byd_by_inc = byd_by_inc.reindex([i for i in income_order if i in byd_by_inc.index])
    fig_bi = go.Figure(go.Bar(
        x=[str(i) for i in byd_by_inc.index], y=byd_by_inc.values,
        marker_color="#A23B72",
        text=[f"{v:.0f}%" for v in byd_by_inc.values], textposition="outside",
    ))
    fig_bi.update_layout(**LAYOUT_BASE, title="BYD consideration rate by income band",
                         yaxis_title="% considering BYD", height=380, xaxis_tickangle=-30)
    st.plotly_chart(fig_bi, use_container_width=True)

# BYD by powertrain preference
byd_by_pt = df.groupby("powertrain_short")["considers_byd"].agg(["mean", "sum", "count"])
byd_by_pt["rate_%"] = (byd_by_pt["mean"] * 100).round(1)
byd_by_pt = byd_by_pt[["sum", "count", "rate_%"]].rename(
    columns={"sum": "n_considering_BYD", "count": "n_total"}
)
st.subheader("BYD consideration rate by powertrain preference")
st.dataframe(
    byd_by_pt.sort_values("rate_%", ascending=False),
    use_container_width=True,
)
