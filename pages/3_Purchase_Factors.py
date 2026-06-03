"""Page 3 — Purchase factors, barriers and information sources."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import (
    load_survey, sidebar_filters, hbar, heatmap_pct,
    explode_and_count, LAYOUT_BASE,
)
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Purchase Factors", layout="wide")
apply_byd_theme()
page_header("Purchase Factors, Barriers & Information Sources", "What drives buying decisions and where consumers research EVs")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Purchase factors ───────────────────────────────────────────────────────────
st.subheader("What drives the purchase decision?")
tab1, tab2 = st.tabs(["Top-3 factors (multi-select)", "Single most important"])

with tab1:
    vc = explode_and_count(df, "purchase_factors_top3", top_n=15)
    fig = go.Figure(go.Bar(
        x=vc.values[::-1], y=vc.index[::-1].tolist(),
        orientation="h", marker_color="#2E86AB",
        text=vc.values[::-1], textposition="outside",
    ))
    fig.update_layout(**LAYOUT_BASE, title="Purchase decision factors — top 3 selections (exploded)",
                      xaxis_title="Mentions", height=max(340, 40 * len(vc)))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = hbar(df["purchase_factor_most_important"],
               "Single most important purchase factor", color="Viridis")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Factors by demographic ─────────────────────────────────────────────────────
st.subheader("Purchase factor intensity by demographic")

col1, col2 = st.columns(2)
with col1:
    fig = heatmap_pct(df, "age_range", "purchase_factor_most_important",
                      "Most important factor × Age (row %)",
                      row_order=age_order, colorscale="Blues")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = heatmap_pct(df, "monthly_income", "purchase_factor_most_important",
                      "Most important factor × Income (row %)",
                      row_order=income_order, colorscale="Purples")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── EV adoption barriers ───────────────────────────────────────────────────────
st.subheader("EV adoption barriers")

tab_b1, tab_b2, tab_b3 = st.tabs(["Overall", "By age group", "By income"])

with tab_b1:
    vc_b = explode_and_count(df, "ev_adoption_barriers", top_n=15)
    fig_b = go.Figure(go.Bar(
        x=vc_b.values[::-1], y=vc_b.index[::-1].tolist(),
        orientation="h", marker_color="#BC4749",
        text=vc_b.values[::-1], textposition="outside",
    ))
    fig_b.update_layout(**LAYOUT_BASE, title="EV adoption barriers (multi-select, exploded)",
                        xaxis_title="Mentions", height=max(340, 40 * len(vc_b)))
    st.plotly_chart(fig_b, use_container_width=True)

with tab_b2:
    import pandas as pd
    from survey_utils import explode_multiselect

    long_b = explode_multiselect(df, "ev_adoption_barriers")
    long_b = long_b.join(df[["age_range"]], on="row").dropna(subset=["age_range", "value"])
    rows = []
    for age in age_order:
        sub = long_b[long_b["age_range"] == age]
        if sub.empty:
            continue
        top = sub["value"].value_counts().head(5)
        tot = top.sum()
        for b, cnt in top.items():
            rows.append({"age_range": str(age), "barrier": b, "share": cnt / tot if tot else 0})
    if rows:
        stack_df = pd.DataFrame(rows)
        pivot = stack_df.pivot_table(index="age_range", columns="barrier", values="share",
                                     fill_value=0, aggfunc="sum")
        pivot = pivot.reindex([str(a) for a in age_order if str(a) in pivot.index])
        fig_ba = go.Figure()
        import plotly.colors as plc
        colors = plc.qualitative.Set2
        for i, barrier in enumerate(pivot.columns):
            fig_ba.add_trace(go.Bar(
                name=barrier, x=pivot.index.tolist(), y=pivot[barrier].values,
                marker_color=colors[i % len(colors)],
            ))
        fig_ba.update_layout(**LAYOUT_BASE, barmode="stack",
                             title="Top-5 barriers per age group (share among top mentions)",
                             yaxis_title="Share", height=420,
                             legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig_ba, use_container_width=True)

with tab_b3:
    fig = heatmap_pct(df, "monthly_income", "ev_adoption_barriers",
                      "Note: barrier column uses first value only — use Overall tab for full picture",
                      row_order=income_order, colorscale="Reds")
    # Better: show barrier frequency within income band using explode
    long_bi = explode_multiselect(df, "ev_adoption_barriers")
    long_bi = long_bi.join(df[["monthly_income"]], on="row").dropna(subset=["monthly_income", "value"])
    rows_i = []
    for inc in income_order:
        sub = long_bi[long_bi["monthly_income"] == inc]
        if sub.empty:
            continue
        top = sub["value"].value_counts().head(5)
        tot = top.sum()
        for b, cnt in top.items():
            rows_i.append({"income": str(inc), "barrier": b, "share": cnt / tot if tot else 0})
    if rows_i:
        import plotly.colors as plc
        stack_i = pd.DataFrame(rows_i)
        pivot_i = stack_i.pivot_table(index="income", columns="barrier", values="share",
                                      fill_value=0, aggfunc="sum")
        pivot_i = pivot_i.reindex([str(i) for i in income_order if str(i) in pivot_i.index])
        fig_bi = go.Figure()
        colors2 = plc.qualitative.Pastel
        for j, barrier in enumerate(pivot_i.columns):
            fig_bi.add_trace(go.Bar(
                name=barrier, x=pivot_i.index.tolist(), y=pivot_i[barrier].values,
                marker_color=colors2[j % len(colors2)],
            ))
        fig_bi.update_layout(**LAYOUT_BASE, barmode="stack",
                             title="Top-5 barriers per income band",
                             yaxis_title="Share", height=440, xaxis_tickangle=-30,
                             legend=dict(orientation="h", y=-0.4))
        st.plotly_chart(fig_bi, use_container_width=True)

st.divider()

# ── Information sources ────────────────────────────────────────────────────────
st.subheader("Information sources used in purchase research")

vc_info = explode_and_count(df, "info_sources", top_n=15)
fig_info = go.Figure(go.Bar(
    x=vc_info.values[::-1], y=vc_info.index[::-1].tolist(),
    orientation="h", marker_color="#52B788",
    text=vc_info.values[::-1], textposition="outside",
))
fig_info.update_layout(**LAYOUT_BASE, title="Information sources (multi-select, exploded)",
                       xaxis_title="Mentions", height=max(300, 40 * len(vc_info)))
st.plotly_chart(fig_info, use_container_width=True)

# Info sources by age
fig_info_age = heatmap_pct(df, "age_range", "info_sources",
                           "Note: heatmap uses first listed source — see overall chart for full picture",
                           row_order=age_order, colorscale="Teal")
# Better display: grouped bar
long_info = explode_multiselect(df, "info_sources")
long_info = long_info.join(df[["age_range"]], on="row").dropna()
top_sources = vc_info.head(8).index.tolist()
long_info_top = long_info[long_info["value"].isin(top_sources)]
rows_inf = []
for age in age_order:
    sub = long_info_top[long_info_top["age_range"] == age]
    n_age = (df["age_range"] == age).sum()
    if sub.empty or n_age == 0:
        continue
    for src in top_sources:
        cnt = (sub["value"] == src).sum()
        rows_inf.append({"age": str(age), "source": src, "pct": cnt / n_age * 100})
if rows_inf:
    inf_df = pd.DataFrame(rows_inf)
    import plotly.colors as plc
    colors3 = plc.qualitative.Set3
    fig_inf2 = go.Figure()
    for k, src in enumerate(top_sources):
        sub_s = inf_df[inf_df["source"] == src]
        fig_inf2.add_trace(go.Bar(
            name=src, x=sub_s["age"].tolist(), y=sub_s["pct"].tolist(),
            marker_color=colors3[k % len(colors3)],
        ))
    fig_inf2.update_layout(**LAYOUT_BASE, barmode="group",
                           title="Top information sources by age group (% within age group)",
                           yaxis_title="% of respondents in group", height=420,
                           legend=dict(orientation="h", y=-0.35))
    st.plotly_chart(fig_inf2, use_container_width=True)
