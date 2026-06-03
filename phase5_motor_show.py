"""Phase 5 — Motor show respondent analysis."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from survey_utils import (
    STAGE_ORDER, thai_layout, count_bar, heatmap_crosstab,
    grouped_count_bar, split_brand_segments,
)


def run_phase5(df_plot, AGE_ORDER_PLOT, INCOME_ORDER_PLOT):
    df_ms = df_plot[df_plot["data_source"] == "motor_show"].copy()
    print(f"Motor show respondents (cleaned rows): {len(df_ms)}")

    _seen_ps = df_ms["purchase_stage"].dropna().unique().tolist()
    PURCHASE_STAGE_ORDER = [x for x in STAGE_ORDER if x in _seen_ps] + [
        x for x in _seen_ps if x not in STAGE_ORDER
    ]

    count_bar(
        df_ms["purchase_stage"],
        "Motor show — purchase stage (readiness to buy)",
        order=PURCHASE_STAGE_ORDER if PURCHASE_STAGE_ORDER else None,
    )

    heatmap_crosstab(
        df_ms, "purchase_stage", "powertrain_choose_today",
        "Motor show — purchase stage vs powertrain if choosing today (row %)",
        colorscale="Blues",
    )

    # Exploded powertrains under consideration × purchase stage
    tmp_ms = df_ms[["purchase_stage", "powertrain_considering"]].dropna()
    rows_pt = []
    for _, r in tmp_ms.iterrows():
        for p in str(r["powertrain_considering"]).split(";"):
            p = p.strip()
            if p:
                rows_pt.append({"purchase_stage": r["purchase_stage"], "powertrain": p})
    long_pt = pd.DataFrame(rows_pt)
    if not long_pt.empty:
        ct_pt = pd.crosstab(long_pt["purchase_stage"], long_pt["powertrain"], normalize="index")
        z_pt = ct_pt.values.astype(float)
        text_pt = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_pt]
        fig_pt = go.Figure(
            data=go.Heatmap(
                z=z_pt,
                x=[str(c) for c in ct_pt.columns],
                y=[str(i) for i in ct_pt.index],
                text=text_pt, texttemplate="%{text}",
                colorscale="Greens", colorbar=dict(title="Share"),
                hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_pt.update_layout(
            title="Motor show — purchase stage vs powertrain under consideration (exploded, row %)",
            xaxis_title="Powertrain", yaxis_title="Purchase stage",
        )
        fig_pt.update_xaxes(tickangle=-45)
        thai_layout(fig_pt, height=520, width=1100)
        fig_pt.show()

    heatmap_crosstab(
        df_ms, "purchase_stage", "byd_view_factor",
        "Motor show — purchase stage vs main factor shaping BYD view (row %)",
        colorscale="Purples",
    )

    # EV barriers × purchase stage
    tmp_b_ms = df_ms[["purchase_stage", "ev_adoption_barriers"]].dropna()
    rows_b = []
    for _, r in tmp_b_ms.iterrows():
        for b in str(r["ev_adoption_barriers"]).split(";"):
            b = b.strip()
            if b:
                rows_b.append({"purchase_stage": r["purchase_stage"], "barrier": b})
    long_b_ms = pd.DataFrame(rows_b)
    if not long_b_ms.empty:
        ct_b = pd.crosstab(long_b_ms["purchase_stage"], long_b_ms["barrier"], normalize="index")
        z_b = ct_b.values.astype(float)
        text_b = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_b]
        fig_b_ms = go.Figure(
            data=go.Heatmap(
                z=z_b,
                x=[str(c) for c in ct_b.columns],
                y=[str(i) for i in ct_b.index],
                text=text_b, texttemplate="%{text}",
                colorscale="Oranges", colorbar=dict(title="Share"),
                hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_b_ms.update_layout(
            title="Motor show — purchase stage vs EV adoption barriers (exploded, row %)",
            xaxis_title="Barrier", yaxis_title="Purchase stage",
        )
        fig_b_ms.update_xaxes(tickangle=-45)
        thai_layout(fig_b_ms, height=520, width=1100)
        fig_b_ms.show()

    # Brands × purchase stage
    rows_br = []
    for _, r in df_ms.dropna(subset=["purchase_stage", "brands_considering"]).iterrows():
        for seg in split_brand_segments(r["brands_considering"]):
            if seg:
                rows_br.append({"purchase_stage": r["purchase_stage"], "brand": seg})
    long_br = pd.DataFrame(rows_br)
    if not long_br.empty:
        ct_br = pd.crosstab(long_br["purchase_stage"], long_br["brand"], normalize="index")
        z_br = ct_br.values.astype(float)
        text_br = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_br]
        fig_br = go.Figure(
            data=go.Heatmap(
                z=z_br,
                x=[str(c) for c in ct_br.columns],
                y=[str(i) for i in ct_br.index],
                text=text_br, texttemplate="%{text}",
                colorscale="Teal", colorbar=dict(title="Share"),
                hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_br.update_layout(
            title="Motor show — purchase stage vs brand mentions (exploded multi-select list, row %)",
            xaxis_title="Brand segment", yaxis_title="Purchase stage",
        )
        fig_br.update_xaxes(tickangle=-45)
        thai_layout(fig_br, height=520, width=max(1100, 40 + 14 * ct_br.shape[1]))
        fig_br.show()

    # Cohort comparisons
    grouped_count_bar(df_plot, "age_range", "Age range — by cohort", AGE_ORDER_PLOT)
    grouped_count_bar(df_plot, "gender", "Gender — by cohort")
    grouped_count_bar(df_plot, "location", "Location — by cohort")
    grouped_count_bar(df_plot, "monthly_income", "Monthly income — by cohort", INCOME_ORDER_PLOT)

    byd_flag = (
        df_plot["brands_considering"].fillna("")
        .str.contains(r"\bBYD\b", case=False, regex=True)
    )
    tmp_k = pd.DataFrame({"data_source": df_plot["data_source"], "mentions_byd": byd_flag})
    share_byd = tmp_k.groupby("data_source")["mentions_byd"].mean() * 100

    fig_k = go.Figure(
        go.Bar(
            x=[str(i) for i in share_byd.index],
            y=share_byd.values,
            marker=dict(color=["#636EFA", "#EF553B", "#00cc96"]),
        )
    )
    fig_k.update_layout(
        title="Share of respondents mentioning BYD in brand list (%) — by cohort",
        yaxis_title="% of cohort", xaxis_title="Cohort",
    )
    thai_layout(fig_k, height=400, width=600)
    fig_k.show()

    grouped_count_bar(
        df_plot, "likelihood_switch_ev_3y",
        "Likelihood to switch to an electrified vehicle in 3 years — by cohort",
    )

    # Purchase factors by cohort
    rows_pf = []
    for _, r in df_plot.dropna(subset=["purchase_factors_top3"]).iterrows():
        for p in str(r["purchase_factors_top3"]).split(";"):
            p = p.strip()
            if p:
                rows_pf.append({"data_source": r["data_source"], "factor": p})
    long_pf = pd.DataFrame(rows_pf)
    if not long_pf.empty:
        ct_pf = pd.crosstab(long_pf["factor"], long_pf["data_source"], normalize="columns")
        z_pf = ct_pf.values.astype(float)
        text_pf = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_pf]
        fig_pf = go.Figure(
            data=go.Heatmap(
                z=z_pf,
                x=[str(c) for c in ct_pf.columns],
                y=[str(i) for i in ct_pf.index],
                text=text_pf, texttemplate="%{text}",
                colorscale="Blues", colorbar=dict(title="Share of cohort"),
                hovertemplate="factor=%{y}<br>cohort=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_pf.update_layout(
            title="Purchase factors (top-3 selections, exploded) — share within each cohort (column %)",
            xaxis_title="Cohort", yaxis_title="Factor",
        )
        thai_layout(fig_pf, height=max(400, 40 + 18 * len(ct_pf.index)), width=700)
        fig_pf.show()

    # EV barriers by cohort
    rows_evb = []
    for _, r in df_plot.dropna(subset=["ev_adoption_barriers"]).iterrows():
        for b in str(r["ev_adoption_barriers"]).split(";"):
            b = b.strip()
            if b:
                rows_evb.append({"data_source": r["data_source"], "barrier": b})
    long_evb = pd.DataFrame(rows_evb)
    if not long_evb.empty:
        ct_evb = pd.crosstab(long_evb["barrier"], long_evb["data_source"], normalize="columns")
        z_evb = ct_evb.values.astype(float)
        text_evb = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_evb]
        fig_evb = go.Figure(
            data=go.Heatmap(
                z=z_evb,
                x=[str(c) for c in ct_evb.columns],
                y=[str(i) for i in ct_evb.index],
                text=text_evb, texttemplate="%{text}",
                colorscale="Oranges", colorbar=dict(title="Share of cohort"),
                hovertemplate="barrier=%{y}<br>cohort=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_evb.update_layout(
            title="EV adoption barriers (exploded) — share within each cohort (column %)",
            xaxis_title="Cohort", yaxis_title="Barrier",
        )
        thai_layout(fig_evb, height=max(450, 40 + 16 * len(ct_evb.index)), width=700)
        fig_evb.show()
