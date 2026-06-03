"""Shared data-loading helpers for the Streamlit app."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.colors as plc

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from survey_utils import (
    load_data, clean_survey, short_powertrain_label,
    one_hot_multiselect, split_multiselect,
    POWERTRAIN_COLORS, PT_ORDER, FONT_FAMILY,
    DD_CANONICAL_ORDER, INCOME_CANONICAL_ORDER,
)

_CSV = "แบบสอบถามความสนใจในการซื้อรถยนต์ไฟฟ้าทั่วไป (Responses) - Form Responses 1.csv"
DATA_PATH = _ROOT / _CSV
MOTOR_SHOW_PATH = _ROOT / "motor_show.csv"
CHINA_PATH = _ROOT / "survey_china.xlsx"

LAYOUT_BASE = dict(
    font=dict(family=FONT_FAMILY, size=12, color="#111111"),
    template="plotly_white",
    margin=dict(l=20, r=20, t=55, b=40),
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_font=dict(size=13, color="#d70c19", family=FONT_FAMILY),
    colorway=["#d70c19", "#1a1a1a", "#f59e0b", "#2563eb", "#16a34a", "#7c3aed", "#0891b2", "#ea580c"],
)

SOURCE_LABELS = {
    "general": "General online",
    "motor_show": "Motor show",
    "survey_china": "Survey China",
}


@st.cache_data
def load_survey() -> tuple[pd.DataFrame, list, list, list]:
    df_raw = load_data(DATA_PATH, MOTOR_SHOW_PATH, CHINA_PATH)
    df_clean, age_order, income_order, dd_order = clean_survey(df_raw)
    df_plot = _add_features(df_clean)
    return df_plot, age_order, income_order, dd_order


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["powertrain_short"] = df["powertrain_choose_today"].map(short_powertrain_label)

    lik_map: dict[str, float] = {}
    for lab in df["likelihood_switch_ev_3y"].dropna().astype(str).unique():
        low = lab.lower()
        if "definitely not" in low:
            lik_map[lab] = 0.0
        elif "unlikely" in low:
            lik_map[lab] = 0.2
        elif "not sure" in low:
            lik_map[lab] = 0.4
        elif "likely" in low and "unlikely" not in low:
            lik_map[lab] = 0.6
        elif "definitely will" in low:
            lik_map[lab] = 0.8
        elif "already" in low or "process" in low:
            lik_map[lab] = 1.0
        else:
            lik_map[lab] = np.nan

    chg_map: dict[str, float] = {}
    for lab in df["charging_convenience"].dropna().astype(str).unique():
        low = lab.lower()
        if "not convenient at all" in low:
            chg_map[lab] = 0.0
        elif "mostly depend on public" in low or "not very convenient" in low:
            chg_map[lab] = 0.25
        elif "not sure" in low:
            chg_map[lab] = 0.5
        elif "somewhat convenient" in low:
            chg_map[lab] = 0.75
        elif "very convenient" in low or "charge at home" in low:
            chg_map[lab] = 1.0
        else:
            chg_map[lab] = np.nan

    bev = pd.to_numeric(df["familiarity_bev"], errors="coerce")
    phev = pd.to_numeric(df["familiarity_phev"], errors="coerce")
    fam_norm = ((bev + phev) / 2 - 1) / 4

    lik_n = df["likelihood_switch_ev_3y"].map(lik_map)
    chg_n = df["charging_convenience"].map(chg_map)
    combo = 0.35 * lik_n + 0.35 * chg_n + 0.30 * fam_norm
    df["ev_readiness_index"] = np.where(combo.notna(), 1 + 9 * combo, np.nan)

    df["generation"] = df["age_range"].map({
        "18–24": "Gen Z", "25–34": "Millennial",
        "35–44": "Gen X", "45–54": "Boomer", "55+": "Boomer+",
    })
    df["is_genz"] = df["age_range"].isin(["18–24"])
    df["is_midage"] = df["age_range"].isin(["35–44", "45–54"])

    return df


def sidebar_filters(df: pd.DataFrame, age_order: list, income_order: list) -> pd.DataFrame:
    from utils.styles import sidebar_brand
    sidebar_brand()
    st.sidebar.markdown("### Filters")
    all_sources = df["data_source"].dropna().unique().tolist()
    sources = st.sidebar.multiselect("Data source", all_sources, default=all_sources)
    ages = st.sidebar.multiselect("Age group", age_order, default=age_order)
    genders = df["gender"].dropna().unique().tolist()
    selected_genders = st.sidebar.multiselect("Gender", genders, default=genders)

    mask = (
        df["data_source"].isin(sources)
        & df["age_range"].isin(ages)
        & df["gender"].isin(selected_genders)
    )
    filtered = df[mask]
    st.sidebar.caption(f"{len(filtered):,} of {len(df):,} respondents")
    return filtered


# ── Chart helpers ──────────────────────────────────────────────────────────────

def hbar(series: pd.Series, title: str, top_n: int | None = None, color: str = "Blues") -> go.Figure:
    vc = series.dropna().astype(str).value_counts()
    if top_n:
        vc = vc.head(top_n)
    vc = vc.sort_values(ascending=True)
    n = len(vc)
    colors = plc.sample_colorscale(color, [i / max(1, n - 1) for i in range(n)])
    fig = go.Figure(go.Bar(
        x=vc.values, y=vc.index.tolist(),
        orientation="h", marker=dict(color=colors), showlegend=False,
        text=vc.values, textposition="outside",
    ))
    fig.update_layout(**LAYOUT_BASE, title=title, xaxis_title="Count", yaxis_title="")
    height = max(320, min(900, 60 + 28 * max(1, n)))
    fig.update_layout(height=height)
    return fig


def heatmap_pct(df: pd.DataFrame, row_col: str, col_col: str, title: str,
                row_order: list | None = None, col_order: list | None = None,
                colorscale: str = "Blues") -> go.Figure:
    sub = df[[row_col, col_col]].dropna()
    ct = pd.crosstab(sub[row_col], sub[col_col], normalize="index") * 100
    if row_order:
        ct = ct.reindex([r for r in row_order if r in ct.index])
    if col_order:
        ct = ct.reindex(columns=[c for c in col_order if c in ct.columns], fill_value=0)
    z = ct.values.astype(float)
    text = [[f"{v:.0f}%" for v in r] for r in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ct.columns], y=[str(i) for i in ct.index],
        text=text, texttemplate="%{text}",
        colorscale=colorscale, colorbar=dict(title="%"),
        hovertemplate="%{y} × %{x}: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(**LAYOUT_BASE, title=title, height=max(340, 80 + 40 * len(ct.index)))
    fig.update_xaxes(tickangle=-30)
    return fig


def stacked_bar_pct(df: pd.DataFrame, row_col: str, col_col: str, title: str,
                    row_order: list | None = None, col_order: list | None = None,
                    color_map: dict | None = None) -> go.Figure:
    sub = df[[row_col, col_col]].dropna()
    ct = pd.crosstab(sub[row_col], sub[col_col], normalize="index") * 100
    if row_order:
        ct = ct.reindex([r for r in row_order if r in ct.index])
    cols = col_order if col_order else ct.columns.tolist()
    cols = [c for c in cols if c in ct.columns]
    fig = go.Figure()
    for c in cols:
        vals = ct[c].values
        color = (color_map or {}).get(c, None)
        fig.add_trace(go.Bar(
            name=c, x=[str(r) for r in ct.index], y=vals,
            marker_color=color,
            text=[f"{v:.0f}%" if v >= 4 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig.update_layout(**LAYOUT_BASE, title=title, barmode="stack",
                      yaxis_title="% within group", height=400)
    return fig


def explode_and_count(df: pd.DataFrame, col: str, top_n: int | None = None) -> pd.Series:
    rows = []
    for val in df[col].dropna():
        for tok in split_multiselect(str(val)):
            if tok.strip():
                rows.append(tok.strip())
    vc = pd.Series(rows).value_counts()
    return vc.head(top_n) if top_n else vc
