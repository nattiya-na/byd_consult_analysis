"""Phase 6 — Feature engineering: EV Readiness Index and one-hot encoding."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go

from survey_utils import (
    PT_ORDER, POWERTRAIN_COLORS, thai_layout,
    short_powertrain_label, one_hot_multiselect,
)


def run_phase6(df_plot):
    """Add powertrain_short, plugin_familiarity_norm, and ev_readiness_index to df_plot.

    Returns the modified df_plot.
    """
    df_plot = df_plot.copy()
    df_plot["powertrain_short"] = df_plot["powertrain_choose_today"].map(short_powertrain_label)

    _like = df_plot["likelihood_switch_ev_3y"].dropna().astype(str).unique().tolist()
    LIKELIHOOD_SCORE = {}
    for lab in _like:
        low = lab.lower()
        if "definitely not" in low:
            LIKELIHOOD_SCORE[lab] = 0.0
        elif "unlikely" in low:
            LIKELIHOOD_SCORE[lab] = 0.2
        elif "not sure" in low:
            LIKELIHOOD_SCORE[lab] = 0.4
        elif "likely" in low and "unlikely" not in low:
            LIKELIHOOD_SCORE[lab] = 0.6
        elif "definitely will" in low:
            LIKELIHOOD_SCORE[lab] = 0.8
        elif "already" in low or "process" in low:
            LIKELIHOOD_SCORE[lab] = 1.0
        else:
            LIKELIHOOD_SCORE[lab] = np.nan

    _chg = df_plot["charging_convenience"].dropna().astype(str).unique().tolist()
    CHARGING_SCORE = {}
    for lab in _chg:
        low = lab.lower()
        if "not convenient at all" in low:
            CHARGING_SCORE[lab] = 0.0
        elif "not very convenient" in low or "mostly depend on public" in low:
            CHARGING_SCORE[lab] = 0.25
        elif "not sure" in low:
            CHARGING_SCORE[lab] = 0.5
        elif "somewhat convenient" in low:
            CHARGING_SCORE[lab] = 0.75
        elif "very convenient" in low or "charge at home" in low:
            CHARGING_SCORE[lab] = 1.0
        else:
            CHARGING_SCORE[lab] = np.nan

    bev = pd.to_numeric(df_plot["familiarity_bev"], errors="coerce")
    phev = pd.to_numeric(df_plot["familiarity_phev"], errors="coerce")
    fam_mean = (bev + phev) / 2
    plugin_fam = (fam_mean - 1) / 4
    df_plot["plugin_familiarity_norm"] = plugin_fam

    lik_n = df_plot["likelihood_switch_ev_3y"].map(LIKELIHOOD_SCORE)
    chg_n = df_plot["charging_convenience"].map(CHARGING_SCORE)
    w1, w2, w3 = 0.35, 0.35, 0.30
    combo = w1 * lik_n + w2 * chg_n + w3 * df_plot["plugin_familiarity_norm"]
    df_plot["ev_readiness_index"] = np.where(combo.notna(), 1 + 9 * combo, np.nan)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df_plot["ev_readiness_index"].dropna(), bins=15, kde=True, ax=ax, color="#2E86AB")
    ax.set_title("EV Readiness Index (1–10)")
    ax.set_xlabel("Index")
    plt.tight_layout()
    plt.show()

    fig_ev = go.Figure()
    for pt in PT_ORDER:
        sub = df_plot.loc[df_plot["powertrain_short"] == pt, "ev_readiness_index"].dropna()
        if len(sub) == 0:
            continue
        fig_ev.add_trace(
            go.Box(
                y=sub, name=pt,
                marker_color=POWERTRAIN_COLORS.get(pt, "#888888"),
                boxmean="sd",
            )
        )
    fig_ev.update_layout(
        title="EV Readiness Index by powertrain (Plotly)",
        yaxis_title="Index", xaxis_title="Powertrain",
    )
    thai_layout(fig_ev, height=420, width=880)
    fig_ev.show()

    print(
        df_plot.groupby("powertrain_short")["ev_readiness_index"]
        .agg(["mean", "count"]).sort_values("mean", ascending=False)
    )

    barriers_ohe = one_hot_multiselect(df_plot, "ev_adoption_barriers", "b_")
    factors_top3_ohe = one_hot_multiselect(df_plot, "purchase_factors_top3", "f3_")
    info_sources_ohe = one_hot_multiselect(df_plot, "info_sources", "info_")
    brands_ohe = one_hot_multiselect(df_plot, "brands_considering", "br_")
    print(
        "One-hot shapes:",
        barriers_ohe.shape, factors_top3_ohe.shape,
        info_sources_ohe.shape, brands_ohe.shape,
    )

    return df_plot
