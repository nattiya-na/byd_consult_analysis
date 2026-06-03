"""Page 10 — Deep Dive: cross-dimensional analysis for BYD product-market fit."""
from __future__ import annotations
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, LAYOUT_BASE, explode_and_count,
)
from survey_utils import (
    PT_ORDER, POWERTRAIN_COLORS, split_multiselect, FONT_FAMILY,
)
from utils.styles import apply_byd_theme, page_header, section_header

st.set_page_config(page_title="Deep Dive — PMF Analysis", layout="wide")
apply_byd_theme()
page_header(
    "Deep Dive — Product Market Fit Analysis",
    "Cross-dimensional segmentation: who buys what, why they hesitate, and how to reach them",
)

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Shared helpers ─────────────────────────────────────────────────────────────

BUDGET_ORDER = [
    "Below 500,000 THB",
    "500,001 – 800,000 THB",
    "800,001 – 1,200,000 THB",
    "1,200,001 – 1,500,000 THB",
    "1,500,001 – 2,000,000 THB",
    "Above 2,000,000 THB",
    "Not sure",
]


def _clean_budget(val) -> str:
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    for canonical in BUDGET_ORDER:
        if canonical in s:
            return canonical
    sl = s.lower()
    if "not sure" in sl:
        return "Not sure"
    if "below" in sl and "500" in s:
        return "Below 500,000 THB"
    if "above" in sl and "2,000" in s:
        return "Above 2,000,000 THB"
    if re.search(r"800,001", s) and re.search(r"1,200,000", s):
        return "800,001 – 1,200,000 THB"
    if re.search(r"500,001", s) and re.search(r"800,000", s):
        return "500,001 – 800,000 THB"
    if re.search(r"1,200,001", s) and re.search(r"1,500,000", s):
        return "1,200,001 – 1,500,000 THB"
    if re.search(r"1,500,001", s) and re.search(r"2,000,000", s):
        return "1,500,001 – 2,000,000 THB"
    return np.nan


df["budget_clean"] = df["budget_range"].map(_clean_budget)
df["ev_readiness_index"] = pd.to_numeric(df["ev_readiness_index"], errors="coerce")

BARRIER_SHORT = {
    "Insufficient charging stations": "Charging stations",
    "Battery concerns": "Battery concerns",
    "Maintenance concerns": "Maintenance",
    "Range anxiety": "Range anxiety",
    "Charging takes too long": "Slow charging",
    "No home charging access": "No home charging",
    "Limited service network": "Limited service",
    "High upfront cost": "High cost",
    "Satisfied with current vehicle": "Happy w/ ICE",
    "Technology is too new": "Tech too new",
    "Uncertain resale value": "Resale value",
    "Lack of brand trust": "Brand trust",
    "I have no concerns": "No concerns",
}

FACTOR_SHORT = {
    "After-sales service / service network": "After-sales",
    "Brand trust / reliability": "Brand trust",
    "Purchase price": "Price",
    "Running cost over time": "Running cost",
    "Technology / features": "Tech / features",
    "Performance / driving experience": "Performance",
    "Design / appearance": "Design",
    "Resale value": "Resale value",
    "Charging convenience": "Charging",
    "Promotions / financing": "Promotions",
}

INFO_SHORT = {
    "Social media": "Social media",
    "TikTok": "TikTok",
    "Auto shows": "Auto shows",
    "Friends / family": "Friends/family",
    "Automotive websites / forums": "Auto websites",
    "Influencers / KOLs / reviewers": "KOLs",
    "Test-drive events": "Test drives",
    "Dealers / showrooms": "Dealers",
    "YouTube) Social media (Facebook": "YouTube/Facebook",
}


