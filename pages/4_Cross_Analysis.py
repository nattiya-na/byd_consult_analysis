"""Page 4 — Cross analysis: demographics × EV readiness / driving distance / etc."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, heatmap_pct, stacked_bar_pct,
    LAYOUT_BASE,
)
from survey_utils import PT_ORDER, POWERTRAIN_COLORS, DD_CANONICAL_ORDER, INCOME_CANONICAL_ORDER
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Cross Analysis", layout="wide")
apply_byd_theme()
page_header("Cross Analysis", "Multi-dimensional segmentation: demographics × EV readiness, income, driving distance")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Analyst picks ──────────────────────────────────────────────────────────────
st.subheader("Analyst picks — the most revealing cross-cuts")

pick_tabs = st.tabs([
    "Housing × EV Readiness",
    "Income × Driving Distance",
    "Age × Charging Access",
    "Driving Distance × Powertrain",
    "Income × Likelihood to Switch",
    "Age × EV Readiness",
])

# 1. Housing type × EV Readiness (box plot)
with pick_tabs[0]:
    st.markdown("**Does housing type (house vs condo) predict EV readiness?**")
    st.caption("Home charging access is the single strongest predictor of EV readiness. Housing type is a proxy for that.")
    housing_map = {
        "house": "House", "condo": "Condo / Apartment",
        "townhouse": "Townhouse", "House": "House",
        "Condo": "Condo / Apartment", "Townhouse": "Townhouse",
    }
    df["housing_type"] = df["purchase_decision_role"].map(
        lambda x: "House" if pd.notna(x) and "house" in str(x).lower()
        else ("Condo" if pd.notna(x) and "condo" in str(x).lower() else None)
    )
    fig = go.Figure()
    colors_h = ["#2E86AB", "#A23B72", "#F18F01", "#6A994E"]
    for i, src in enumerate(df["data_source"].unique()):
        sub = df[df["data_source"] == src]["ev_readiness_index"].dropna()
        if sub.empty:
            continue
        fig.add_trace(go.Box(
            y=sub, name=src, marker_color=colors_h[i % len(colors_h)], boxmean=True,
        ))
    # Better: use charging convenience as proxy for housing
    charging_order = [
        "Very convenient — I can likely charge at home",
        "Somewhat convenient — condo/workplace/shared charging may be available",
        "Not very convenient — I would mostly depend on public charging",
        "Not convenient at all",
        "Not sure",
    ]
    fig2 = go.Figure()
    for i, chg in enumerate(charging_order):
        sub = df[df["charging_convenience"].astype(str).str.contains(
            chg[:25], case=False, na=False
        )]["ev_readiness_index"].dropna()
        if sub.empty:
            continue
        label = chg[:40] + ("…" if len(chg) > 40 else "")
        fig2.add_trace(go.Box(
            y=sub, name=label, marker_color=colors_h[i % len(colors_h)], boxmean=True,
        ))
    fig2.update_layout(**LAYOUT_BASE,
                       title="EV Readiness Index by charging convenience (proxy for housing/access)",
                       yaxis_title="EV Readiness (1–10)", height=440, xaxis_tickangle=-20)
    st.plotly_chart(fig2, use_container_width=True)
    grp = df.groupby(
        df["charging_convenience"].str[:40]
    )["ev_readiness_index"].agg(["mean", "median", "count"]).round(2)
    st.dataframe(grp, use_container_width=True)

# 2. Income × Driving distance
with pick_tabs[1]:
    st.markdown("**Do higher-income respondents drive more?**")
    st.caption("Longer daily distances raise charging anxiety — a key barrier to EV adoption.")
    fig = heatmap_pct(df, "monthly_income", "daily_driving_distance",
                      "Income × Daily driving distance (row %)",
                      row_order=income_order, col_order=dd_order, colorscale="YlOrRd")
    st.plotly_chart(fig, use_container_width=True)

# 3. Age × Charging access
with pick_tabs[2]:
    st.markdown("**Which age groups have the least charging access?**")
    st.caption("Younger segments (condo dwellers) may face more infrastructure barriers despite higher EV enthusiasm.")
    fig = heatmap_pct(df, "age_range", "charging_convenience",
                      "Age × Charging convenience (row %)",
                      row_order=age_order, colorscale="Blues")
    st.plotly_chart(fig, use_container_width=True)

# 4. Driving distance × Powertrain preference
with pick_tabs[3]:
    st.markdown("**Does how far you drive determine what powertrain you choose?**")
    st.caption("Higher-mileage drivers may favor PHEV/REEV over BEV due to range anxiety.")
    fig = stacked_bar_pct(df, "daily_driving_distance", "powertrain_short",
                          "Daily driving distance × Powertrain choice (row %)",
                          row_order=dd_order, col_order=PT_ORDER, color_map=POWERTRAIN_COLORS)
    st.plotly_chart(fig, use_container_width=True)

# 5. Income × Likelihood to switch to EV
with pick_tabs[4]:
    st.markdown("**Does income predict willingness to switch to EV in 3 years?**")
    st.caption("Higher income = earlier adopter, or does the affordability constraint disappear?")
    fig = heatmap_pct(df, "monthly_income", "likelihood_switch_ev_3y",
                      "Income × Likelihood to switch to EV in 3 years (row %)",
                      row_order=income_order, colorscale="Greens")
    st.plotly_chart(fig, use_container_width=True)

# 6. Age × EV Readiness (box)
with pick_tabs[5]:
    st.markdown("**Are younger respondents actually more EV-ready?**")
    st.caption("EV Readiness Index = composite of likelihood, charging access, and familiarity.")
    fig = go.Figure()
    colors_a = plc.qualitative.Set2
    for i, age in enumerate(age_order):
        sub = df[df["age_range"] == age]["ev_readiness_index"].dropna()
        if sub.empty:
            continue
        fig.add_trace(go.Box(
            y=sub, name=f"{age}<br>(n={len(sub)})",
            marker_color=colors_a[i % len(colors_a)], boxmean=True,
        ))
    fig.update_layout(**LAYOUT_BASE,
                      title="EV Readiness Index by age group",
                      yaxis_title="EV Readiness (1–10)", height=440)
    st.plotly_chart(fig, use_container_width=True)
    grp2 = df.groupby(df["age_range"].astype(str))["ev_readiness_index"].agg(["mean", "median", "count"]).round(2)
    st.dataframe(grp2, use_container_width=True)

st.divider()

# ── Custom explorer ────────────────────────────────────────────────────────────
st.subheader("Custom cross-tab explorer")
st.caption("Select any two variables to generate a heatmap. Row % normalisation applied.")

CROSS_OPTIONS = {
    "Age group": "age_range",
    "Monthly income": "monthly_income",
    "Gender": "gender",
    "Daily driving distance": "daily_driving_distance",
    "Data source": "data_source",
    "Powertrain choice": "powertrain_short",
    "Charging convenience": "charging_convenience",
    "Likelihood to switch to EV": "likelihood_switch_ev_3y",
    "Purchase factor (most important)": "purchase_factor_most_important",
}

col_x, col_y = st.columns(2)
row_var = col_x.selectbox("Row variable (Y axis)", list(CROSS_OPTIONS.keys()), index=0)
col_var = col_y.selectbox("Column variable (X axis)", list(CROSS_OPTIONS.keys()), index=5)

row_col = CROSS_OPTIONS[row_var]
col_col = CROSS_OPTIONS[col_var]

if row_col == col_col:
    st.warning("Please select two different variables.")
else:
    row_order_custom = (
        age_order if row_col == "age_range"
        else income_order if row_col == "monthly_income"
        else dd_order if row_col == "daily_driving_distance"
        else PT_ORDER if row_col == "powertrain_short"
        else None
    )
    col_order_custom = (
        age_order if col_col == "age_range"
        else income_order if col_col == "monthly_income"
        else dd_order if col_col == "daily_driving_distance"
        else PT_ORDER if col_col == "powertrain_short"
        else None
    )
    fig_custom = heatmap_pct(df, row_col, col_col,
                             f"{row_var} × {col_var} (row %)",
                             row_order=row_order_custom, col_order=col_order_custom,
                             colorscale="RdYlGn")
    st.plotly_chart(fig_custom, use_container_width=True)

    sub = df[[row_col, col_col]].dropna()
    ct_abs = pd.crosstab(sub[row_col], sub[col_col])
    if row_order_custom:
        ct_abs = ct_abs.reindex([r for r in row_order_custom if r in ct_abs.index])
    with st.expander("Raw counts table"):
        st.dataframe(ct_abs, use_container_width=True)
