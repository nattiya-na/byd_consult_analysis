"""Page 1 — Demographics & sample composition."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as plc
from plotly.subplots import make_subplots
import streamlit as st

from utils.data_loader import load_survey, sidebar_filters, hbar, heatmap_pct, stacked_bar_pct, LAYOUT_BASE, SOURCE_LABELS
from survey_utils import PT_ORDER, POWERTRAIN_COLORS, HH_PROXY_ORDER, split_multiselect
from utils.styles import apply_byd_theme, page_header, section_header

st.set_page_config(page_title="Demographics", layout="wide")
apply_byd_theme()
page_header("Demographics & Sample Composition", "Who responded: age, gender, income, location, occupation")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Data source breakdown ──────────────────────────────────────────────────────
st.subheader("Sample composition")
c1, c2, c3 = st.columns(3)
for col, src in zip([c1, c2, c3], ["general", "motor_show", "survey_china"]):
    n = (df["data_source"] == src).sum()
    col.metric(SOURCE_LABELS[src], f"{n:,}", f"{n/len(df)*100:.0f}% of total")

# Source bar
fig_src = hbar(df["data_source"].map(SOURCE_LABELS), "Respondents by data source", color="Blues")
st.plotly_chart(fig_src, use_container_width=True)

st.divider()

# ── Age, gender, income ────────────────────────────────────────────────────────
st.subheader("Core demographics")

tab_age, tab_gender, tab_income, tab_location, tab_occupation, tab_distance = st.tabs(
    ["Age", "Gender", "Income", "Location", "Occupation", "Driving distance"]
)

with tab_age:
    fig = hbar(
        df["age_range"].cat.remove_unused_categories(),
        "Respondents by age group",
        color="Viridis",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_gender:
    vc = df["gender"].value_counts()
    fig_g = go.Figure()
    fig_g.add_trace(go.Pie(
        labels=vc.index.tolist(), values=vc.values.tolist(),
        hole=0.4, textinfo="label+percent",
        marker=dict(colors=["#2E86AB", "#A23B72", "#F18F01", "#6A994E"]),
    ))
    fig_g.update_layout(**LAYOUT_BASE, title="Gender distribution", height=380)
    st.plotly_chart(fig_g, use_container_width=True)

with tab_income:
    inc_series = df["monthly_income"].cat.remove_unused_categories()
    fig = hbar(inc_series, "Respondents by monthly income", color="Purples")
    st.plotly_chart(fig, use_container_width=True)

with tab_location:
    fig = hbar(df["location"], "Respondents by location (top 20)", top_n=20, color="Teal")
    st.plotly_chart(fig, use_container_width=True)

with tab_occupation:
    fig = hbar(df["occupation"], "Respondents by occupation", color="Oranges")
    st.plotly_chart(fig, use_container_width=True)

with tab_distance:
    dd_series = df["daily_driving_distance"].cat.remove_unused_categories()
    fig = hbar(dd_series, "Daily driving distance", color="Blues")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Cross-demographic heatmaps ─────────────────────────────────────────────────
st.subheader("Demographics cross-cuts")
col1, col2 = st.columns(2)

with col1:
    fig = heatmap_pct(df, "age_range", "gender", "Age × Gender (row %)",
                      row_order=age_order, colorscale="Blues")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = heatmap_pct(df, "age_range", "monthly_income", "Age × Income (row %)",
                      row_order=age_order, col_order=income_order, colorscale="Purples")
    st.plotly_chart(fig, use_container_width=True)

fig = heatmap_pct(df, "monthly_income", "daily_driving_distance",
                  "Income × Driving distance (row %)",
                  row_order=income_order, col_order=dd_order, colorscale="Teal")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Household & Family Needs ───────────────────────────────────────────────────
section_header(
    "Household & Family Car Needs",
    "Who lives in the household, how many cars they own, and how that shapes the car they want",
)

# ── Feature engineering ────────────────────────────────────────────────────────
def _hh_proxy(row) -> str:
    c = row["cars_owned_count_n"]
    h = row["household_size_n"]
    if pd.isna(c) or pd.isna(h) or h == 0:
        return np.nan
    c, h = int(c), int(h)
    if c == 0:
        return "No car"
    if c < h:
        return "≥1 car, fewer cars than people"
    if c == h:
        return "≥1 car, as many cars as number of people"
    return "≥1 car, more cars than people"

df["hh_vehicle_proxy"] = df.apply(_hh_proxy, axis=1)
df["cars_per_person"] = (
    df["cars_owned_count_n"] / df["household_size_n"].replace(0, np.nan)
)

# ── KPI strip ──────────────────────────────────────────────────────────────────
hh_valid = df["household_size_n"].dropna()
cars_valid = df["cars_owned_count_n"].dropna()
joint_pct = df["purchase_decision_role"].str.contains(
    "share|influence", case=False, na=False
).mean() * 100
multi_car_pct = (cars_valid >= 2).mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Modal household size", f"{int(hh_valid.mode()[0])} people",
          f"mean {hh_valid.mean():.1f}")
k2.metric("Mean cars per household", f"{cars_valid.mean():.1f}",
          f"{(cars_valid >= 2).sum()} households ≥2 cars")
k3.metric("Multi-car households (≥2)", f"{multi_car_pct:.0f}%")
k4.metric("Joint purchase decision", f"{joint_pct:.0f}%",
          "shared or influenced")
k5.metric("'No car' households", f"{(cars_valid == 0).sum()}",
          "pure first-time buyers")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
hh_tabs = st.tabs([
    "Household size",
    "Cars owned",
    "Car density (HH proxy)",
    "Family size × Powertrain",
    "Current cars → Next car",
    "Decision role",
])

# Tab 1 — Household size distribution
with hh_tabs[0]:
    hh_vc = hh_valid.value_counts().sort_index()
    palette = plc.sample_colorscale("Blues", [i / max(1, len(hh_vc) - 1) for i in range(len(hh_vc))])
    fig_hh = go.Figure(go.Bar(
        x=[f"{int(v)} people" for v in hh_vc.index],
        y=hh_vc.values,
        marker_color=palette,
        text=hh_vc.values,
        textposition="outside",
    ))
    fig_hh.update_layout(
        **LAYOUT_BASE,
        title="Household size distribution",
        xaxis_title="Household size",
        yaxis_title="Count",
        height=380,
    )
    st.plotly_chart(fig_hh, use_container_width=True)
    st.info(
        "**Insight:** The 4-person household (2 adults + 2 children) is by far the most common "
        "profile — 76 respondents. This is the Thai nuclear family. BYD should design its "
        "family-car messaging around a 5-seat, practical daily driver with enough boot space "
        "and ADAS for school runs and weekend trips."
    )

# Tab 2 — Cars owned distribution
with hh_tabs[1]:
    cars_vc = cars_valid.astype(int).value_counts().sort_index()
    car_labels = {0: "0 — no car", 1: "1 car", 2: "2 cars", 3: "3 cars",
                  4: "4 cars", 5: "5+ cars"}
    palette2 = plc.sample_colorscale("Reds", [i / max(1, len(cars_vc) - 1) for i in range(len(cars_vc))])
    fig_cars = go.Figure(go.Bar(
        x=[car_labels.get(int(v), f"{int(v)} cars") for v in cars_vc.index],
        y=cars_vc.values,
        marker_color=palette2,
        text=cars_vc.values,
        textposition="outside",
    ))
    fig_cars.update_layout(
        **LAYOUT_BASE,
        title="Cars currently owned per household",
        xaxis_title="Number of cars",
        yaxis_title="Count",
        height=380,
    )
    st.plotly_chart(fig_cars, use_container_width=True)

    # Cars owned × income heatmap
    inc_cars = df.dropna(subset=["monthly_income", "cars_owned_count_n"]).copy()
    inc_cars["cars_owned_count_n"] = inc_cars["cars_owned_count_n"].astype(int)
    ct_ic = pd.crosstab(
        inc_cars["monthly_income"].astype(str),
        inc_cars["cars_owned_count_n"],
        normalize="index",
    ) * 100
    valid_inc = [i for i in income_order if i in ct_ic.index]
    ct_ic = ct_ic.reindex(valid_inc)
    inc_short = [i.replace(" THB", "").replace("Below ", "<").replace("Above ", ">") for i in valid_inc]
    fig_ic = go.Figure(go.Heatmap(
        z=ct_ic.values.astype(float),
        x=[f"{int(c)} car{'s' if c != 1 else ''}" for c in ct_ic.columns],
        y=inc_short,
        text=[[f"{v:.0f}%" for v in r] for r in ct_ic.values],
        texttemplate="%{text}",
        colorscale="YlOrRd",
        colorbar=dict(title="% of income"),
        hovertemplate="%{y} → %{x}: %{z:.1f}%<extra></extra>",
    ))
    fig_ic.update_layout(
        **LAYOUT_BASE,
        title="Income band × cars owned (row %) — does income predict car count?",
        height=360,
    )
    st.plotly_chart(fig_ic, use_container_width=True)
    st.info(
        "**Insight:** Mean 2.7 cars per household — this is a car-saturated market. "
        "Most EV buyers are adding a new car or replacing one, not buying their first. "
        "High-income households (100k+ THB) skew toward 3–5 cars, making them "
        "replacement/upgrade buyers rather than first-time EV converts."
    )

# Tab 3 — Car density (HH proxy) × powertrain
with hh_tabs[2]:
    proxy_vc = df["hh_vehicle_proxy"].value_counts()
    valid_proxy = [p for p in HH_PROXY_ORDER if p in proxy_vc.index]

    col_a, col_b = st.columns([1, 2])
    with col_a:
        proxy_colors = ["#6b7280", "#d70c19", "#f59e0b", "#1a1a1a"]
        fig_pv = go.Figure(go.Bar(
            x=[proxy_vc.get(p, 0) for p in valid_proxy],
            y=[p.replace("≥1 car, ", "") for p in valid_proxy],
            orientation="h",
            marker_color=proxy_colors[:len(valid_proxy)],
            text=[proxy_vc.get(p, 0) for p in valid_proxy],
            textposition="outside",
        ))
        fig_pv.update_layout(
            **LAYOUT_BASE,
            title="Car density (cars vs. household people)",
            height=320,
        )
        st.plotly_chart(fig_pv, use_container_width=True)

    with col_b:
        sub_proxy = df.dropna(subset=["hh_vehicle_proxy", "powertrain_short"])
        ct_pp = pd.crosstab(
            sub_proxy["hh_vehicle_proxy"], sub_proxy["powertrain_short"], normalize="index"
        ) * 100
        ct_pp = ct_pp.reindex([p for p in HH_PROXY_ORDER if p in ct_pp.index])
        valid_pt = [p for p in PT_ORDER if p in ct_pp.columns]
        ct_pp = ct_pp[valid_pt]

        fig_pp = go.Figure()
        for pt in valid_pt:
            vals = ct_pp[pt].values
            fig_pp.add_trace(go.Bar(
                name=pt,
                x=[p.replace("≥1 car, ", "") for p in ct_pp.index],
                y=vals,
                marker_color=POWERTRAIN_COLORS.get(pt),
                text=[f"{v:.0f}%" if v >= 6 else "" for v in vals],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_pp.update_layout(
            **LAYOUT_BASE,
            barmode="stack",
            title="Car density group × powertrain preference (row %)",
            yaxis_title="% within group",
            height=320,
        )
        st.plotly_chart(fig_pp, use_container_width=True)

    st.info(
        "**Key PMF finding:** Households with *fewer cars than people* (the largest group, n=146) "
        "show the **strongest BEV preference at 43%** — they need a practical gap-filler car for "
        "daily commuting. Households with *as many cars as people* (n=46) flip to **30% PHEV** — "
        "they want a flexible upgrade, not a pure city runaround. "
        "Multi-car, car-dense households (more cars than people) split between BEV and PHEV, "
        "suggesting they treat the new purchase as either a premium daily or a long-range weekend car."
    )

# Tab 4 — Family size (household_size_n) × powertrain
with hh_tabs[3]:
    fam_pt = df.dropna(subset=["household_size_n", "powertrain_short"]).copy()
    fam_pt["hh_size_grp"] = fam_pt["household_size_n"].apply(
        lambda x: "1–2 people" if x <= 2
        else ("3–4 people" if x <= 4 else "5+ people")
    )
    HH_GRP_ORDER = ["1–2 people", "3–4 people", "5+ people"]

    ct_fp = pd.crosstab(fam_pt["hh_size_grp"], fam_pt["powertrain_short"], normalize="index") * 100
    ct_fp = ct_fp.reindex([g for g in HH_GRP_ORDER if g in ct_fp.index])
    valid_pt2 = [p for p in PT_ORDER if p in ct_fp.columns]

    fig_fp = go.Figure()
    for pt in valid_pt2:
        vals = ct_fp[pt].values
        fig_fp.add_trace(go.Bar(
            name=pt,
            x=ct_fp.index.tolist(),
            y=vals,
            marker_color=POWERTRAIN_COLORS.get(pt),
            text=[f"{v:.0f}%" if v >= 5 else "" for v in vals],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_fp.update_layout(
        **LAYOUT_BASE,
        barmode="stack",
        title="Household size group × powertrain preference (row %)",
        yaxis_title="% within household size group",
        height=380,
    )
    st.plotly_chart(fig_fp, use_container_width=True)

    # Box plot: household_size_n by powertrain
    fig_box = go.Figure()
    colors_box = plc.qualitative.Set2
    for i, pt in enumerate([p for p in PT_ORDER if p in fam_pt["powertrain_short"].unique()]):
        sub = fam_pt[fam_pt["powertrain_short"] == pt]["household_size_n"]
        fig_box.add_trace(go.Box(
            y=sub, name=f"{pt}<br>(n={len(sub)})",
            marker_color=POWERTRAIN_COLORS.get(pt, colors_box[i % len(colors_box)]),
            boxmean=True,
        ))
    fig_box.update_layout(
        **LAYOUT_BASE,
        title="Household size distribution by powertrain first choice",
        yaxis_title="People in household",
        height=380,
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.info(
        "**Insight:** REEV buyers have the **largest median household size (5 people)** — "
        "bigger families need the range reassurance that a fuel generator provides. "
        "3–4 person households (the modal Thai family) are split roughly evenly between "
        "BEV and HEV/PHEV, suggesting BYD should offer a clear '4-person family' story for "
        "both the Atto 3 (BEV) and the Song DM-i (PHEV). "
        "1–2 person households lean BEV most strongly — urban singles and couples "
        "have no range anxiety and just need a clean, connected commuter."
    )

# Tab 5 — Current powertrains owned → next car preference
with hh_tabs[4]:
    CURRENT_PT_CLEAN = {
        "ICE:": "ICE",
        "HEV: +": "HEV",
        "BEV:": "BEV",
        "PHEV: +": "PHEV",
        "Range-extended electric vehicle: electric drive with fuel generator": "REEV",
        "Do not own a car": "No car",
    }
    upgrade_rows = []
    for idx, row in df.iterrows():
        next_pt = row["powertrain_short"]
        current_raw = row["current_powertrains_owned"]
        if pd.isna(current_raw) or pd.isna(next_pt):
            continue
        seen = set()
        for tok in split_multiselect(str(current_raw)):
            tok = tok.strip()
            label = CURRENT_PT_CLEAN.get(tok)
            if label and label not in seen:
                upgrade_rows.append({"current": label, "next": next_pt})
                seen.add(label)

    if upgrade_rows:
        up_df = pd.DataFrame(upgrade_rows)
        CURR_ORDER = ["No car", "ICE", "HEV", "PHEV", "BEV", "REEV"]
        ct_up = pd.crosstab(up_df["current"], up_df["next"], normalize="index") * 100
        ct_up = ct_up.reindex([c for c in CURR_ORDER if c in ct_up.index])
        valid_next = [p for p in PT_ORDER if p in ct_up.columns]
        ct_up = ct_up[valid_next]

        fig_up = go.Figure()
        for pt in valid_next:
            vals = ct_up[pt].values
            fig_up.add_trace(go.Bar(
                name=pt,
                x=ct_up.index.tolist(),
                y=vals,
                marker_color=POWERTRAIN_COLORS.get(pt),
                text=[f"{v:.0f}%" if v >= 6 else "" for v in vals],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_up.update_layout(
            **LAYOUT_BASE,
            barmode="stack",
            title="Current powertrain owned → next car powertrain preference (row %)",
            xaxis_title="Currently own",
            yaxis_title="% choosing each next powertrain",
            height=400,
        )
        st.plotly_chart(fig_up, use_container_width=True)

        # Counts table
        ct_abs = pd.crosstab(up_df["current"], up_df["next"])
        ct_abs = ct_abs.reindex([c for c in CURR_ORDER if c in ct_abs.index])
        st.caption("Absolute counts (current → next):")
        st.dataframe(ct_abs, use_container_width=True)

        st.info(
            "**Upgrade path insight:** Current ICE owners split between BEV and HEV for their "
            "next car — they are not yet all-in on full electric. Current HEV owners show higher "
            "BEV intent than any other group, suggesting HEV is the natural stepping stone to BEV. "
            "Current PHEV owners are most likely to choose BEV next — reinforcing that PHEV is a "
            "transitional technology, not a destination. "
            "**Implication for BYD:** Target current HEV and PHEV owners for BEV upsell; "
            "target ICE owners with the Song DM-i PHEV as a lower-anxiety first step."
        )

# Tab 6 — Purchase decision role
with hh_tabs[5]:
    role_vc = df["purchase_decision_role"].value_counts()
    ROLE_COLORS = ["#d70c19", "#1a1a1a", "#6b7280", "#e2ddd6"]
    fig_role = go.Figure(go.Pie(
        labels=role_vc.index.tolist(),
        values=role_vc.values.tolist(),
        hole=0.42,
        textinfo="label+percent",
        marker=dict(colors=ROLE_COLORS[:len(role_vc)]),
        textfont=dict(size=12),
    ))
    fig_role.update_layout(
        **LAYOUT_BASE,
        title="Purchase decision role — who decides?",
        height=380,
    )
    st.plotly_chart(fig_role, use_container_width=True)

    # Decision role × powertrain
    role_pt = df.dropna(subset=["purchase_decision_role", "powertrain_short"]).copy()
    ct_rp = pd.crosstab(role_pt["purchase_decision_role"], role_pt["powertrain_short"], normalize="index") * 100
    valid_pt3 = [p for p in PT_ORDER if p in ct_rp.columns]
    ct_rp = ct_rp[valid_pt3]

    # Short role labels
    role_short = {
        "I am the primary decision-maker": "Primary decision-maker",
        "I share the decision with others": "Shared decision",
        "I influence the decision but am not the final decision-maker": "Influencer",
        "I am not involved": "Not involved",
    }
    ct_rp.index = [role_short.get(r, r[:35]) for r in ct_rp.index]

    fig_rp = go.Figure()
    for pt in valid_pt3:
        vals = ct_rp[pt].values
        fig_rp.add_trace(go.Bar(
            name=pt,
            x=ct_rp.index.tolist(),
            y=vals,
            marker_color=POWERTRAIN_COLORS.get(pt),
            text=[f"{v:.0f}%" if v >= 6 else "" for v in vals],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_rp.update_layout(
        **LAYOUT_BASE,
        barmode="stack",
        title="Purchase decision role × powertrain preference (row %)",
        yaxis_title="% within role",
        height=380,
        xaxis_tickangle=-15,
    )
    st.plotly_chart(fig_rp, use_container_width=True)

    st.info(
        "**Insight:** ~32% of respondents share or only influence the purchase decision — "
        "meaning the car must pass a *household veto*, not just satisfy one buyer. "
        "This is why design and interior quality rank so high: a partner or parent "
        "will reject a car on looks alone. "
        "BYD's marketing should address the whole household, not just the test-driver — "
        "family lifestyle imagery, spaciousness, and safety features matter beyond the spec sheet."
    )