def multiselect_pct_heatmap(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    group_order: list,
    short_labels: dict | None,
    title: str,
    colorscale: str = "YlOrRd",
    top_n: int = 10,
) -> go.Figure | None:
    """
    For each group, compute % of respondents who mentioned each multi-select value.
    Returns a heatmap figure.
    """
    rows = []
    for idx, row in df.iterrows():
        grp = row[group_col]
        val = row[value_col]
        if pd.isna(grp) or pd.isna(val):
            continue
        for tok in split_multiselect(str(val)):
            tok = tok.strip()
            if tok:
                rows.append({"idx": idx, "group": str(grp), "value": tok})

    if not rows:
        return None

    long = pd.DataFrame(rows).drop_duplicates(subset=["idx", "group", "value"])
    group_totals = df[group_col].dropna().astype(str).value_counts()

    ct = long.groupby(["group", "value"]).size().reset_index(name="count")
    ct["pct"] = ct.apply(
        lambda r: r["count"] / group_totals.get(r["group"], 1) * 100, axis=1
    )

    # Keep top_n values by total mentions
    top_values = ct.groupby("value")["count"].sum().nlargest(top_n).index.tolist()
    ct = ct[ct["value"].isin(top_values)]

    pivot = ct.pivot(index="group", columns="value", values="pct").fillna(0)

    # Apply order
    valid_groups = [g for g in group_order if g in pivot.index]
    pivot = pivot.reindex(valid_groups)

    # Apply short labels to columns
    if short_labels:
        pivot.columns = [short_labels.get(c, c[:28]) for c in pivot.columns]

    z = pivot.values.astype(float)
    text = [[f"{v:.0f}%" for v in r] for r in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(c) for c in pivot.columns],
        y=[str(r) for r in pivot.index],
        text=text,
        texttemplate="%{text}",
        colorscale=colorscale,
        colorbar=dict(title="% of group"),
        hovertemplate="%{y} → %{x}: %{z:.1f}% of group<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=title,
        height=max(320, 80 + 45 * len(pivot.index)),
        xaxis_tickangle=-30,
    )
    return fig


def insight_box(text: str) -> None:
    st.info(f"**PMF Signal:** {text}")


# ── Summary KPIs ───────────────────────────────────────────────────────────────
section_header("Conversion Funnel Overview", "Headline stats across the full filtered dataset")

likely_mask = df["likelihood_switch_ev_3y"].str.contains(
    "Likely|Definitely|process", case=False, na=False
)
bev_share = (df["powertrain_short"] == "BEV").mean() * 100
byd_mask = df["brands_considering"].fillna("").str.contains(r"\bBYD\b", case=False, regex=True)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Likely to switch to EV (3yr)", f"{likely_mask.mean()*100:.0f}%", f"{likely_mask.sum()} respondents")
c2.metric("BEV as first choice today", f"{bev_share:.0f}%")
c3.metric("BYD consideration rate", f"{byd_mask.mean()*100:.0f}%")
top_barrier = explode_and_count(df, "ev_adoption_barriers", top_n=1)
c4.metric("#1 EV barrier", top_barrier.index[0] if len(top_barrier) else "—")
top_factor = explode_and_count(df, "purchase_factors_top3", top_n=1)
c5.metric("#1 purchase factor", top_factor.index[0] if len(top_factor) else "—")

st.divider()

# ── Tab layout ─────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Age × Barriers",
    "Income × Barriers",
    "Segment Sweet Spots",
    "Purchase Drivers by Age",
    "Media Channels by Age",
    "Budget × Powertrain Fit",
    "BYD Consideration Map",
    "Barrier Load vs. Readiness",
])

