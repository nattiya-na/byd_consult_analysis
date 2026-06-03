"""Phase 9 — Competitive and BYD brand positioning, plus powertrain × BYD analysis."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:
    from scipy.stats import chi2_contingency
except ImportError:
    chi2_contingency = None

from survey_utils import (
    PT_ORDER, POWERTRAIN_COLORS, thai_layout,
    short_powertrain_label, split_multiselect,
)


def run_phase9(df_plot, AGE_ORDER_PLOT):
    br = df_plot["brands_considering"].fillna("").str.lower()
    cohort_th = br.str.contains(r"\btoyota\b", regex=True) | br.str.contains(r"\bhonda\b", regex=True)
    cohort_byd = br.str.contains(r"\bbyd\b", regex=True)
    print("Toyota/Honda mention:", int(cohort_th.sum()), "BYD mention:", int(cohort_byd.sum()))

    def pt_mix(mask, label):
        sub = df_plot.loc[mask, "powertrain_short"].value_counts(normalize=True).sort_index()
        print(f"--- {label} (n={mask.sum()}) ---")
        print((sub * 100).round(1).astype(str) + "%")
        return sub

    pt_mix(cohort_th, "Toyota or Honda in brands")
    pt_mix(cohort_byd, "BYD in brands")

    fig, ax = plt.subplots(figsize=(9, 4))
    comp = pd.DataFrame(
        {
            "Toyota/Honda": df_plot.loc[cohort_th, "powertrain_short"].value_counts(normalize=True),
            "BYD": df_plot.loc[cohort_byd, "powertrain_short"].value_counts(normalize=True),
        }
    ).T.fillna(0)
    bar_cols = [c for c in PT_ORDER if c in comp.columns] + [
        c for c in comp.columns if c not in PT_ORDER
    ]
    comp = comp.reindex(columns=bar_cols)
    comp.plot(
        kind="bar", ax=ax,
        color=[POWERTRAIN_COLORS.get(c, "#999999") for c in comp.columns],
    )
    ax.set_title("Powertrain if choosing today — brand cohorts (share within cohort)")
    ax.set_ylabel("Share")
    ax.legend(title="Powertrain", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.setp(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    plt.show()

    GEN_MAP = {}
    for _a in AGE_ORDER_PLOT:
        if _a.startswith("18"):
            GEN_MAP[_a] = "Gen Z"
        elif _a.startswith("25"):
            GEN_MAP[_a] = "Millennial"
        elif _a.startswith("35"):
            GEN_MAP[_a] = "Gen X"
        elif _a.startswith("45"):
            GEN_MAP[_a] = "Boomer"
        else:
            GEN_MAP[_a] = "Boomer+"
    df_plot["generation"] = df_plot["age_range"].map(GEN_MAP)

    def top_reasons_by_gen(col, title):
        print(f"\n=== {title} ===")
        for g in ["Gen Z", "Millennial", "Gen X", "Boomer", "Boomer+"]:
            s = df_plot.loc[df_plot["generation"] == g, col].dropna().astype(str)
            if s.empty:
                continue
            vc = s.value_counts().head(5)
            print(g, "(n=%d)" % len(s))
            print(vc.head(3).to_string())

    top_reasons_by_gen("byd_not_considering_reason", "BYD not considering — top reasons")
    top_reasons_by_gen("byd_considering_reason", "BYD considering — top reasons")


def run_phase9b(df_plot):
    """Powertrain considering × BYD in brand list cross-analysis."""
    br = df_plot["brands_considering"].fillna("").str.lower()
    cohort_byd = br.str.contains(r"\bbyd\b", regex=True)

    rows_long = []
    for idx in df_plot.index:
        byd_flag = bool(cohort_byd.loc[idx])
        raw = df_plot.loc[idx, "powertrain_considering"]
        for token in split_multiselect(raw):
            pt = short_powertrain_label(token)
            if isinstance(pt, str):
                rows_long.append({"idx": idx, "pt_short": pt, "byd": byd_flag})

    long_cons = pd.DataFrame(rows_long)

    if not long_cons.empty:
        vc_byd = long_cons.loc[long_cons["byd"], "pt_short"].value_counts(normalize=True)
        vc_non = long_cons.loc[~long_cons["byd"], "pt_short"].value_counts(normalize=True)
        comp_cons = pd.DataFrame({"BYD in brands": vc_byd, "Not BYD in brands": vc_non}).T.fillna(0)
        bar_cols = [c for c in PT_ORDER if c in comp_cons.columns] + [
            c for c in comp_cons.columns if c not in PT_ORDER
        ]
        comp_cons = comp_cons.reindex(columns=bar_cols)
        fig, ax = plt.subplots(figsize=(9, 4))
        comp_cons.plot(
            kind="bar", ax=ax,
            color=[POWERTRAIN_COLORS.get(c, "#999999") for c in comp_cons.columns],
        )
        ax.set_title(
            "Powertrains under consideration — BYD vs not BYD in brand list "
            "(share within cohort; exploded mentions)"
        )
        ax.set_ylabel("Share of mentions")
        ax.legend(title="Powertrain", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.setp(ax.get_xticklabels(), rotation=0)
        plt.tight_layout()
        plt.show()
    else:
        print("No exploded powertrain considering rows.")

    EV_PLUGIN = {"BEV", "PHEV", "REEV"}

    def _ev_plugin_considering(val):
        found = set()
        for token in split_multiselect(val):
            pt = short_powertrain_label(token)
            if isinstance(pt, str):
                found.add(pt)
        return bool(found & EV_PLUGIN)

    df_plot["ev_plugin_considering"] = df_plot["powertrain_considering"].map(_ev_plugin_considering)

    row_labels = cohort_byd.map({True: "Yes", False: "No"}).rename("BYD in brands")
    col_labels = df_plot["ev_plugin_considering"].map(
        {True: "EV-plugin in considering", False: "No EV-plugin in considering"}
    )
    ct2 = pd.crosstab(row_labels, col_labels)
    print("\n2×2 counts (respondent-level):")
    print(ct2)
    print("\nRow % (within BYD yes / no):")
    row_pct = (ct2.div(ct2.sum(axis=1), axis=0) * 100).round(1).astype(str) + "%"
    print(row_pct)

    if chi2_contingency is not None and ct2.size and min(ct2.shape) >= 2:
        try:
            chi2, p, dof, exp = chi2_contingency(ct2.values)
            print(
                f"\nChi-square test on 2×2: χ²={chi2:.3f}, p={p:.4f} "
                "(survey responses are not independent trials; interpret cautiously)."
            )
        except ValueError as e:
            print(f"\nChi-square skipped: {e}")
    else:
        print("\n(install scipy for chi-square test.)")

    idx_order = df_plot.index
    hm_cols = [c for c in PT_ORDER if c != "Other"]
    pt_present = {pt: [] for pt in hm_cols}
    for idx in idx_order:
        tokens = set()
        for token in split_multiselect(df_plot.loc[idx, "powertrain_considering"]):
            pt = short_powertrain_label(token)
            if isinstance(pt, str) and pt in pt_present:
                tokens.add(pt)
        for pt in hm_cols:
            pt_present[pt].append(1 if pt in tokens else 0)

    hm_df = pd.DataFrame(pt_present, index=idx_order)
    hm_df["byd"] = cohort_byd
    share_byd = hm_df.loc[hm_df["byd"], hm_cols].mean()
    share_non = hm_df.loc[~hm_df["byd"], hm_cols].mean()
    hm_mat = pd.DataFrame({"BYD in brands": share_byd, "Not BYD in brands": share_non}).T
    hm_mat = hm_mat[[c for c in hm_cols if c in hm_mat.columns]]

    z = hm_mat.values.astype(float)
    text = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in r] for r in z]
    fig_h = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[str(c) for c in hm_mat.columns],
            y=[str(i) for i in hm_mat.index],
            text=text, texttemplate="%{text}",
            colorscale="Blues", colorbar=dict(title="Share of respondents"),
            hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
        )
    )
    fig_h.update_layout(
        title="Respondents including each powertrain in considering (row % within BYD / not BYD)",
        xaxis_title="Powertrain", yaxis_title="",
    )
    fig_h.update_xaxes(tickangle=-45)
    thai_layout(fig_h, height=420, width=900)
    fig_h.show()
