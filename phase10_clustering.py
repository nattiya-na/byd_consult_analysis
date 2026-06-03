"""Phase 10 — K-Modes clustering (categorical personas)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from kmodes.kmodes import KModes
except ImportError:
    KModes = None

from survey_utils import short_powertrain_label


def run_phase10(df_plot):
    if KModes is None:
        print("Install kmodes: pip install kmodes")
        return

    feat_cols = [
        "age_range", "monthly_income", "charging_convenience",
        "powertrain_choose_today", "likelihood_switch_ev_3y",
    ]
    dfc = df_plot.dropna(subset=feat_cols).copy()
    Xcat = dfc[feat_cols].astype(str).values

    costs = []
    ks = list(range(2, 7))
    for k in ks:
        km = KModes(n_clusters=k, init="Huang", n_init=10, random_state=42, verbose=0)
        km.fit(Xcat)
        costs.append(km.cost_)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(ks, costs, marker="o")
    ax.set_xlabel("K")
    ax.set_ylabel("K-Modes cost")
    ax.set_title("Elbow / cost curve")
    plt.tight_layout()
    plt.show()

    K_SEL = 4
    km_final = KModes(n_clusters=K_SEL, init="Huang", n_init=15, random_state=42, verbose=0)
    clusters = km_final.fit_predict(Xcat)
    dfc = dfc.copy()
    dfc["cluster"] = clusters
    print(dfc["cluster"].value_counts().sort_index())

    for c in range(K_SEL):
        print(f"\n--- Cluster {c} (n={(dfc['cluster'] == c).sum()}) ---")
        sub = dfc[dfc["cluster"] == c]
        for col in feat_cols:
            print(col + ":", sub[col].value_counts().head(3).to_string())
        print(
            "powertrain_short:",
            sub["powertrain_choose_today"].map(short_powertrain_label)
            .value_counts().head(5).to_string(),
        )
        print("ev_readiness mean:", float(sub["ev_readiness_index"].mean()))

    print("\n--- Persona labels (see markdown executive summary) ---")
    for c in range(K_SEL):
        sub = dfc[dfc["cluster"] == c]
        mode_pt = (
            sub["powertrain_choose_today"].map(short_powertrain_label).mode().iloc[0]
            if len(sub) else np.nan
        )
        print(f"Cluster {c}: dominant powertrain ~ {mode_pt}, n={len(sub)}")
