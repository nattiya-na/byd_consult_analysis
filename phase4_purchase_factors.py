"""Phase 4 — Purchase factors, barriers, BYD positioning, and information sources."""
import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from survey_utils import thai_layout, barh_counts, split_multiselect


def run_phase4(df_plot):
    pf = (
        df_plot["purchase_factors_top3"].dropna().str.split(";").explode().str.strip()
    )
    pf = pf[pf != ""]
    barh_counts(pf, "Purchase decision factors (top 3 selections, exploded)", figsize=(10, 8))
    barh_counts(
        df_plot["purchase_factor_most_important"],
        "Single most important purchase factor",
        figsize=(10, 7),
    )

    # EV adoption barriers
    barriers = (
        df_plot["ev_adoption_barriers"].dropna().str.split(";").explode().str.strip()
    )
    barriers = barriers[barriers != ""]
    vc = barriers.value_counts().sort_values()
    height = max(400, min(1200, 80 + 22 * len(vc)))
    fig_b = go.Figure(
        go.Bar(
            x=vc.values, y=[str(i) for i in vc.index],
            orientation="h", marker=dict(color="steelblue"), showlegend=False,
        )
    )
    fig_b.update_layout(
        title="Barriers to electrified vehicle adoption (exploded multi-select)",
        xaxis_title="Count", yaxis_title="",
    )
    thai_layout(fig_b, height=height, width=800)
    fig_b.show()

    # BYD considering / not considering reasons
    reason_pos = df_plot["byd_considering_reason"].dropna()
    reason_pos = reason_pos[
        ~reason_pos.str.contains(
            r"Not considering BYD|ไม่ได้เลือก\s*BYD", case=False, na=False, regex=True
        )
    ]
    reason_neg = df_plot["byd_not_considering_reason"].dropna()
    reason_neg = reason_neg[
        ~reason_neg.str.contains(
            r"Considering BYD|พิจารณา\s*BYD", case=False, na=False, regex=True
        )
    ]

    fig_byd = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.14,
        subplot_titles=(
            "Reasons for considering BYD (conditional)",
            "Reasons for NOT considering BYD (conditional)",
        ),
    )
    for col_i, series in enumerate([reason_pos, reason_neg], start=1):
        vc = series.value_counts().head(12).sort_values()
        if vc.empty:
            fig_byd.add_annotation(
                text="No data", xref="x domain", yref="y domain",
                x=0.5, y=0.5, showarrow=False, row=1, col=col_i,
            )
        else:
            fig_byd.add_trace(
                go.Bar(
                    x=vc.values, y=[str(i) for i in vc.index],
                    orientation="h", marker=dict(color="teal"), showlegend=False,
                ),
                row=1, col=col_i,
            )
        fig_byd.update_xaxes(title_text="Count", row=1, col=col_i)
    thai_layout(fig_byd, height=520, width=1200)
    fig_byd.show()

    df_plot["mentions_byd_in_brands"] = (
        df_plot["brands_considering"].fillna("")
        .str.contains(r"\bBYD\b", case=False, regex=True)
    )
    print("Rows mentioning BYD in brand list:", int(df_plot["mentions_byd_in_brands"].sum()))

    # Information sources
    info = (
        df_plot["info_sources"].dropna().str.split(";").explode().str.strip()
    )
    info = info[info != ""]
    barh_counts(info, "Information sources when researching cars (exploded)", figsize=(10, 6))


def run_phase4b(df_plot):
    """Self-explicated feature importance derived from top-3 order + most important."""
    MI_BONUS = 5.0
    RANK_WEIGHTS = (3.0, 2.0, 1.0)

    def _raw_importance_row(row):
        mi = row.get("purchase_factor_most_important")
        if pd.isna(mi) or str(mi).strip() == "":
            return None
        mi = str(mi).strip()
        tokens = split_multiselect(row.get("purchase_factors_top3"))[:3]
        scores = {}
        for i, tok in enumerate(tokens):
            if not tok:
                continue
            scores[tok] = scores.get(tok, 0.0) + RANK_WEIGHTS[i]
        scores[mi] = scores.get(mi, 0.0) + MI_BONUS
        total = sum(scores.values())
        if total <= 0:
            return None
        return {k: (v / total) * 100.0 for k, v in scores.items()}

    _rows = []
    _idx = []
    for i, row in df_plot.iterrows():
        d = _raw_importance_row(row)
        if d is None:
            continue
        _rows.append(d)
        _idx.append(i)

    if not _rows:
        raise RuntimeError(
            "Phase 4b: no respondents with non-empty importance weights. "
            "Check purchase_factor_most_important / purchase_factors_top3."
        )

    se_wide = pd.DataFrame(_rows, index=_idx).fillna(0.0)
    n_se = len(se_wide)
    print(f"Phase 4b: n = {n_se} respondents (non-null most important + positive weight).")
    print(
        f"Check: per-respondent sums → min {se_wide.sum(axis=1).min():.4f}, "
        f"max {se_wide.sum(axis=1).max():.4f}"
    )

    mean_imp = se_wide.mean().sort_values(ascending=False)
    std_imp = se_wide.std()
    summary = (
        pd.DataFrame({"mean_pct": mean_imp, "std_pct": std_imp.reindex(mean_imp.index)})
        .round(2).rename_axis("factor")
    )
    print(summary.to_string())

    if "data_source" in df_plot.columns:
        ds_tbl = se_wide.join(df_plot["data_source"], how="left").groupby("data_source").mean().T
        ds_tbl = ds_tbl.round(2).sort_index()
        print("\nMean importance by data source:")
        print(ds_tbl.to_string())

    mean_for_plot = mean_imp.sort_values(ascending=True)
    _y = [str(i) for i in mean_for_plot.index]
    _x = mean_for_plot.values
    _n = len(_x)
    _scale = [i / max(1, _n - 1) for i in range(_n)]
    _colors = plc.sample_colorscale("Viridis", _scale)
    fig = go.Figure(
        go.Bar(x=_x, y=_y, orientation="h", marker=dict(color=_colors), showlegend=False)
    )
    fig.update_layout(
        title=(
            f"Self-explicated mean importance (%) — top-3 ranks 3/2/1 + "
            f"{MI_BONUS:g} to most important (n={n_se})"
        ),
        xaxis_title="Mean importance (%)", yaxis_title="",
    )
    thai_layout(fig, height=max(360, min(1200, 80 + 22 * max(1, _n))), width=800)
    fig.show()
