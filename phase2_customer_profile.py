"""Phase 2 — Customer profile: demographic overview and household analysis."""
import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from survey_utils import (
    FONT_FAMILY, HH_PROXY_ORDER, thai_layout, barh_counts, count_bar,
    _hbar_trace, hh_vehicle_proxy,
)


def run_phase2(df_plot, AGE_ORDER_PLOT, INCOME_ORDER_PLOT, DD_ORDER_PLOT):
    count_bar(
        df_plot["data_source"],
        "Respondents by data source (three cohorts)",
        order=["general", "motor_show", "survey_china"],
    )

    fig_d = make_subplots(
        rows=2, cols=3,
        horizontal_spacing=0.08, vertical_spacing=0.18,
        specs=[
            [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "domain"}],
        ],
        subplot_titles=(
            "Respondents by location", "Respondents by age range", "Respondents by gender",
            "Respondents by occupation", "Respondents by monthly income", "Gender (share)",
        ),
    )
    demo = [
        (df_plot["location"], None),
        (df_plot["age_range"], AGE_ORDER_PLOT),
        (df_plot["gender"], None),
    ]
    for col_i, (ser, ord_) in enumerate(demo, start=1):
        d = ser.dropna()
        vc = d.value_counts()
        if ord_ is not None:
            ord_ = [o for o in ord_ if o in vc.index]
            vc = vc.reindex(ord_).fillna(0).astype(int)
        else:
            vc = vc.sort_values(ascending=True)
        fig_d.add_trace(_hbar_trace(vc, "Blues"), row=1, col=col_i)

    occ = df_plot["occupation"].dropna().value_counts().sort_values(ascending=True)
    fig_d.add_trace(_hbar_trace(occ, "Oranges"), row=2, col=1)

    inc = (
        df_plot["monthly_income"].dropna().value_counts()
        .reindex(INCOME_ORDER_PLOT).fillna(0).astype(int)
    )
    fig_d.add_trace(_hbar_trace(inc, "Purples"), row=2, col=2)

    g_vc = df_plot["gender"].dropna().value_counts()
    fig_d.add_trace(
        go.Pie(
            labels=[str(i) for i in g_vc.index],
            values=g_vc.values,
            textinfo="percent+label",
            textfont=dict(family=FONT_FAMILY, size=10),
            showlegend=False,
        ),
        row=2, col=3,
    )
    for c in range(1, 4):
        fig_d.update_xaxes(title_text="Count", row=1, col=c)
    for c in range(1, 3):
        fig_d.update_xaxes(title_text="Count", row=2, col=c)
    thai_layout(fig_d, height=950, width=1250)
    fig_d.show()

    fig_p = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Location (share)", "Age range (share)"),
    )
    for col_i, (ser, _ts, top_n) in enumerate(
        [
            (df_plot["location"], "loc", 7),
            (df_plot["age_range"], "age", len(AGE_ORDER_PLOT)),
        ],
        start=1,
    ):
        vc = ser.dropna().value_counts()
        if len(vc) > top_n:
            head = vc.head(top_n - 1)
            other = vc.iloc[top_n - 1:].sum()
            vc = pd.concat([head, pd.Series({"อื่นๆ": other})])
        fig_p.add_trace(
            go.Pie(
                labels=[str(i) for i in vc.index],
                values=vc.values,
                textinfo="percent+label",
                textfont=dict(family=FONT_FAMILY, size=9),
                showlegend=False,
            ),
            row=1, col=col_i,
        )
    thai_layout(fig_p, height=480, width=1100)
    fig_p.show()

    # Household size and cars owned
    fig_h = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Household size (parsed)", "Cars owned (parsed)"),
    )
    for col_i, col in enumerate(["household_size_n", "cars_owned_count_n"], start=1):
        s = df_plot[col].dropna()
        if s.empty:
            fig_h.add_annotation(
                text="No data", xref="x domain", yref="y domain",
                x=0.5, y=0.5, showarrow=False, row=1, col=col_i,
            )
        else:
            vc = s.astype(int).value_counts().sort_index()
            fig_h.add_trace(
                go.Bar(x=vc.index.astype(str), y=vc.values, showlegend=False),
                row=1, col=col_i,
            )
        fig_h.update_yaxes(title_text="Count", row=1, col=col_i)
    thai_layout(fig_h, height=400, width=950)
    fig_h.show()

    # Household vehicle proxy
    sub = df_plot.dropna(subset=["household_size_n", "cars_owned_count_n"]).copy()
    sub["hh_vehicle_proxy"] = sub.apply(hh_vehicle_proxy, axis=1)
    sub["hh_vehicle_proxy"] = pd.Categorical(
        sub["hh_vehicle_proxy"], categories=HH_PROXY_ORDER, ordered=True
    )
    n_all = len(sub)
    vc_all = sub["hh_vehicle_proxy"].value_counts().reindex(HH_PROXY_ORDER).fillna(0).astype(int)
    pct_all = (100 * vc_all / n_all).round(1)
    summary_all = pd.DataFrame({"count": vc_all, "pct_of_valid_rows": pct_all})
    print(f"Rows with valid household size and cars (n={n_all}):")
    print(summary_all.to_string())
    print()

    with_car = sub[sub["cars_owned_count_n"] > 0]
    n_car = len(with_car)
    if n_car:
        vc2 = with_car["hh_vehicle_proxy"].value_counts()
        two_cats = HH_PROXY_ORDER[1:]
        vc2b = vc2.reindex(two_cats).fillna(0).astype(int)
        pct2 = (100 * vc2b / n_car).round(1)
        summary_car = pd.DataFrame({"count": vc2b, "pct_of_households_with_ge_1_car": pct2})
        print(f"Among households with ≥1 car (n={n_car}) — structural sharing proxy:")
        print(summary_car.to_string())
        print()

    owners = sub[sub["cars_owned_count_n"] > 0].copy()
    owners["people_per_car"] = (
        pd.to_numeric(owners["household_size_n"], errors="coerce")
        / pd.to_numeric(owners["cars_owned_count_n"], errors="coerce")
    )
    ppc_vc = (
        owners["people_per_car"].round(1).value_counts().sort_index()
        if len(owners) else pd.Series(dtype=int)
    )
    ct = pd.crosstab(sub["household_size_n"], sub["cars_owned_count_n"], margins=False)

    fig_share = make_subplots(
        rows=2, cols=2, row_heights=[0.42, 0.58],
        vertical_spacing=0.14, horizontal_spacing=0.12,
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "heatmap", "colspan": 2}, None],
        ],
        subplot_titles=(
            "Household vehicle proxy (structural)",
            "People per car (≥1 car only)",
            "Household size × cars owned (counts, not row %)",
        ),
    )
    x_proxy = [str(x) for x in HH_PROXY_ORDER]
    y_proxy = [int(vc_all[k]) for k in HH_PROXY_ORDER]
    n_b = len(y_proxy)
    col_scale = [i / max(1, n_b - 1) for i in range(n_b)]
    bar_cols = plc.sample_colorscale("Blues", col_scale)
    fig_share.add_trace(
        go.Bar(x=x_proxy, y=y_proxy, marker=dict(color=bar_cols), showlegend=False),
        row=1, col=1,
    )
    if ppc_vc.empty:
        fig_share.add_annotation(
            text="No households with ≥1 car", xref="x2 domain", yref="y2 domain",
            x=0.5, y=0.5, showarrow=False, row=1, col=2,
        )
    else:
        x_ppc = [str(v) for v in ppc_vc.index]
        y_ppc = ppc_vc.values.astype(int)
        n_p = len(y_ppc)
        col_scale_p = [i / max(1, n_p - 1) for i in range(n_p)]
        bar_cols_p = plc.sample_colorscale("Viridis", col_scale_p)
        fig_share.add_trace(
            go.Bar(x=x_ppc, y=y_ppc, marker=dict(color=bar_cols_p), showlegend=False),
            row=1, col=2,
        )
    fig_share.add_trace(
        go.Heatmap(
            z=ct.values,
            x=[str(c) for c in ct.columns],
            y=[str(r) for r in ct.index],
            colorscale="Blues", showscale=True,
            hovertemplate="household_size=%{y}<br>cars_owned=%{x}<br>count=%{z}<extra></extra>",
        ),
        row=2, col=1,
    )
    fig_share.update_xaxes(title_text="", tickangle=-20, row=1, col=1)
    fig_share.update_yaxes(title_text="Count", row=1, col=1)
    fig_share.update_xaxes(title_text="People per car (1 d.p.)", row=1, col=2)
    fig_share.update_yaxes(title_text="Count", row=1, col=2)
    fig_share.update_xaxes(title_text="Cars owned", row=2, col=1)
    fig_share.update_yaxes(title_text="Household size", row=2, col=1)
    thai_layout(fig_share, height=800, width=1000)
    fig_share.show()

    # Daily driving distance
    count_bar(df_plot["daily_driving_distance"], "Average daily driving distance")

    exploded_pt = (
        df_plot["current_powertrains_owned"].dropna().str.split(";").explode().str.strip()
    )
    exploded_pt = exploded_pt[exploded_pt != ""]
    barh_counts(exploded_pt, "Current powertrains owned (multi-select, exploded)", figsize=(10, 8))

    _sub_dd = df_plot.dropna(subset=["daily_driving_distance", "age_range"])
    _seen_dd = _sub_dd["daily_driving_distance"].unique().tolist()
    _seen_dd_set = set(_seen_dd)
    DAILY_ORDER_PLOT = [d for d in DD_ORDER_PLOT if d in _seen_dd_set] + sorted(
        [x for x in _seen_dd if x not in DD_ORDER_PLOT], key=lambda z: str(z).lower()
    )
    ct_dd_age = pd.crosstab(_sub_dd["age_range"], _sub_dd["daily_driving_distance"])
    age_rows = [a for a in AGE_ORDER_PLOT if a in ct_dd_age.index]
    dd_cols = [d for d in DAILY_ORDER_PLOT if d in ct_dd_age.columns]
    ct_dd_age = ct_dd_age.reindex(index=age_rows, columns=dd_cols).fillna(0).astype(int)
    _row_sum = ct_dd_age.sum(axis=1)
    pct_dd_age = ct_dd_age.div(_row_sum.where(_row_sum != 0), axis=0).fillna(0) * 100

    if _sub_dd.empty or not age_rows or not dd_cols:
        print("No rows with both daily driving distance and age range to plot.")
    else:
        fig_dd_age = go.Figure()
        n_dd = max(1, len(dd_cols))
        y_labels = [str(a) for a in pct_dd_age.index]
        for i, dd in enumerate(dd_cols):
            c = plc.sample_colorscale("Plasma", [i / max(1, n_dd - 1)])[0]
            _xv = pct_dd_age[dd].values
            fig_dd_age.add_trace(
                go.Bar(
                    name=str(dd), x=_xv, y=y_labels, orientation="h",
                    marker_color=c,
                    text=[f"{v:.0f}%" if v >= 3 else "" for v in _xv],
                    textposition="inside", insidetextanchor="middle",
                    textfont=dict(size=11, color="white"),
                )
            )
        fig_dd_age.update_layout(
            title="Average daily driving distance by age range (100% stacked)",
            barmode="stack",
            xaxis_title="Share within age range (%)",
            yaxis_title="Age range",
            legend_title_text="Daily driving distance",
        )
        fig_dd_age.update_xaxes(range=[0, 100])
        fig_dd_age.update_yaxes(autorange="reversed")
        thai_layout(fig_dd_age, height=max(480, 44 * len(age_rows)), width=900)
        fig_dd_age.show()
