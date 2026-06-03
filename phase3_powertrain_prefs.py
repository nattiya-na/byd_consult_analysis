"""Phase 3 — Powertrain preferences by age and income."""
import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from survey_utils import (
    thai_layout, barh_counts, heatmap_crosstab, split_brand_segments,
)


def run_phase3(df_plot, AGE_ORDER_PLOT, INCOME_ORDER_PLOT):
    cons_exploded = (
        df_plot["powertrain_considering"].dropna().str.split(";").explode().str.strip()
    )
    cons_exploded = cons_exploded[cons_exploded != ""]
    barh_counts(cons_exploded, "Powertrains under consideration (exploded)", figsize=(10, 7))
    barh_counts(
        df_plot["powertrain_choose_today"],
        "Powertrain most likely if choosing today",
        figsize=(10, 7),
    )

    heatmap_crosstab(
        df_plot, "age_range", "powertrain_choose_today",
        "Age range vs powertrain if choosing today (row %)",
        colorscale="Blues",
    )

    tmp = df_plot[["age_range", "powertrain_considering"]].dropna()
    rows = []
    for _, r in tmp.iterrows():
        for p in str(r["powertrain_considering"]).split(";"):
            p = p.strip()
            if p:
                rows.append({"age_range": r["age_range"], "powertrain": p})
    long_age = pd.DataFrame(rows)
    if not long_age.empty:
        ct2 = pd.crosstab(long_age["age_range"], long_age["powertrain"], normalize="index")
        z2 = ct2.values.astype(float)
        text2 = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in r] for r in z2]
        fig2 = go.Figure(
            data=go.Heatmap(
                z=z2,
                x=[str(c) for c in ct2.columns],
                y=[str(i) for i in ct2.index],
                text=text2, texttemplate="%{text}",
                colorscale="Greens", colorbar=dict(title="Share"),
                hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig2.update_layout(
            title="Age range vs powertrain under consideration (exploded, row %)",
            xaxis_title="Powertrain", yaxis_title="Age range",
        )
        fig2.update_xaxes(tickangle=-45)
        thai_layout(fig2, height=520, width=1100)
        fig2.show()

    # Brands considering by age (exploded)
    BR_TOP_N = 20
    rows_br_age = []
    for _, r in df_plot.dropna(subset=["age_range", "brands_considering"]).iterrows():
        for seg in split_brand_segments(r["brands_considering"]):
            if seg:
                rows_br_age.append({"age_range": r["age_range"], "brand": seg})
    long_br_age = pd.DataFrame(rows_br_age)
    if long_br_age.empty:
        print("No rows with both age range and brands considering to plot.")
    else:
        ct_br_age = pd.crosstab(long_br_age["age_range"], long_br_age["brand"], normalize="index")
        mention_totals = long_br_age["brand"].value_counts()
        top_brands = mention_totals.head(BR_TOP_N).index.tolist()

        vc_br_all = mention_totals.head(min(30, len(mention_totals)))
        y_br_all = [str(s) for s in vc_br_all.index[::-1]]
        x_br_all = vc_br_all.values[::-1]
        n_br_all = len(x_br_all)
        sc_br_all = [j / max(1, n_br_all - 1) for j in range(n_br_all)]
        col_br_all = plc.sample_colorscale("Teal", sc_br_all)
        fig_br_all = go.Figure(
            data=go.Bar(
                x=x_br_all, y=y_br_all, orientation="h",
                marker=dict(color=col_br_all), showlegend=False,
            )
        )
        fig_br_all.update_layout(
            title="Brands under consideration (exploded list, overall mention counts)",
            xaxis_title="Mentions", yaxis_title="Brand segment",
        )
        thai_layout(fig_br_all, height=max(400, 100 + 28 * n_br_all), width=920)
        fig_br_all.show()

        ct_br_age = ct_br_age.reindex(columns=top_brands, fill_value=0)
        age_rows_br = [a for a in AGE_ORDER_PLOT if a in ct_br_age.index]
        if not age_rows_br:
            print("No overlapping age bands for brand mentions heatmap.")
        else:
            ct_br_age = ct_br_age.reindex(index=age_rows_br)
            z_br_age = ct_br_age.values.astype(float)
            text_br_age = [
                [f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_br_age
            ]
            fig_br_age = go.Figure(
                data=go.Heatmap(
                    z=z_br_age,
                    x=[str(c) for c in ct_br_age.columns],
                    y=[str(i) for i in ct_br_age.index],
                    text=text_br_age, texttemplate="%{text}",
                    colorscale="Teal", colorbar=dict(title="Share"),
                    hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
                )
            )
            fig_br_age.update_layout(
                title="Age range vs brand mentions (exploded multi-select list, row %)",
                xaxis_title="Brand segment", yaxis_title="Age range",
            )
            fig_br_age.update_xaxes(tickangle=-45)
            thai_layout(fig_br_age, height=520, width=max(1100, 40 + 14 * ct_br_age.shape[1]))
            fig_br_age.show()

            TOP_BR_PER_AGE = 8
            n_age_bar = len(age_rows_br)
            v_sp = min(0.14, 0.55 / max(n_age_bar, 1))
            fig_br_h = make_subplots(
                rows=n_age_bar, cols=1,
                subplot_titles=[f"Top brands — {a}" for a in age_rows_br],
                vertical_spacing=v_sp,
            )
            h_per = max(220, min(400, 72 + 24 * TOP_BR_PER_AGE))
            for ri, age in enumerate(age_rows_br, start=1):
                vc_b = (
                    long_br_age.loc[long_br_age["age_range"] == age, "brand"]
                    .value_counts().head(TOP_BR_PER_AGE)
                )
                if vc_b.empty:
                    continue
                y_b = [str(s) for s in vc_b.index[::-1]]
                x_b = vc_b.values[::-1]
                nb = len(x_b)
                sc_b = [j / max(1, nb - 1) for j in range(nb)]
                col_b = plc.sample_colorscale("Teal", sc_b)
                fig_br_h.add_trace(
                    go.Bar(x=x_b, y=y_b, orientation="h", marker=dict(color=col_b), showlegend=False),
                    row=ri, col=1,
                )
            fig_br_h.update_layout(
                title_text="Top brands by age group (mention counts, exploded list)",
                showlegend=False, height=min(2200, 100 + n_age_bar * h_per),
            )
            fig_br_h.update_xaxes(title_text="Mentions")
            thai_layout(fig_br_h, width=920)
            fig_br_h.show()

    heatmap_crosstab(
        df_plot, "monthly_income", "powertrain_choose_today",
        "Monthly income vs powertrain if choosing today (row %)",
        colorscale="Blues",
    )

    # Monthly income vs brands considering
    rows_br_inc = []
    for _, r in df_plot.dropna(subset=["monthly_income", "brands_considering"]).iterrows():
        for seg in split_brand_segments(r["brands_considering"]):
            if seg:
                rows_br_inc.append({"monthly_income": r["monthly_income"], "brand": seg})
    long_br_inc = pd.DataFrame(rows_br_inc)
    if long_br_inc.empty:
        print("No rows with both monthly income and brands considering to plot.")
    else:
        ct_br_inc = pd.crosstab(
            long_br_inc["monthly_income"], long_br_inc["brand"], normalize="index"
        )
        mention_totals_inc = long_br_inc["brand"].value_counts()
        top_brands_inc = mention_totals_inc.head(BR_TOP_N).index.tolist()
        ct_br_inc = ct_br_inc.reindex(columns=top_brands_inc, fill_value=0)
        income_rows_br = [x for x in INCOME_ORDER_PLOT if x in ct_br_inc.index]
        if not income_rows_br:
            print("No overlapping income bands for brand mentions heatmap.")
        else:
            ct_br_inc = ct_br_inc.reindex(index=income_rows_br)
            z_br_inc = ct_br_inc.values.astype(float)
            text_br_inc = [
                [f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_br_inc
            ]
            fig_br_inc = go.Figure(
                data=go.Heatmap(
                    z=z_br_inc,
                    x=[str(c) for c in ct_br_inc.columns],
                    y=[str(i) for i in ct_br_inc.index],
                    text=text_br_inc, texttemplate="%{text}",
                    colorscale="Teal", colorbar=dict(title="Share"),
                    hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
                )
            )
            fig_br_inc.update_layout(
                title="Monthly income vs brand mentions (exploded multi-select list, row %)",
                xaxis_title="Brand segment", yaxis_title="Monthly income",
            )
            fig_br_inc.update_xaxes(tickangle=-45)
            thai_layout(fig_br_inc, height=520, width=max(1100, 40 + 14 * ct_br_inc.shape[1]))
            fig_br_inc.show()

            TOP_BR_PER_INC = 8
            n_inc_bar = len(income_rows_br)
            v_sp_inc = min(0.14, 0.55 / max(n_inc_bar, 1))
            fig_br_inc_h = make_subplots(
                rows=n_inc_bar, cols=1,
                subplot_titles=[f"Top brands — {a}" for a in income_rows_br],
                vertical_spacing=v_sp_inc,
            )
            h_per_inc = max(220, min(400, 72 + 24 * TOP_BR_PER_INC))
            for ri, inc in enumerate(income_rows_br, start=1):
                vc_b = (
                    long_br_inc.loc[long_br_inc["monthly_income"] == inc, "brand"]
                    .value_counts().head(TOP_BR_PER_INC)
                )
                if vc_b.empty:
                    continue
                y_b = [str(s) for s in vc_b.index[::-1]]
                x_b = vc_b.values[::-1]
                nb = len(x_b)
                sc_b = [j / max(1, nb - 1) for j in range(nb)]
                col_b = plc.sample_colorscale("Teal", sc_b)
                fig_br_inc_h.add_trace(
                    go.Bar(x=x_b, y=y_b, orientation="h", marker=dict(color=col_b), showlegend=False),
                    row=ri, col=1,
                )
            fig_br_inc_h.update_layout(
                title_text="Top brands by income band (mention counts, exploded list)",
                showlegend=False, height=min(2200, 100 + n_inc_bar * h_per_inc),
            )
            fig_br_inc_h.update_xaxes(title_text="Mentions")
            thai_layout(fig_br_inc_h, width=920)
            fig_br_inc_h.show()

    # Age vs single most important purchase factor + barriers
    heatmap_crosstab(
        df_plot, "age_range", "purchase_factor_most_important",
        "Age range vs single most important purchase factor (row %)",
        colorscale="Purples",
    )

    tmp_b = df_plot[["age_range", "ev_adoption_barriers"]].dropna()
    rows_b = []
    for _, r in tmp_b.iterrows():
        for b in str(r["ev_adoption_barriers"]).split(";"):
            b = b.strip()
            if b:
                rows_b.append({"age_range": r["age_range"], "barrier": b})
    long_bar = pd.DataFrame(rows_b)
    if not long_bar.empty:
        ct_b = pd.crosstab(long_bar["age_range"], long_bar["barrier"], normalize="index")
        z_b = ct_b.values.astype(float)
        text_b = [
            [f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in row] for row in z_b
        ]
        fig_b = go.Figure(
            data=go.Heatmap(
                z=z_b,
                x=[str(c) for c in ct_b.columns],
                y=[str(i) for i in ct_b.index],
                text=text_b, texttemplate="%{text}",
                colorscale="Oranges", colorbar=dict(title="Share"),
                hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
            )
        )
        fig_b.update_layout(
            title="Age range vs EV adoption barriers (exploded, row %)",
            xaxis_title="Barrier", yaxis_title="Age range",
        )
        fig_b.update_xaxes(tickangle=-45)
        thai_layout(fig_b, height=520, width=1100)
        fig_b.show()