# ── Tab 1: Age × EV Barriers ──────────────────────────────────────────────────
with tabs[0]:
    section_header(
        "Which age group fears what?",
        "% of respondents in each age group who mentioned each EV adoption barrier (multi-select)"
    )
    fig = multiselect_pct_heatmap(
        df, "age_range", "ev_adoption_barriers",
        age_order, BARRIER_SHORT,
        "Age Group × EV Adoption Barriers  (% of age group mentioning each barrier)",
        colorscale="OrRd", top_n=10,
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data.")

    insight_box(
        "If Gen Z (18–24) cite infrastructure barriers more than service barriers, "
        "BYD's message to them should centre on charging convenience and city-ready range — "
        "not after-sales reassurance. Older segments (45–54) who cite service/brand trust "
        "respond better to warranty, partnership, and longevity proof points."
    )

    with st.expander("Raw counts table"):
        rows_b = []
        for idx, row in df.iterrows():
            age = row["age_range"]
            val = row["ev_adoption_barriers"]
            if pd.isna(age) or pd.isna(val):
                continue
            for tok in split_multiselect(str(val)):
                tok = tok.strip()
                if tok:
                    rows_b.append({"age_range": str(age), "barrier": tok})
        if rows_b:
            raw_ct = pd.DataFrame(rows_b).value_counts(["age_range", "barrier"]).unstack(fill_value=0)
            valid = [g for g in age_order if g in raw_ct.index]
            st.dataframe(raw_ct.reindex(valid), use_container_width=True)

# ── Tab 2: Income × EV Barriers ───────────────────────────────────────────────
with tabs[1]:
    section_header(
        "Does income shift barrier type?",
        "% of respondents in each income band who mentioned each EV barrier"
    )
    fig2 = multiselect_pct_heatmap(
        df, "monthly_income", "ev_adoption_barriers",
        income_order, BARRIER_SHORT,
        "Income Band × EV Adoption Barriers  (% of income group mentioning each barrier)",
        colorscale="BuPu", top_n=10,
    )
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Insufficient data.")

    insight_box(
        "Low-income bands (below 30k THB) are disproportionately blocked by 'High upfront cost' — "
        "BYD should offer entry-level BEV or lease/financing products here. "
        "Mid-to-high income bands (60k–150k THB) show the highest 'Limited service network' concern, "
        "making them the primary target for BYD's service guarantee campaign. "
        "High-income (150k+) show lower barrier counts overall — this is the easiest conversion segment."
    )

# ── Tab 3: Segment Sweet Spots (Age × Income EV Readiness) ────────────────────
with tabs[2]:
    section_header(
        "Where are the highest-readiness targets?",
        "Mean EV Readiness Index (1–10) per age × income cell — darker = more ready"
    )

    pivot_ri = df.dropna(subset=["age_range", "monthly_income", "ev_readiness_index"]).copy()
    pivot_ri["age_range"] = pivot_ri["age_range"].astype(str)
    pivot_ri["monthly_income"] = pivot_ri["monthly_income"].astype(str)

    grp_ri = pivot_ri.groupby(["age_range", "monthly_income"]).agg(
        mean_ri=("ev_readiness_index", "mean"),
        count=("ev_readiness_index", "count"),
    ).reset_index()

    heat_ri = grp_ri.pivot(index="age_range", columns="monthly_income", values="mean_ri")
    heat_count = grp_ri.pivot(index="age_range", columns="monthly_income", values="count").fillna(0)

    valid_age = [a for a in age_order if a in heat_ri.index]
    valid_inc = [i for i in income_order if i in heat_ri.columns]
    heat_ri = heat_ri.reindex(valid_age)[valid_inc]
    heat_count = heat_count.reindex(valid_age)[valid_inc].fillna(0)

    z_ri = heat_ri.values.astype(float)
    text_ri = []
    for i, row_a in enumerate(valid_age):
        row_txt = []
        for j, col_i in enumerate(valid_inc):
            v = heat_ri.loc[row_a, col_i] if row_a in heat_ri.index and col_i in heat_ri.columns else np.nan
            n = int(heat_count.loc[row_a, col_i]) if row_a in heat_count.index and col_i in heat_count.columns else 0
            row_txt.append(f"{v:.1f}<br>n={n}" if not np.isnan(v) else f"n={n}")
        text_ri.append(row_txt)

    inc_short = [i.replace(" THB", "").replace("Below ", "<").replace("Above ", ">") for i in valid_inc]
    fig3 = go.Figure(go.Heatmap(
        z=z_ri,
        x=inc_short,
        y=valid_age,
        text=text_ri,
        texttemplate="%{text}",
        colorscale="YlGn",
        colorbar=dict(title="Readiness"),
        zmin=1, zmax=10,
        hovertemplate="Age %{y} × Income %{x}<br>Mean readiness: %{z:.1f}<extra></extra>",
    ))
    fig3.update_layout(
        **LAYOUT_BASE,
        title="EV Readiness Index by Age × Income — segment sweet spots",
        height=380, xaxis_tickangle=-30,
    )
    st.plotly_chart(fig3, use_container_width=True)

    insight_box(
        "Dark green cells = highest-readiness segments = lowest cost to convert. "
        "Prioritise BYD's conversion campaigns on these segments first. "
        "Light cells (low readiness + low count) may need longer nurture cycles or different products (PHEV/REEV) "
        "to build a path to eventual BEV purchase."
    )

    # Bonus: top segments ranked
    top_segs = grp_ri[grp_ri["count"] >= 5].nlargest(8, "mean_ri")[
        ["age_range", "monthly_income", "mean_ri", "count"]
    ].rename(columns={"mean_ri": "Mean EV Readiness", "count": "n"})
    top_segs["Mean EV Readiness"] = top_segs["Mean EV Readiness"].round(2)
    st.caption("Top 8 segments by mean EV readiness (min n=5):")
    st.dataframe(top_segs, use_container_width=True, hide_index=True)

# ── Tab 4: Purchase Drivers × Age ─────────────────────────────────────────────
with tabs[3]:
    section_header(
        "What drives each age group's decision?",
        "% of age group who included each factor in their top-3 purchase criteria"
    )
    fig4 = multiselect_pct_heatmap(
        df, "age_range", "purchase_factors_top3",
        age_order, FACTOR_SHORT,
        "Age Group × Purchase Factors  (% mentioning each factor in top-3)",
        colorscale="Blues", top_n=10,
    )
    if fig4:
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Insufficient data.")

    insight_box(
        "After-sales and brand trust dominate across all ages — BYD's service expansion "
        "is its single biggest lever. However, younger groups (18–34) over-index on 'Running cost' "
        "and 'Technology / features', suggesting BYD Seal/Atto messaging should lead with TCO and tech. "
        "Older groups (45+) weight 'Brand trust' higher — localised service and Thai-language support matter most."
    )

    st.divider()
    section_header("Most important single factor × age", "Which factor wins when only one can be picked")

    pfi_df = df.dropna(subset=["age_range", "purchase_factor_most_important"]).copy()
    pfi_df["age_range"] = pfi_df["age_range"].astype(str)
    pfi_ct = pd.crosstab(
        pfi_df["age_range"], pfi_df["purchase_factor_most_important"], normalize="index"
    ) * 100
    valid_age2 = [a for a in age_order if a in pfi_ct.index]
    pfi_ct = pfi_ct.reindex(valid_age2)

    top_factors = pfi_ct.sum().nlargest(8).index.tolist()
    pfi_ct_top = pfi_ct[top_factors]
    pfi_ct_top.columns = [FACTOR_SHORT.get(c, c[:22]) for c in pfi_ct_top.columns]

    fig4b = go.Figure()
    palette = plc.qualitative.Set2
    for i, col in enumerate(pfi_ct_top.columns):
        fig4b.add_trace(go.Bar(
            name=col,
            x=pfi_ct_top.index.tolist(),
            y=pfi_ct_top[col].values,
            marker_color=palette[i % len(palette)],
            text=[f"{v:.0f}%" if v >= 5 else "" for v in pfi_ct_top[col].values],
            textposition="inside",
        ))
    fig4b.update_layout(
        **LAYOUT_BASE,
        barmode="stack",
        title="Most important purchase factor (single pick) by age group — row %",
        yaxis_title="% of age group",
        height=380,
    )
    st.plotly_chart(fig4b, use_container_width=True)

# ── Tab 5: Media Channels × Age ───────────────────────────────────────────────
with tabs[4]:
    section_header(
        "Where does each age group get information?",
        "% of age group using each information source — informs IMC channel strategy"
    )
    fig5 = multiselect_pct_heatmap(
        df, "age_range", "info_sources",
        age_order, INFO_SHORT,
        "Age Group × Information Sources  (% of age group using each channel)",
        colorscale="Teal", top_n=9,
    )
    if fig5:
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("Insufficient data.")

    insight_box(
        "TikTok and Social media dominate among 18–34. Auto shows and Friends/family are "
        "the top channels for 35–54. BYD's KOL/TikTok spend should be front-loaded on Gen Z "
        "while event/experiential marketing and peer referral programs target mid-age buyers. "
        "Test-drive events appear high across all ages — worth investing in nationwide."
    )

    # Bonus: channel reach by generation
    st.divider()
    section_header("Channel reach — Gen Z vs. Mid-Age side-by-side")

    gen_df = df.copy()
    gen_df["gen_group"] = gen_df["age_range"].astype(str).map(
        lambda x: "Gen Z (18–24)" if x == "18–24"
        else ("Millennial (25–34)" if x == "25–34"
              else ("Mid-Age (35–54)" if x in ("35–44", "45–54") else None))
    )
    gen_df = gen_df.dropna(subset=["gen_group"])
    gen_groups = ["Gen Z (18–24)", "Millennial (25–34)", "Mid-Age (35–54)"]

    info_rows = []
    for idx, row in gen_df.iterrows():
        grp = row["gen_group"]
        val = row["info_sources"]
        if pd.isna(val):
            continue
        for tok in split_multiselect(str(val)):
            tok = tok.strip()
            if tok and tok in INFO_SHORT:
                info_rows.append({"group": grp, "channel": INFO_SHORT[tok]})

    if info_rows:
        gen_totals = gen_df["gen_group"].value_counts()
        info_long2 = pd.DataFrame(info_rows)
        info_ct2 = info_long2.groupby(["group", "channel"]).size().reset_index(name="count")
        info_ct2["pct"] = info_ct2.apply(
            lambda r: r["count"] / gen_totals.get(r["group"], 1) * 100, axis=1
        )
        info_pivot2 = info_ct2.pivot(index="group", columns="channel", values="pct").fillna(0)
        valid_gen = [g for g in gen_groups if g in info_pivot2.index]
        info_pivot2 = info_pivot2.reindex(valid_gen)

        fig5b = go.Figure()
        gen_colors = {"Gen Z (18–24)": "#2E86AB", "Millennial (25–34)": "#00A851", "Mid-Age (35–54)": "#A23B72"}
        for grp in valid_gen:
            if grp not in info_pivot2.index:
                continue
            row_v = info_pivot2.loc[grp]
            fig5b.add_trace(go.Bar(
                name=grp,
                x=row_v.index.tolist(),
                y=row_v.values,
                marker_color=gen_colors.get(grp, "#888"),
            ))
        fig5b.update_layout(
            **LAYOUT_BASE,
            barmode="group",
            title="Channel reach by generation cohort (% using each channel)",
            yaxis_title="% of cohort",
            height=400,
            xaxis_tickangle=-25,
        )
        st.plotly_chart(fig5b, use_container_width=True)

# ── Tab 6: Budget × Powertrain Fit ────────────────────────────────────────────
with tabs[5]:
    section_header(
        "Which powertrain fits which budget?",
        "Stacked bar: powertrain first choice (today) distribution within each budget tier"
    )

    bud_pt = df.dropna(subset=["budget_clean", "powertrain_short"]).copy()
    ct_bp = pd.crosstab(bud_pt["budget_clean"], bud_pt["powertrain_short"], normalize="index") * 100
    valid_bud = [b for b in BUDGET_ORDER if b in ct_bp.index]
    ct_bp = ct_bp.reindex(valid_bud)
    valid_pt = [p for p in PT_ORDER if p in ct_bp.columns]
    ct_bp = ct_bp[valid_pt]

    fig6 = go.Figure()
    for pt in valid_pt:
        vals = ct_bp[pt].values
        fig6.add_trace(go.Bar(
            name=pt,
            x=[b.replace(" THB", "") for b in ct_bp.index.tolist()],
            y=vals,
            marker_color=POWERTRAIN_COLORS.get(pt),
            text=[f"{v:.0f}%" if v >= 5 else "" for v in vals],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig6.update_layout(
        **LAYOUT_BASE,
        barmode="stack",
        title="Powertrain first choice × budget tier (row %)",
        yaxis_title="% within budget tier",
        height=420,
        xaxis_tickangle=-25,
    )
    st.plotly_chart(fig6, use_container_width=True)

    insight_box(
        "BEV preference rises with budget — confirming the premium EV market is real and actionable. "
        "PHEV/REEV preference is strongest in the 800k–1.5M THB range, aligning with BYD Song Plus/DM-i pricing. "
        "Below 800k THB, ICE/HEV still dominate — BYD has a product gap here. An affordable entry-level BEV "
        "or REEV at sub-800k could unlock a large price-sensitive segment."
    )

    # Add raw count table
    with st.expander("Counts table (absolute)"):
        ct_abs = pd.crosstab(bud_pt["budget_clean"], bud_pt["powertrain_short"])
        valid_b2 = [b for b in BUDGET_ORDER if b in ct_abs.index]
        st.dataframe(ct_abs.reindex(valid_b2), use_container_width=True)

    st.divider()
    section_header("Income × Budget alignment", "Do stated budgets match income reality?")

    inc_bud = df.dropna(subset=["monthly_income", "budget_clean"]).copy()
    inc_bud["monthly_income"] = inc_bud["monthly_income"].astype(str)
    ct_ib = pd.crosstab(inc_bud["monthly_income"], inc_bud["budget_clean"], normalize="index") * 100
    valid_inc2 = [i for i in income_order if i in ct_ib.index]
    valid_bud2 = [b for b in BUDGET_ORDER if b in ct_ib.columns]
    ct_ib = ct_ib.reindex(valid_inc2)[valid_bud2].fillna(0)

    bud_short = [b.replace(" THB", "").replace("Below ", "<").replace("Above ", ">") for b in valid_bud2]

    fig6b = go.Figure(go.Heatmap(
        z=ct_ib.values.astype(float),
        x=bud_short,
        y=valid_inc2,
        text=[[f"{v:.0f}%" for v in r] for r in ct_ib.values],
        texttemplate="%{text}",
        colorscale="Blues",
        colorbar=dict(title="% of income"),
        hovertemplate="%{y} → budget %{x}: %{z:.1f}%<extra></extra>",
    ))
    fig6b.update_layout(
        **LAYOUT_BASE,
        title="Income band × stated budget (row %) — do budgets align with income?",
        height=380, xaxis_tickangle=-25,
    )
    st.plotly_chart(fig6b, use_container_width=True)

    insight_box(
        "If high-income respondents cluster in lower budget tiers than expected, "
        "price perception (not affordability) is the conversion barrier — "
        "indicating a need for value justification, not discounting."
    )

# ── Tab 7: BYD Consideration Map ──────────────────────────────────────────────
with tabs[6]:
    section_header(
        "Where is BYD's brand strongest and weakest?",
        "BYD consideration rate by age × income + competitive brand comparison"
    )

    byd_df = df.copy()
    byd_df["considers_byd"] = byd_df["brands_considering"].fillna("").str.contains(
        r"\bBYD\b", case=False, regex=True
    ).astype(int)
    byd_df["considers_tesla"] = byd_df["brands_considering"].fillna("").str.contains(
        r"\bTesla\b", case=False, regex=True
    ).astype(int)
    byd_df["considers_toyota"] = byd_df["brands_considering"].fillna("").str.contains(
        r"\bToyota\b", case=False, regex=True
    ).astype(int)
    byd_df["considers_honda"] = byd_df["brands_considering"].fillna("").str.contains(
        r"\bHonda\b", case=False, regex=True
    ).astype(int)

    byd_age_inc = byd_df.dropna(subset=["age_range", "monthly_income"]).copy()
    byd_age_inc["age_range"] = byd_age_inc["age_range"].astype(str)
    byd_age_inc["monthly_income"] = byd_age_inc["monthly_income"].astype(str)

    heat_byd = byd_age_inc.groupby(["age_range", "monthly_income"])["considers_byd"].mean() * 100
    heat_byd = heat_byd.unstack(fill_value=np.nan)
    valid_a3 = [a for a in age_order if a in heat_byd.index]
    valid_i3 = [i for i in income_order if i in heat_byd.columns]
    heat_byd = heat_byd.reindex(valid_a3)[valid_i3]

    heat_n = byd_age_inc.groupby(["age_range", "monthly_income"]).size().unstack(fill_value=0)
    heat_n = heat_n.reindex(valid_a3)
    heat_n = heat_n[[c for c in valid_i3 if c in heat_n.columns]].reindex(columns=valid_i3, fill_value=0)

    text_byd = []
    for a in valid_a3:
        row_t = []
        for i in valid_i3:
            v = heat_byd.loc[a, i] if a in heat_byd.index and i in heat_byd.columns else np.nan
            n = int(heat_n.loc[a, i]) if a in heat_n.index and i in heat_n.columns else 0
            row_t.append(f"{v:.0f}%<br>n={n}" if not np.isnan(v) else f"n={n}")
        text_byd.append(row_t)

    inc_s3 = [i.replace(" THB", "").replace("Below ", "<").replace("Above ", ">") for i in valid_i3]
    fig7 = go.Figure(go.Heatmap(
        z=heat_byd.values.astype(float),
        x=inc_s3,
        y=valid_a3,
        text=text_byd,
        texttemplate="%{text}",
        colorscale="YlGn",
        colorbar=dict(title="% considering BYD"),
        zmin=0, zmax=60,
        hovertemplate="Age %{y} × Income %{x}<br>BYD consideration: %{z:.0f}%<extra></extra>",
    ))
    fig7.update_layout(
        **LAYOUT_BASE,
        title="BYD consideration rate by age × income (% of segment considering BYD)",
        height=380, xaxis_tickangle=-30,
    )
    st.plotly_chart(fig7, use_container_width=True)

    insight_box(
        "Dark green cells = BYD's core market; light/grey cells = untapped or hostile territory. "
        "Focus retention campaigns on dark cells. For light cells, diagnose whether the barrier is "
        "brand trust, product gap, or price mismatch — each requires a different fix."
    )

    st.divider()
    section_header("BYD vs. competitors — consideration rate by age group")

    brands_age = byd_age_inc.groupby("age_range")[
        ["considers_byd", "considers_tesla", "considers_toyota", "considers_honda"]
    ].mean() * 100
    valid_a4 = [a for a in age_order if a in brands_age.index]
    brands_age = brands_age.reindex(valid_a4)

    fig7b = go.Figure()
    brand_map = {
        "considers_byd": ("BYD", "#00A851"),
        "considers_tesla": ("Tesla", "#E31937"),
        "considers_toyota": ("Toyota", "#EB0A1E"),
        "considers_honda": ("Honda", "#CC0000"),
    }
    for col, (label, color) in brand_map.items():
        fig7b.add_trace(go.Scatter(
            x=brands_age.index.tolist(),
            y=brands_age[col].values,
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5),
            marker=dict(size=9),
        ))
    fig7b.update_layout(
        **LAYOUT_BASE,
        title="Brand consideration rate by age group — BYD vs. Tesla vs. Toyota vs. Honda",
        yaxis_title="% of age group considering brand",
        height=380,
        hovermode="x unified",
    )
    st.plotly_chart(fig7b, use_container_width=True)

    insight_box(
        "This shows BYD's age-group penetration gap vs. Japanese brands. "
        "Where Toyota/Honda lead but BYD lags, the root cause is brand trust, not product. "
        "Where Tesla leads but BYD lags among high-income groups, "
        "BYD needs premium positioning and software/feature differentiation."
    )

# ── Tab 8: Barrier Load vs. EV Readiness ─────────────────────────────────────
with tabs[7]:
    section_header(
        "Do more barriers mean less readiness — or do they reveal engaged undecideds?",
        "Scatter: number of barriers cited vs. EV readiness index, coloured by powertrain preference"
    )

    scatter_df = df.copy()
    scatter_df["barrier_count"] = scatter_df["ev_adoption_barriers"].apply(
        lambda x: len(split_multiselect(str(x))) if pd.notna(x) else 0
    )
    scatter_df = scatter_df.dropna(subset=["ev_readiness_index", "powertrain_short"])

    fig8 = go.Figure()
    palette8 = plc.qualitative.Set2
    for i, pt in enumerate([p for p in PT_ORDER if p in scatter_df["powertrain_short"].unique()]):
        sub = scatter_df[scatter_df["powertrain_short"] == pt]
        fig8.add_trace(go.Scatter(
            x=sub["barrier_count"].values,
            y=sub["ev_readiness_index"].values,
            mode="markers",
            name=pt,
            marker=dict(
                color=POWERTRAIN_COLORS.get(pt, palette8[i % len(palette8)]),
                size=9, opacity=0.75,
                line=dict(color="white", width=0.5),
            ),
            hovertemplate=(
                f"<b>{pt}</b><br>"
                "Barriers: %{x}<br>EV Readiness: %{y:.1f}<extra></extra>"
            ),
        ))
    fig8.update_layout(
        **LAYOUT_BASE,
        title="Barrier count vs. EV Readiness Index — coloured by powertrain preference",
        xaxis_title="Number of EV barriers mentioned",
        yaxis_title="EV Readiness Index (1–10)",
        height=440,
        legend_title="Powertrain",
    )
    st.plotly_chart(fig8, use_container_width=True)

    insight_box(
        "Respondents who cite many barriers yet still show moderate-to-high EV readiness are "
        "'informed undecideds' — they've researched EVs enough to identify specific concerns but "
        "haven't been given satisfactory answers. These are BYD's highest-value leads: they are "
        "educated, motivated, and one good conversation (or test drive) away from converting."
    )

    st.divider()
    section_header("Barrier count distribution — who lists the most barriers?")

    bc_age = scatter_df.groupby(scatter_df["age_range"].astype(str))["barrier_count"].mean().round(2)
    bc_inc = scatter_df.groupby(scatter_df["monthly_income"].astype(str))["barrier_count"].mean().round(2)

    col_l, col_r = st.columns(2)
    with col_l:
        valid_a5 = [a for a in age_order if a in bc_age.index]
        bc_age_ordered = bc_age.reindex(valid_a5)
        fig8b = go.Figure(go.Bar(
            x=bc_age_ordered.index.tolist(),
            y=bc_age_ordered.values,
            marker_color="#002D62",
            text=[f"{v:.1f}" for v in bc_age_ordered.values],
            textposition="outside",
        ))
        fig8b.update_layout(
            **LAYOUT_BASE,
            title="Mean # barriers cited — by age group",
            yaxis_title="Mean barrier count",
            height=340,
        )
        st.plotly_chart(fig8b, use_container_width=True)

    with col_r:
        valid_i5 = [i for i in income_order if i in bc_inc.index]
        bc_inc_ordered = bc_inc.reindex(valid_i5)
        inc_labels = [
            i.replace(" THB", "").replace("Below ", "<").replace("Above ", ">")
            for i in bc_inc_ordered.index
        ]
        fig8c = go.Figure(go.Bar(
            x=inc_labels,
            y=bc_inc_ordered.values,
            marker_color="#00A851",
            text=[f"{v:.1f}" for v in bc_inc_ordered.values],
            textposition="outside",
        ))
        fig8c.update_layout(
            **LAYOUT_BASE,
            title="Mean # barriers cited — by income band",
            yaxis_title="Mean barrier count",
            height=340,
            xaxis_tickangle=-25,
        )
        st.plotly_chart(fig8c, use_container_width=True)

    insight_box(
        "Segments with high barrier counts but also high EV readiness are the prime target for "
        "BYD's reassurance content: dedicated FAQs, service-centre maps, BYD owner testimonials, "
        "and partner warranty programmes. Segments with low barrier count but also low readiness "
        "are largely unaware — awareness/education campaigns should address them first."
    )
