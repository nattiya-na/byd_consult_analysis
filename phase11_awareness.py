"""Phase 11 — Powertrain awareness (Q13 familiarity 1–5 ratings)."""
import pandas as pd
import plotly.graph_objects as go

from survey_utils import thai_layout


_FAM_COLS = [
    "familiarity_ice", "familiarity_hev", "familiarity_phev",
    "familiarity_reev", "familiarity_bev",
]
_SHORT = {
    "familiarity_ice": "ICE", "familiarity_hev": "HEV", "familiarity_phev": "PHEV",
    "familiarity_reev": "REEV", "familiarity_bev": "BEV",
}


def run_phase11(df_plot, AGE_ORDER_PLOT):
    dfc = df_plot.copy()
    for c in _FAM_COLS:
        dfc[c] = pd.to_numeric(dfc[c], errors="coerce")

    n_valid = dfc[_FAM_COLS].notna().all(axis=1).sum()
    print(
        f"Rows with all five familiarity scores non-missing: "
        f"{n_valid} / {len(dfc)} (total rows in df_plot)"
    )

    desc = dfc[_FAM_COLS].agg(["mean", "median", "std", "min", "max"])
    print("\n=== Summary (1–5 scale) ===")
    print(desc.round(3).to_string())

    dfc["hev_minus_phev"] = dfc["familiarity_hev"] - dfc["familiarity_phev"]
    print(
        "\nMean(HEV − PHEV):",
        round(dfc["hev_minus_phev"].mean(), 3),
        "— share of rows with HEV score strictly greater than PHEV:",
        round((dfc["familiarity_hev"] > dfc["familiarity_phev"]).mean() * 100, 1),
        "%",
    )

    print("\n=== Mean familiarity by age_range ===")
    by_age = dfc.groupby("age_range", observed=False)[_FAM_COLS].mean().round(3)
    print(by_age.to_string())

    means = dfc[_FAM_COLS].mean()
    order = [
        "familiarity_ice", "familiarity_hev", "familiarity_bev",
        "familiarity_phev", "familiarity_reev",
    ]
    fig = go.Figure(
        go.Bar(
            x=[_SHORT[c] for c in order],
            y=[means[c] for c in order],
            marker_color=["#BC4749", "#6A994E", "#2E86AB", "#A23B72", "#F18F01"],
            text=[f"{means[c]:.2f}" for c in order],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Mean self-reported familiarity (Q13) by powertrain — combined sample",
        yaxis_title="Mean score (1–5)", xaxis_title="Powertrain",
        yaxis_range=[0, 5.35], height=420, showlegend=False,
        margin=dict(t=60, b=50),
    )
    fig.show()

    print(
        "\nCorrelation (familiarity scores): HEV–BEV",
        round(dfc["familiarity_hev"].corr(dfc["familiarity_bev"]), 3),
        "; PHEV–BEV",
        round(dfc["familiarity_phev"].corr(dfc["familiarity_bev"]), 3),
    )
