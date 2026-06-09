"""Phase 4 — Purchase factors, barriers, BYD positioning, and information sources."""
import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from survey_utils import thai_layout, barh_counts, split_multiselect

_MI_BONUS = 5.0
_RANK_WEIGHTS = (3.0, 2.0, 1.0)


def _importance_weights(df_plot: pd.DataFrame) -> pd.DataFrame:
    """Per-respondent self-explicated importance (%).

    Returns a wide DataFrame — rows = valid respondents (original index),
    columns = factor labels, values = normalised importance %.
    """
    rows, idx = [], []
    for i, row in df_plot.iterrows():
        mi = row.get("purchase_factor_most_important")
        if pd.isna(mi) or str(mi).strip() == "":
            continue
        mi = str(mi).strip()
        tokens = split_multiselect(row.get("purchase_factors_top3"))[:3]
        scores: dict[str, float] = {}
        for j, tok in enumerate(tokens):
            if tok:
                scores[tok] = scores.get(tok, 0.0) + _RANK_WEIGHTS[j]
        scores[mi] = scores.get(mi, 0.0) + _MI_BONUS
        total = sum(scores.values())
        if total <= 0:
            continue
        rows.append({k: (v / total) * 100.0 for k, v in scores.items()})
        idx.append(i)
    return pd.DataFrame(rows, index=idx).fillna(0.0)


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
    se_wide = _importance_weights(df_plot)
    if se_wide.empty:
        raise RuntimeError(
            "Phase 4b: no respondents with non-empty importance weights. "
            "Check purchase_factor_most_important / purchase_factors_top3."
        )
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
            f"{_MI_BONUS:g} to most important (n={n_se})"
        ),
        xaxis_title="Mean importance (%)", yaxis_title="",
    )
    thai_layout(fig, height=max(360, min(1200, 80 + 22 * max(1, _n))), width=800)
    fig.show()


def run_phase4c(df_plot, age_order):
    """Purchase factor importance cross-tabulated by age group.

    Chart 1: heatmap — mean importance (%) per age × factor cell.
    Chart 2: deviation bars — how each age group differs from the overall mean
             (highlights which factors are age-distinctive).
    """
    se_wide = _importance_weights(df_plot)
    if se_wide.empty:
        print("Phase 4c: no valid respondents — skipping.")
        return

    se_age = se_wide.join(df_plot["age_range"], how="left")
    se_age = se_age[se_age["age_range"].notna()]
    factor_cols = [c for c in se_age.columns if c != "age_range"]

    age_mean = se_age.groupby("age_range")[factor_cols].mean()
    age_n = se_age.groupby("age_range").size().rename("n")

    valid_ages = [a for a in age_order if a in age_mean.index]
    age_mean = age_mean.loc[valid_ages]

    # Sort factors by overall mean descending so the most important appear first
    overall_mean = age_mean.mean(axis=0).sort_values(ascending=False)
    factors_sorted = overall_mean.index.tolist()
    age_mean = age_mean[factors_sorted]

    n_total = len(se_age)

    # ── Chart 1: heatmap age × factor ─────────────────────────────────────────
    z = age_mean.values
    y_labels = [f"{a} (n={age_n.get(a, 0)})" for a in valid_ages]
    x_labels = [str(f) for f in factors_sorted]

    annotations = []
    for row_i, age_lbl in enumerate(y_labels):
        for col_j, factor_lbl in enumerate(x_labels):
            annotations.append(
                dict(
                    x=factor_lbl, y=age_lbl,
                    text=f"{z[row_i, col_j]:.1f}",
                    showarrow=False,
                    font=dict(size=10, color="black"),
                    xref="x", yref="y",
                )
            )

    fig1 = go.Figure(
        go.Heatmap(
            z=z,
            x=x_labels,
            y=y_labels,
            colorscale="RdYlGn",
            colorbar=dict(title="Mean importance (%)"),
            hovertemplate="Age: %{y}<br>Factor: %{x}<br>Importance: %{z:.1f}%<extra></extra>",
        )
    )
    fig1.update_layout(annotations=annotations)
    fig1.update_layout(
        title=f"Purchase factor importance by age group — mean self-explicated % (n={n_total})",
        xaxis_title="Purchase factor",
        yaxis_title="Age range",
        xaxis=dict(tickangle=-35),
    )
    thai_layout(fig1, height=max(320, 80 + 50 * len(valid_ages)), width=1100)
    fig1.show()

    # ── Chart 2: deviation from overall mean (top 10 factors) ────────────────
    top_factors = factors_sorted[:10]
    deviation = age_mean[top_factors].sub(overall_mean[top_factors], axis=1)

    palette = plc.qualitative.Set2
    fig2 = go.Figure()
    for i, age in enumerate(valid_ages):
        row_dev = deviation.loc[age]
        fig2.add_trace(
            go.Bar(
                name=age,
                x=[str(f) for f in top_factors],
                y=row_dev.values.tolist(),
                marker_color=palette[i % len(palette)],
                hovertemplate=f"Age: {age}<br>Factor: %{{x}}<br>Δ vs mean: %{{y:.1f}} pp<extra></extra>",
            )
        )
    fig2.add_shape(
        type="line", x0=0, x1=1, xref="paper", y0=0, y1=0,
        line=dict(dash="dot", color="gray", width=1),
    )
    fig2.update_layout(
        title=(
            f"Age-group deviation from overall mean importance — top {len(top_factors)} factors "
            f"(positive = above average priority for that age group)"
        ),
        xaxis_title="Purchase factor",
        yaxis_title="Deviation from overall mean (pp)",
        barmode="group",
        legend_title="Age range",
        xaxis=dict(tickangle=-30),
    )
    thai_layout(fig2, height=520, width=1100)
    fig2.show()
