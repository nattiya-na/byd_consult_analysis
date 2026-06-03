/"""BYD EV Survey — IMC Analysis Dashboard.

Generates output/dashboard.html

Objective: Identify IMC strategy per powertrain for BYD customers.
Target personas:
  • Gen Z (18–24):      open to BEV, price-sensitive
  • Middle Age (35–54): family-oriented, minimal charging hassle → PHEV / REEV
"""
import matplotlib; matplotlib.use("Agg")
import re
from pathlib import Path
from datetime import date
from collections import Counter

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
from plotly.subplots import make_subplots

from survey_utils import (
    load_data, clean_survey,
    short_powertrain_label, explode_multiselect, split_brand_segments,
    POWERTRAIN_COLORS, PT_ORDER, FONT_FAMILY,
    DD_CANONICAL_ORDER, INCOME_CANONICAL_ORDER,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
_DIR = Path(__file__).parent
_CSV = "แบบสอบถามความสนใจในการซื้อรถยนต์ไฟฟ้าทั่วไป (Responses) - Form Responses 1.csv"
OUTPUT = _DIR / "output" / "dashboard.html"

# ── Persona definitions ───────────────────────────────────────────────────────
GENZ_AGES   = ["18–24"]
MIDAGE_AGES = ["35–44", "45–54"]
GEN_MAP = {"18–24": "Gen Z", "25–34": "Millennial",
           "35–44": "Gen X", "45–54": "Boomer", "55+": "Boomer+"}
GEN_ORDER = ["Gen Z", "Millennial", "Gen X", "Boomer", "Boomer+"]

PC = {"Gen Z": "#2E86AB", "Middle Age": "#E07A5F", "All": "#6C757D",
      "Millennial": "#52B788", "Gen X": "#E07A5F", "Boomer": "#C77DFF"}
FONT = FONT_FAMILY
BASE = dict(font=dict(family=FONT, size=11), template="plotly_white",
            margin=dict(l=10, r=10, t=55, b=35))

BUDGET_ORDER = [
    "Below 500,000 THB", "500,001 – 800,000 THB",
    "800,001 – 1,200,000 THB", "1,200,001 – 1,500,000 THB",
    "1,500,001 – 2,000,000 THB", "Above 2,000,000 THB", "Not sure",
]
CHARGING_MAP = {
    "Not convenient at all": "Not convenient at all",
    "Not very convenient — I would mostly depend on public charging": "Mostly public charging",
    "Somewhat convenient — condo/workplace/shared charging may be available": "Somewhat convenient",
    "Very convenient — I can likely charge at home": "Home charging",
    "Not sure": "Not sure",
}
INFO_DROP = re.compile(r"^\(|YouTube\) Social|^family$|^forums$|^reviewers$|^showrooms$|^radio ads$|^Research$")
INFO_NORM = {"TikTok": "TikTok / Social media", "Social media": "TikTok / Social media",
             "(Facebook": None, "YouTube)": None}
INFO_ORDER = [
    "TikTok / Social media", "Auto shows", "Friends / family",
    "Automotive websites / forums", "Influencers / KOLs / reviewers",
    "Test-drive events", "Dealers / showrooms", "TV / radio",
]


# ── Data helpers ──────────────────────────────────────────────────────────────

def _norm_budget(s):
    if pd.isna(s): return np.nan
    s = str(s)
    for canon in BUDGET_ORDER:
        key = re.sub(r"[^\d]", "", canon.split("THB")[0])
        if key and key in re.sub(r"[^\d]", "", s):
            return canon
    if "not sure" in s.lower(): return "Not sure"
    return np.nan


def _norm_charging(s):
    if pd.isna(s): return np.nan
    s = re.sub(r"^[—\- /]+", "", str(s)).strip()
    for k, v in CHARGING_MAP.items():
        if s.startswith(k[:20]):
            return v
    return np.nan


def _explode_info(series):
    rows = []
    for val in series.dropna():
        for tok in str(val).split(";"):
            tok = tok.strip()
            if not tok or INFO_DROP.search(tok): continue
            tok = INFO_NORM.get(tok, tok)
            if tok: rows.append(tok)
    return pd.Series(rows)


def _explode_col(series, sep=";"):
    rows = []
    for val in series.dropna():
        for tok in str(val).split(sep):
            tok = tok.strip()
            if tok: rows.append(tok)
    return pd.Series(rows)


def _pct_series(series, top_n=None):
    vc = series.value_counts(normalize=True) * 100
    return vc.head(top_n) if top_n else vc


# ── Feature engineering ───────────────────────────────────────────────────────

def build_features(df_clean):
    df = df_clean.copy()
    df["powertrain_short"] = df["powertrain_choose_today"].map(short_powertrain_label)
    df["generation"] = df["age_range"].map(GEN_MAP)
    df["is_genz"]   = df["age_range"].isin(GENZ_AGES)
    df["is_midage"] = df["age_range"].isin(MIDAGE_AGES)
    df["persona"]   = np.where(df["is_genz"], "Gen Z",
                     np.where(df["is_midage"], "Middle Age", "Other"))
    df["budget_clean"]   = df["budget_range"].map(_norm_budget)
    df["charging_clean"] = df["charging_convenience"].map(_norm_charging)
    df["mentions_byd"]   = (df["brands_considering"].fillna("")
                              .str.contains(r"\bBYD\b", case=False, regex=True))

    # EV Readiness Index
    LIK = {}
    for lab in df["likelihood_switch_ev_3y"].dropna().astype(str).unique():
        low = lab.lower()
        if "definitely not" in low:  LIK[lab] = 0.0
        elif "unlikely" in low:      LIK[lab] = 0.2
        elif "not sure" in low:      LIK[lab] = 0.4
        elif "likely" in low:        LIK[lab] = 0.6
        elif "definitely will" in low: LIK[lab] = 0.8
        elif "already" in low or "process" in low: LIK[lab] = 1.0
        else: LIK[lab] = np.nan
    CHG = {v: s for k, v in CHARGING_MAP.items()
           for s in [{"Not convenient at all": 0.0, "Mostly public charging": 0.25,
                      "Somewhat convenient": 0.5, "Home charging": 1.0,
                      "Not sure": np.nan}[v]] if not pd.isna(s)}
    CHG["Not sure"] = np.nan

    bev  = pd.to_numeric(df["familiarity_bev"],  errors="coerce")
    phev = pd.to_numeric(df["familiarity_phev"], errors="coerce")
    fam  = ((bev + phev) / 2 - 1) / 4
    lik_n = df["likelihood_switch_ev_3y"].map(LIK)
    chg_n = df["charging_clean"].map(CHG)
    combo = 0.35 * lik_n + 0.35 * chg_n + 0.30 * fam
    df["ev_readiness"] = np.where(combo.notna(), 1 + 9 * combo, np.nan)
    df["charging_score"] = chg_n
    return df


# ── Chart builders ────────────────────────────────────────────────────────────

def fig_powertrain_by_generation(df):
    pt_cols = [c for c in PT_ORDER if c in df["powertrain_short"].dropna().unique()]
    gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
    ct = pd.crosstab(df["generation"], df["powertrain_short"], normalize="index") * 100
    ct = ct.reindex(index=gen_rows, columns=pt_cols, fill_value=0)

    fig = go.Figure()
    for pt in pt_cols:
        vals = ct[pt].values
        fig.add_trace(go.Bar(
            name=pt, x=[str(g) for g in ct.index], y=vals,
            marker_color=POWERTRAIN_COLORS.get(pt, "#888"),
            text=[f"{v:.0f}%" if v >= 4 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig.update_layout(**BASE, title="Powertrain choice by generation (row %)",
                      barmode="stack", yaxis_title="% within generation",
                      xaxis_title="", legend_title="Powertrain",
                      height=360, width=None)
    return fig


def fig_ev_readiness_by_generation(df):
    gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
    fig = go.Figure()
    colors = ["#2E86AB","#52B788","#E07A5F","#C77DFF","#F18F01"]
    for i, gen in enumerate(gen_rows):
        sub = df.loc[df["generation"] == gen, "ev_readiness"].dropna()
        if sub.empty: continue
        fig.add_trace(go.Box(
            y=sub, name=f"{gen}<br>(n={len(sub)})",
            marker_color=colors[i % len(colors)], boxmean=True,
        ))
    fig.update_layout(**BASE, title="EV Readiness Index (1–10) by generation",
                      yaxis_title="Index", height=380)
    return fig


def fig_purchase_factors_comparison(df):
    groups = {
        "Gen Z": df["is_genz"],
        "Middle Age": df["is_midage"],
        "All": pd.Series(True, index=df.index),
    }
    factor_pcts = {}
    for label, mask in groups.items():
        top_factors = _explode_col(df.loc[mask, "purchase_factors_top3"])
        if top_factors.empty: continue
        factor_pcts[label] = _pct_series(top_factors, top_n=10)

    all_factors = factor_pcts.get("All", pd.Series(dtype=float)).head(10).index.tolist()
    fig = go.Figure()
    for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"]), ("All", PC["All"])]:
        if label not in factor_pcts: continue
        vals = [factor_pcts[label].get(f, 0) for f in all_factors]
        fig.add_trace(go.Bar(
            name=label, x=vals, y=all_factors, orientation="h",
            marker_color=color, opacity=0.85,
        ))
    fig.update_layout(**BASE, title="Top purchase factors — Gen Z vs Middle Age vs All (%)",
                      barmode="group", xaxis_title="% of mentions",
                      height=420, legend=dict(orientation="h", y=1.1))
    return fig


def fig_info_sources_comparison(df):
    groups = {"Gen Z": df["is_genz"], "Middle Age": df["is_midage"]}
    ns = {k: int(mask.sum()) for k, mask in groups.items()}
    source_pcts = {}
    for label, mask in groups.items():
        src = _explode_info(df.loc[mask, "info_sources"])
        if src.empty: continue
        source_pcts[label] = _pct_series(src)

    all_srcs = _explode_info(df["info_sources"])
    top_srcs = [s for s in INFO_ORDER if s in all_srcs.value_counts().index]
    extra = [s for s in all_srcs.value_counts().head(12).index if s not in top_srcs]
    display_srcs = (top_srcs + extra)[:10]

    fig = go.Figure()
    for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"])]:
        if label not in source_pcts: continue
        vals = [source_pcts[label].get(s, 0) for s in display_srcs]
        fig.add_trace(go.Bar(
            name=f"{label} (n={ns[label]})", x=vals, y=display_srcs,
            orientation="h", marker_color=color, opacity=0.85,
        ))
    fig.update_layout(**BASE, title="Information sources by persona — IMC channel priority (%)",
                      barmode="group", xaxis_title="% of respondents in group",
                      height=400, legend=dict(orientation="h", y=1.1))
    return fig


def fig_charging_by_powertrain(df):
    order_ch = ["Home charging", "Somewhat convenient", "Mostly public charging", "Not convenient at all"]
    pts = [p for p in PT_ORDER if p in df["powertrain_short"].dropna().unique()]
    sub = df.dropna(subset=["powertrain_short", "charging_clean"])
    ct = pd.crosstab(sub["powertrain_short"], sub["charging_clean"], normalize="index") * 100
    ct = ct.reindex(index=pts, columns=[c for c in order_ch if c in ct.columns], fill_value=0)

    z  = ct.values
    txt = [[f"{v:.0f}%" if v >= 3 else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(r) for r in ct.index],
        text=txt, texttemplate="%{text}",
        colorscale="RdYlGn", colorbar=dict(title="Share %"),
        hovertemplate="powertrain=%{y}<br>charging=%{x}<br>%{z:.0f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, title="Charging convenience by powertrain choice (row %)",
                      xaxis_title="Charging situation", yaxis_title="Powertrain chosen",
                      height=350, xaxis_tickangle=-20)
    return fig


def fig_barriers_by_persona(df):
    groups = {"Gen Z": df["is_genz"], "Middle Age": df["is_midage"]}
    barrier_pcts = {}
    for label, mask in groups.items():
        b = _explode_col(df.loc[mask, "ev_adoption_barriers"])
        if b.empty: continue
        barrier_pcts[label] = _pct_series(b, top_n=10)

    all_b = _explode_col(df["ev_adoption_barriers"])
    top_b = all_b.value_counts().head(8).index.tolist()

    fig = go.Figure()
    for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"])]:
        if label not in barrier_pcts: continue
        vals = [barrier_pcts[label].get(b, 0) for b in top_b]
        fig.add_trace(go.Bar(
            name=label, x=vals, y=top_b, orientation="h",
            marker_color=color, opacity=0.85,
        ))
    fig.update_layout(**BASE, title="EV adoption barriers by persona (%)",
                      barmode="group", xaxis_title="% of mentions in group",
                      height=400, legend=dict(orientation="h", y=1.1))
    return fig


def fig_byd_consideration_by_generation(df):
    gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
    rates, ns = [], []
    for gen in gen_rows:
        sub = df[df["generation"] == gen]
        rates.append(sub["mentions_byd"].mean() * 100)
        ns.append(len(sub))
    colors = [PC.get(g, "#888") for g in gen_rows]
    fig = go.Figure(go.Bar(
        x=[f"{g}<br>(n={n})" for g, n in zip(gen_rows, ns)],
        y=rates, marker_color=colors,
        text=[f"{v:.0f}%" for v in rates], textposition="outside",
    ))
    fig.update_layout(**BASE, title="BYD in brand consideration list by generation (%)",
                      yaxis_title="% of generation", yaxis_range=[0, max(rates, default=50) * 1.25],
                      height=350)
    return fig


def fig_byd_barriers_by_persona(df):
    groups = {"Gen Z": df["is_genz"], "Middle Age": df["is_midage"]}
    neg_reason = {}
    for label, mask in groups.items():
        s = df.loc[mask, "byd_not_considering_reason"].dropna()
        s = s[~s.str.contains(r"Considering BYD|พิจารณา", case=False, na=False)]
        if s.empty: continue
        neg_reason[label] = _pct_series(s, top_n=8)

    all_s = df["byd_not_considering_reason"].dropna()
    all_s = all_s[~all_s.str.contains(r"Considering BYD|พิจารณา", case=False, na=False)]
    top_neg = all_s.value_counts().head(6).index.tolist()

    fig = go.Figure()
    for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"])]:
        if label not in neg_reason: continue
        vals = [neg_reason[label].get(b, 0) for b in top_neg]
        fig.add_trace(go.Bar(
            name=label, x=vals, y=top_neg, orientation="h",
            marker_color=color, opacity=0.85,
        ))
    fig.update_layout(**BASE, title="BYD barriers by persona — objections to address (%)",
                      barmode="group", xaxis_title="% within persona",
                      height=360, legend=dict(orientation="h", y=1.1))
    return fig


def fig_byd_reasons_by_persona(df):
    groups = {"Gen Z": df["is_genz"], "Middle Age": df["is_midage"]}
    pos_reason = {}
    for label, mask in groups.items():
        s = df.loc[mask, "byd_considering_reason"].dropna()
        s = s[~s.str.contains(r"Not considering BYD|ไม่ได้เลือก", case=False, na=False)]
        if s.empty: continue
        pos_reason[label] = _pct_series(s, top_n=8)

    all_s = df["byd_considering_reason"].dropna()
    all_s = all_s[~all_s.str.contains(r"Not considering BYD|ไม่ได้เลือก", case=False, na=False)]
    top_pos = all_s.value_counts().head(6).index.tolist()

    fig = go.Figure()
    for label, color in [("Gen Z", PC["Gen Z"]), ("Middle Age", PC["Middle Age"])]:
        if label not in pos_reason: continue
        vals = [pos_reason[label].get(r, 0) for r in top_pos]
        fig.add_trace(go.Bar(
            name=label, x=vals, y=top_pos, orientation="h",
            marker_color=color, opacity=0.85,
        ))
    fig.update_layout(**BASE, title="BYD positive reasons by persona — messages to amplify (%)",
                      barmode="group", xaxis_title="% within persona",
                      height=340, legend=dict(orientation="h", y=1.1))
    return fig


def fig_budget_by_powertrain(df):
    sub = df.dropna(subset=["powertrain_short", "budget_clean"])
    pts = [p for p in PT_ORDER if p in sub["powertrain_short"].unique()]
    bdgs = [b for b in BUDGET_ORDER if b in sub["budget_clean"].unique()]
    ct = pd.crosstab(sub["powertrain_short"], sub["budget_clean"], normalize="index") * 100
    ct = ct.reindex(index=pts, columns=bdgs, fill_value=0)
    z = ct.values
    txt = [[f"{v:.0f}%" if v >= 4 else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(r) for r in ct.index],
        text=txt, texttemplate="%{text}",
        colorscale="Blues", colorbar=dict(title="Share %"),
        hovertemplate="powertrain=%{y}<br>budget=%{x}<br>%{z:.0f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, title="Budget range by powertrain choice (row %)",
                      xaxis_title="Budget (THB)", yaxis_title="Powertrain chosen",
                      height=340, xaxis_tickangle=-30)
    return fig


def fig_daily_driving_by_powertrain(df):
    sub = df.dropna(subset=["powertrain_short", "daily_driving_distance"])
    pts = [p for p in PT_ORDER if p in sub["powertrain_short"].unique()]
    dds = [d for d in DD_CANONICAL_ORDER if d in sub["daily_driving_distance"].unique()]
    ct  = pd.crosstab(sub["powertrain_short"], sub["daily_driving_distance"], normalize="index") * 100
    ct  = ct.reindex(index=pts, columns=dds, fill_value=0)
    z   = ct.values
    txt = [[f"{v:.0f}%" if v >= 4 else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(r) for r in ct.index],
        text=txt, texttemplate="%{text}",
        colorscale="Oranges", colorbar=dict(title="Share %"),
        hovertemplate="powertrain=%{y}<br>distance=%{x}<br>%{z:.0f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, title="Daily driving distance by powertrain choice (row %)",
                      xaxis_title="Daily driving distance", yaxis_title="Powertrain chosen",
                      height=340, xaxis_tickangle=-20)
    return fig


def fig_familiarity_by_persona(df):
    FAM_COLS = ["familiarity_ice","familiarity_hev","familiarity_phev","familiarity_reev","familiarity_bev"]
    SHORT    = {"familiarity_ice":"ICE","familiarity_hev":"HEV","familiarity_phev":"PHEV",
                "familiarity_reev":"REEV","familiarity_bev":"BEV"}
    groups = {"Gen Z": df["is_genz"], "Middle Age": df["is_midage"],
              "All": pd.Series(True, index=df.index)}
    fig = go.Figure()
    pt_colors = {"ICE":"#BC4749","HEV":"#6A994E","PHEV":"#A23B72","REEV":"#F18F01","BEV":"#2E86AB"}
    for label, mask in groups.items():
        sub = df[mask].copy()
        for c in FAM_COLS: sub[c] = pd.to_numeric(sub[c], errors="coerce")
        means = [sub[c].mean() for c in FAM_COLS]
        fig.add_trace(go.Bar(
            name=label, x=[SHORT[c] for c in FAM_COLS], y=means,
            marker_color=PC.get(label, "#888"), opacity=0.85,
            text=[f"{v:.2f}" for v in means], textposition="outside",
        ))
    fig.update_layout(**BASE, title="Powertrain familiarity (1–5) — Gen Z vs Middle Age vs All",
                      barmode="group", yaxis_title="Mean score",
                      yaxis_range=[0, 5.5], height=360,
                      legend=dict(orientation="h", y=1.1))
    return fig


def fig_household_by_powertrain(df):
    sub = df.dropna(subset=["powertrain_short", "household_size_n"])
    pts = [p for p in PT_ORDER if p in sub["powertrain_short"].unique()]
    means = sub.groupby("powertrain_short")["household_size_n"].agg(["mean","count"])
    means = means.reindex(pts).dropna()
    colors = [POWERTRAIN_COLORS.get(p, "#888") for p in means.index]
    fig = go.Figure(go.Bar(
        x=[str(i) for i in means.index],
        y=means["mean"].values,
        marker_color=colors,
        text=[f"{v:.1f} (n={int(c)})" for v, c in zip(means["mean"], means["count"])],
        textposition="outside",
    ))
    fig.update_layout(**BASE, title="Mean household size by powertrain choice",
                      yaxis_title="Mean household size", xaxis_title="Powertrain",
                      yaxis_range=[0, means["mean"].max() * 1.25], height=350)
    return fig


def fig_age_factors_heatmap(df):
    gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
    rows = []
    for _, r in df.dropna(subset=["generation","purchase_factors_top3"]).iterrows():
        for f in str(r["purchase_factors_top3"]).split(";"):
            f = f.strip()
            if f: rows.append({"generation": r["generation"], "factor": f})
    long = pd.DataFrame(rows)
    if long.empty: return go.Figure()
    top_f = long["factor"].value_counts().head(8).index.tolist()
    long  = long[long["factor"].isin(top_f)]
    ct    = pd.crosstab(long["generation"], long["factor"], normalize="index") * 100
    ct    = ct.reindex(index=[g for g in gen_rows if g in ct.index], columns=top_f, fill_value=0)
    z     = ct.values
    txt   = [[f"{v:.0f}%" if v >= 3 else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(i) for i in ct.index],
        text=txt, texttemplate="%{text}",
        colorscale="Purples", colorbar=dict(title="Share %"),
        hovertemplate="gen=%{y}<br>factor=%{x}<br>%{z:.0f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, title="Purchase factor importance by generation (row %)",
                      xaxis_tickangle=-35, height=320)
    return fig


def fig_age_barriers_heatmap(df):
    gen_rows = [g for g in GEN_ORDER if g in df["generation"].dropna().unique()]
    rows = []
    for _, r in df.dropna(subset=["generation","ev_adoption_barriers"]).iterrows():
        for b in str(r["ev_adoption_barriers"]).split(";"):
            b = b.strip()
            if b: rows.append({"generation": r["generation"], "barrier": b})
    long = pd.DataFrame(rows)
    if long.empty: return go.Figure()
    top_b = long["barrier"].value_counts().head(8).index.tolist()
    long  = long[long["barrier"].isin(top_b)]
    ct    = pd.crosstab(long["generation"], long["barrier"], normalize="index") * 100
    ct    = ct.reindex(index=[g for g in gen_rows if g in ct.index], columns=top_b, fill_value=0)
    z     = ct.values
    txt   = [[f"{v:.0f}%" if v >= 3 else "" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(i) for i in ct.index],
        text=txt, texttemplate="%{text}",
        colorscale="Oranges", colorbar=dict(title="Share %"),
        hovertemplate="gen=%{y}<br>barrier=%{x}<br>%{z:.0f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, title="EV adoption barriers by generation (row %)",
                      xaxis_tickangle=-35, height=320)
    return fig


# ── KPI helpers ───────────────────────────────────────────────────────────────

def _kpi_card(label, value, sub="", color="#2E86AB"):
    return f"""
<div class="col-6 col-md-3 mb-3">
  <div class="kpi-card" style="border-top:4px solid {color}">
    <div class="kpi-value" style="color:{color}">{value}</div>
    <div class="kpi-label">{label}</div>
    {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
  </div>
</div>"""


def _section(title, subtitle, *charts_html, icon="📊"):
    inner = "\n".join(
        f'<div class="col-12 col-xl-6 mb-4"><div class="chart-card">{ch}</div></div>'
        if i % 2 == 0 and len(charts_html) > 1 else
        f'<div class="col-12 col-xl-6 mb-4"><div class="chart-card">{ch}</div></div>'
        for i, ch in enumerate(charts_html)
    )
    if len(charts_html) == 1:
        inner = f'<div class="col-12 mb-4"><div class="chart-card">{charts_html[0]}</div></div>'
    return f"""
<div class="section-header"><h2>{icon} {title}</h2><p class="text-muted mb-0">{subtitle}</p></div>
<div class="row">{inner}</div>"""


def _imc_card(powertrain, persona, message, channels, barriers, opportunity, color):
    chan_html = "".join(f'<span class="badge me-1" style="background:{color}">{c}</span>' for c in channels)
    bar_html  = "".join(f'<span class="badge bg-secondary me-1">{b}</span>' for b in barriers)
    return f"""
<div class="col-12 col-lg-6 mb-4">
  <div class="imc-card" style="border-left:5px solid {color}">
    <div class="imc-header">
      <span class="powertrain-badge" style="background:{color}">{powertrain}</span>
      <span class="ms-2 persona-label">{persona}</span>
    </div>
    <div class="imc-body">
      <div class="imc-section"><strong>Core Message</strong><p>{message}</p></div>
      <div class="imc-section"><strong>Priority Channels</strong><p class="mb-1">{chan_html}</p></div>
      <div class="imc-section"><strong>Objections to Address</strong><p class="mb-1">{bar_html}</p></div>
      <div class="imc-section"><strong>Market Opportunity</strong><p>{opportunity}</p></div>
    </div>
  </div>
</div>"""


# ── HTML template ─────────────────────────────────────────────────────────────

CSS = """
:root{--blue:#2E86AB;--orange:#E07A5F;--green:#52B788;--dark:#212529;--gray:#6C757D}
body{background:#f4f6f9;color:var(--dark);font-family:'Segoe UI',sans-serif}
.navbar-brand{font-weight:700;font-size:1.3rem;letter-spacing:-.5px}
.section-header{margin:2.5rem 0 1rem;padding-bottom:.75rem;border-bottom:2px solid #dee2e6}
.section-header h2{font-size:1.35rem;font-weight:700;margin-bottom:.2rem}
.kpi-card{background:#fff;border-radius:10px;padding:1.25rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08);height:100%}
.kpi-value{font-size:2.2rem;font-weight:700;line-height:1}
.kpi-label{font-size:.85rem;font-weight:600;color:var(--gray);margin-top:.25rem;text-transform:uppercase;letter-spacing:.5px}
.kpi-sub{font-size:.78rem;color:#adb5bd;margin-top:.2rem}
.chart-card{background:#fff;border-radius:10px;padding:1rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.imc-card{background:#fff;border-radius:10px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.09)}
.imc-header{display:flex;align-items:center;margin-bottom:1rem}
.powertrain-badge{color:#fff;border-radius:6px;padding:.25rem .75rem;font-weight:700;font-size:.95rem}
.persona-label{font-size:.9rem;font-weight:600;color:var(--gray)}
.imc-section{margin-bottom:.75rem}
.imc-section strong{font-size:.8rem;text-transform:uppercase;letter-spacing:.5px;color:var(--gray)}
.imc-section p{margin:.2rem 0 0;font-size:.9rem}
.insight-box{background:#fff;border-radius:10px;padding:1.25rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:1rem;border-left:4px solid var(--blue)}
.insight-box.orange{border-left-color:var(--orange)}
"""

def build_html(df, figs: dict, kpis: dict) -> str:
    def _h(key, **kw):
        fig = figs[key]
        fig.update_layout(height=kw.get("height", fig.layout.height))
        return fig.to_html(full_html=False, include_plotlyjs=False,
                           config={"responsive": True, "displayModeBar": False})

    # ── KPIs ──
    kpi_row = "".join([
        _kpi_card("Total Respondents", f"{kpis['n_total']:,}", f"{kpis['n_sources']}", "#2E86AB"),
        _kpi_card("BYD Consideration Rate", f"{kpis['byd_rate']:.0f}%", "mention BYD in brand list", "#E07A5F"),
        _kpi_card("Gen Z → BEV", f"{kpis['genz_bev']:.0f}%", f"of Gen Z (n={kpis['n_genz']})", "#52B788"),
        _kpi_card("Middle Age → PHEV/REEV", f"{kpis['midage_phev_reev']:.0f}%",
                  f"of ages 35–54 (n={kpis['n_midage']})", "#C77DFF"),
    ])

    # ── Insight boxes ──
    genz_top_factor   = kpis["genz_top_factor"]
    midage_top_factor = kpis["midage_top_factor"]
    genz_top_src      = kpis["genz_top_src"]
    midage_top_src    = kpis["midage_top_src"]
    genz_top_barrier  = kpis["genz_top_barrier"]
    midage_top_barrier = kpis["midage_top_barrier"]

    insights_genz = f"""
<div class="insight-box">
  <strong>Gen Z (18–24) Snapshot</strong> &nbsp;·&nbsp; n={kpis['n_genz']}
  <ul class="mb-0 mt-2 small">
    <li>Top powertrain choice: <strong>BEV ({kpis['genz_bev']:.0f}%)</strong>, but HEV is a close second ({kpis['genz_hev']:.0f}%)</li>
    <li>Top purchase driver: <strong>{genz_top_factor}</strong> — validates price-sensitive framing</li>
    <li>Primary info source: <strong>{genz_top_src}</strong></li>
    <li>Top EV barrier: <strong>{genz_top_barrier}</strong></li>
    <li>EV Readiness: <strong>{kpis['genz_readiness']:.1f}/10</strong> (vs all-sample {kpis['all_readiness']:.1f}/10)</li>
    <li>BYD consideration: <strong>{kpis['genz_byd_rate']:.0f}%</strong></li>
  </ul>
</div>"""

    insights_midage = f"""
<div class="insight-box orange">
  <strong>Middle Age 35–54 Snapshot</strong> &nbsp;·&nbsp; n={kpis['n_midage']}
  <ul class="mb-0 mt-2 small">
    <li>Top powertrain choice: <strong>BEV ({kpis['midage_bev']:.0f}%)</strong>; PHEV+REEV combined = {kpis['midage_phev_reev']:.0f}%</li>
    <li>Top purchase driver: <strong>{midage_top_factor}</strong></li>
    <li>Primary info source: <strong>{midage_top_src}</strong></li>
    <li>Top EV barrier: <strong>{midage_top_barrier}</strong></li>
    <li>Home charging access: <strong>{kpis['midage_home_charging']:.0f}%</strong> have convenient charging</li>
    <li>Mean household size: <strong>{kpis['midage_hh_size']:.1f}</strong> people</li>
    <li>EV Readiness: <strong>{kpis['midage_readiness']:.1f}/10</strong></li>
  </ul>
</div>"""

    # ── IMC Cards ──
    imc_bev_genz = _imc_card(
        "BEV", "Gen Z (18–24)",
        f"Own your future — lowest running cost, zero emissions, full tech. "
        f"BYD BEV starts under 800K THB. Switch now, save every day.",
        [genz_top_src, "TikTok / Reels", "Influencer / KOL reviews", "Auto shows"],
        [genz_top_barrier, "Charging anxiety", "Brand unfamiliarity"],
        f"{kpis['genz_bev']:.0f}% of Gen Z already prefer BEV; only {kpis['genz_byd_rate']:.0f}% consider BYD — large "
        f"conversion gap to close with price-anchored messaging.",
        "#2E86AB",
    )
    imc_phev_midage = _imc_card(
        "PHEV", "Middle Age (35–54)",
        f"Drive petrol when you want, electric when you can. "
        f"PHEV gives your family 50+ km electric range with zero charging compromise. "
        f"Perfect for school runs and weekend trips alike.",
        [midage_top_src, "LINE / Family groups", "Auto shows", "Dealer test-drives"],
        [midage_top_barrier, "Range anxiety", "After-sales reliability"],
        f"{kpis['midage_phev_reev']:.0f}% of Middle Age lean PHEV/REEV; "
        f"{kpis['midage_home_charging']:.0f}% have home/condo charging — "
        f"highlight fuel-backup flexibility for the {100-kpis['midage_home_charging']:.0f}% without.",
        "#A23B72",
    )
    imc_reev_midage = _imc_card(
        "REEV", "Middle Age (35–54)",
        f"The family car that never needs a charging stop. "
        f"Range-extended EV: pure electric driving, ICE generator eliminates range anxiety. "
        f"Ideal for families with long weekend drives.",
        [midage_top_src, "YouTube reviews", "Auto shows", "Word-of-mouth / family"],
        ["Charging infrastructure concerns", "REEV unfamiliarity (avg score 2.4/5)", "Service network"],
        f"REEV familiarity is the lowest of all powertrains (2.4/5). "
        f"Education-first campaigns needed before conversion messaging.",
        "#F18F01",
    )
    imc_hev_millennial = _imc_card(
        "HEV", "Millennial (25–34) · Bridge buyers",
        f"All the fuel savings, none of the charging. "
        f"HEV feels just like petrol — just smarter. Ideal first step toward electrification "
        f"for drivers not yet ready to go fully electric.",
        ["TikTok / Social media", "Auto shows", "Automotive websites / forums", "Friends / family"],
        ["Price vs HEV incumbents (Toyota, Honda)", "Brand trust vs established brands"],
        f"Millennials are the largest segment (n={kpis['n_millennial']}). "
        f"Toyota/Honda HEV cohort is {kpis['th_rate']:.0f}% — BYD HEV must compete on value & warranty.",
        "#6A994E",
    )

    imc_section = f"""
<div class="section-header"><h2>🎯 IMC Strategy per Powertrain</h2>
<p class="text-muted mb-0">Recommended message, channel mix, and objection-handling per BYD powertrain and target persona</p>
</div>
<div class="row">
  {imc_bev_genz}
  {imc_phev_midage}
  {imc_reev_midage}
  {imc_hev_millennial}
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BYD EV Survey — IMC Dashboard</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
<script src="https://cdn.plot.ly/plotly-3.0.0.min.js" charset="utf-8"></script>
<style>{CSS}</style>
</head>
<body>
<nav class="navbar navbar-dark" style="background:#1a1a2e">
  <div class="container-fluid px-4">
    <span class="navbar-brand">⚡ BYD EV Survey — IMC Analysis Dashboard</span>
    <span class="text-white-50 small">Generated {date.today().strftime("%d %b %Y")} &nbsp;·&nbsp; n={kpis['n_total']} respondents</span>
  </div>
</nav>

<div class="container-fluid px-4 pb-5">

  <!-- KPIs -->
  <div class="section-header"><h2>📈 Key Metrics</h2>
    <p class="text-muted mb-0">Combined general online survey + China survey respondents</p>
  </div>
  <div class="row">{kpi_row}</div>

  <!-- Market Overview -->
  {_section("Market Overview",
    "Powertrain preferences across generations — where each cohort lands today",
    _h("pt_by_gen"), _h("byd_by_gen"))}

  <!-- Gen Z -->
  <div class="section-header"><h2>🔵 Persona 1: Gen Z → BEV</h2>
  <p class="text-muted mb-0">Ages 18–24 · Open to BEV · Price-sensitive · Digital-first</p></div>
  <div class="row"><div class="col-12">{insights_genz}</div></div>
  <div class="row">
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("purchase_factors")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("info_sources")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("familiarity")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("byd_barriers")}</div></div>
  </div>

  <!-- Middle Age -->
  <div class="section-header"><h2>🟠 Persona 2: Middle Age → PHEV / REEV</h2>
  <p class="text-muted mb-0">Ages 35–54 · Family-oriented · Minimal charging hassle · Value reliability</p></div>
  <div class="row"><div class="col-12">{insights_midage}</div></div>
  <div class="row">
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("charging_by_pt")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("hh_by_pt")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("budget_by_pt")}</div></div>
    <div class="col-12 col-xl-6 mb-4"><div class="chart-card">{_h("daily_by_pt")}</div></div>
  </div>

  <!-- Cross Analysis -->
  {_section("Cross Analysis",
    "Demographic × behaviour breakdowns to validate persona hypotheses",
    _h("ev_readiness"), _h("age_factors"),
    _h("age_barriers"), _h("byd_reasons"),
    icon="🔬")}

  <!-- IMC Strategy -->
  {imc_section}

</div>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading data…")
    df_raw = load_data(_DIR / _CSV, _DIR / "motor_show.csv", _DIR / "survey_china.xlsx")
    df_clean, *_ = clean_survey(df_raw)
    df = build_features(df_clean)
    n = len(df)

    gz  = df["is_genz"]
    ma  = df["is_midage"]
    ml  = df["generation"] == "Millennial"

    # Compute KPIs
    genz_pt   = df.loc[gz, "powertrain_short"].value_counts(normalize=True) * 100
    midage_pt = df.loc[ma, "powertrain_short"].value_counts(normalize=True) * 100

    def _top(series_mask, col, sep=";"):
        s = _explode_col(df.loc[series_mask, col], sep)
        return s.value_counts().index[0] if not s.empty else "N/A"

    def _top_src(mask):
        s = _explode_info(df.loc[mask, "info_sources"])
        return s.value_counts().index[0] if not s.empty else "N/A"

    def _home_charging_pct(mask):
        sub = df.loc[mask, "charging_clean"].dropna()
        if sub.empty: return 0.0
        return (sub == "Home charging").mean() * 100

    br = df["brands_considering"].fillna("").str.lower()
    th_mask = br.str.contains(r"\btoyota\b|\bhonda\b", regex=True)

    kpis = {
        "n_total":     n,
        "n_sources":   ", ".join(f"{k}: {v}" for k, v in df["data_source"].value_counts().to_dict().items()),
        "byd_rate":    df["mentions_byd"].mean() * 100,
        "n_genz":      int(gz.sum()),
        "n_midage":    int(ma.sum()),
        "n_millennial": int(ml.sum()),
        "genz_bev":    genz_pt.get("BEV", 0),
        "genz_hev":    genz_pt.get("HEV", 0),
        "midage_bev":  midage_pt.get("BEV", 0),
        "midage_phev_reev": midage_pt.get("PHEV", 0) + midage_pt.get("REEV", 0),
        "genz_byd_rate":   df.loc[gz, "mentions_byd"].mean() * 100,
        "genz_readiness":  df.loc[gz, "ev_readiness"].mean(),
        "midage_readiness": df.loc[ma, "ev_readiness"].mean(),
        "all_readiness":   df["ev_readiness"].mean(),
        "midage_home_charging": _home_charging_pct(ma),
        "midage_hh_size": df.loc[ma, "household_size_n"].dropna().mean(),
        "genz_top_factor":    _top(gz, "purchase_factors_top3"),
        "midage_top_factor":  _top(ma, "purchase_factors_top3"),
        "genz_top_src":       _top_src(gz),
        "midage_top_src":     _top_src(ma),
        "genz_top_barrier":   _top(gz, "ev_adoption_barriers"),
        "midage_top_barrier": _top(ma, "ev_adoption_barriers"),
        "th_rate": th_mask.mean() * 100,
    }

    print("Building charts…")
    figs = {
        "pt_by_gen":      fig_powertrain_by_generation(df),
        "byd_by_gen":     fig_byd_consideration_by_generation(df),
        "purchase_factors": fig_purchase_factors_comparison(df),
        "info_sources":   fig_info_sources_comparison(df),
        "ev_readiness":   fig_ev_readiness_by_generation(df),
        "charging_by_pt": fig_charging_by_powertrain(df),
        "hh_by_pt":       fig_household_by_powertrain(df),
        "budget_by_pt":   fig_budget_by_powertrain(df),
        "daily_by_pt":    fig_daily_driving_by_powertrain(df),
        "familiarity":    fig_familiarity_by_persona(df),
        "byd_barriers":   fig_byd_barriers_by_persona(df),
        "byd_reasons":    fig_byd_reasons_by_persona(df),
        "age_factors":    fig_age_factors_heatmap(df),
        "age_barriers":   fig_age_barriers_heatmap(df),
    }

    print("Assembling HTML…")
    html = build_html(df, figs, kpis)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"✓ Dashboard saved → {OUTPUT}")
    print(f"  Open with:  open {OUTPUT}")


if __name__ == "__main__":
    main()
