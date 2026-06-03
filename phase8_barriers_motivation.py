"""Phase 8 — Barrier and motivation deep dive."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from survey_utils import explode_multiselect


def run_phase8(df_plot, AGE_ORDER_PLOT, INCOME_ORDER_PLOT):
    # Top-3 EV barriers per age group (stacked bar)
    long_b = explode_multiselect(df_plot, "ev_adoption_barriers")
    long_b = long_b.join(df_plot[["age_range"]], on="row")
    long_b = long_b.dropna(subset=["age_range", "value"])

    rows_stack = []
    for age in AGE_ORDER_PLOT:
        sub = long_b[long_b["age_range"] == age]
        if sub.empty:
            continue
        top3 = sub["value"].value_counts().head(3)
        tot = top3.sum()
        for b, cnt in top3.items():
            rows_stack.append({"age_range": age, "barrier": b, "share_top3": cnt / tot if tot else 0})
    stack_df = pd.DataFrame(rows_stack)
    if not stack_df.empty:
        pivot = stack_df.pivot_table(
            index="age_range", columns="barrier", values="share_top3",
            fill_value=0, aggfunc="sum",
        )
        pivot = pivot.reindex([a for a in AGE_ORDER_PLOT if a in pivot.index])
        fig, ax = plt.subplots(figsize=(11, 5))
        pivot.plot(kind="barh", stacked=True, ax=ax, colormap="tab20")
        ax.set_title("Top-3 EV barriers per age (share among top-3 mentions)")
        ax.legend(title="Barrier", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
        plt.tight_layout()
        plt.show()

    # Purchase factor most important × monthly income (row % heatmap)
    pfi = df_plot.dropna(subset=["purchase_factor_most_important", "monthly_income"])
    ct_pfi = pd.crosstab(
        pfi["monthly_income"], pfi["purchase_factor_most_important"], normalize="index"
    )
    ct_pfi = ct_pfi.reindex([x for x in INCOME_ORDER_PLOT if x in ct_pfi.index])
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(ct_pfi, annot=True, fmt=".0%", cmap="Purples", ax=ax)
    ax.set_title("Purchase factor most important (row % within income band)")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
