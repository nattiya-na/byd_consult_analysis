"""Page 7 — Key findings: survey stats + interview quotes per theme."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import (
    load_survey, sidebar_filters, hbar, explode_and_count, LAYOUT_BASE,
)
from utils.interview_data import THEMES, PROFILES
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Key Findings", layout="wide")
apply_byd_theme()
page_header("Key Findings", "Survey evidence aligned with qualitative interview insights — quantitative signal meets lived experience")

df, age_order, income_order, dd_order = load_survey()
df = sidebar_filters(df, age_order, income_order)

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

profiles_by_id = {p["id"]: p for p in PROFILES}

SEVERITY_COLOR = {"Critical": "#BC4749", "High": "#F18F01", "Moderate": "#6A994E"}

SEVERITY_EMOJI = {"Critical": "🔴", "High": "🟠", "Moderate": "🟡"}

def severity_badge(s: str) -> str:
    emoji = SEVERITY_EMOJI.get(s, "⚪")
    return f"{emoji} {s}"

def render_quote(q: dict) -> None:
    prof = profiles_by_id.get(q["id"], {})
    age = prof.get("age", "?")
    gender = prof.get("gender", "?")
    persona = prof.get("persona", "?")
    st.markdown(
        f'<div style="border-left:4px solid #00A851;padding:10px 14px;margin:8px 0;'
        f'background:#F8FBF8;border-radius:0 6px 6px 0">'
        f'<em style="color:#1A1A2E">"{q["text"]}"</em><br>'
        f'<small style="color:#6B7280;margin-top:4px;display:block">— Respondent #{q["id"]} · Age {age} · {gender} · Persona {persona}</small>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Theme 1: After-sales ───────────────────────────────────────────────────────
with st.expander(f"🔧 After-Sales Service Quality  {severity_badge('Critical')}", expanded=True):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal**")
        vc_b = explode_and_count(df, "ev_adoption_barriers", top_n=8)
        after_sales_kws = ["after", "service", "maintenance", "repair", "support"]
        after_sales_count = sum(
            cnt for b, cnt in vc_b.items()
            if any(kw in b.lower() for kw in after_sales_kws)
        )
        st.metric("After-sales mentions in barriers", after_sales_count)

        fig_b = go.Figure(go.Bar(
            x=vc_b.values[::-1], y=vc_b.index[::-1].tolist(),
            orientation="h", marker_color="#BC4749",
        ))
        fig_b.update_layout(**LAYOUT_BASE, title="Top EV barriers (survey)", height=300)
        st.plotly_chart(fig_b, use_container_width=True)

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["after_sales"]["quotes"]:
            render_quote(q)

    st.info("**Alignment:** Survey and interviews agree — after-sales is the #1 veto, not price. "
            "Respondents with no experience of BYD service still rate this high based on secondhand accounts.")

# ── Theme 2: Charging ──────────────────────────────────────────────────────────
with st.expander(f"⚡ Charging Infrastructure & Range Anxiety  {severity_badge('Critical')}"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal — Charging convenience distribution**")
        chg_vc = df["charging_convenience"].value_counts()
        fig_chg = go.Figure(go.Bar(
            x=chg_vc.values, y=[s[:40] for s in chg_vc.index.tolist()],
            orientation="h", marker_color="#2E86AB",
        ))
        fig_chg.update_layout(**LAYOUT_BASE, title="Charging convenience (survey)", height=300)
        st.plotly_chart(fig_chg, use_container_width=True)

        ev_ri_by_chg = df.groupby(
            df["charging_convenience"].str[:35]
        )["ev_readiness_index"].mean().sort_values(ascending=False)
        st.caption("Mean EV Readiness by charging access:")
        st.dataframe(ev_ri_by_chg.round(2).rename("Mean EV Readiness"), use_container_width=True)

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["charging"]["quotes"]:
            render_quote(q)

    st.info("**Tension:** Survey shows ~40% of respondents have convenient home charging. "
            "Yet interviews reveal that even those with chargers installed cite public infrastructure "
            "as a major travel-day anxiety. The barrier is psychological as much as physical.")

# ── Theme 3: Design ────────────────────────────────────────────────────────────
with st.expander(f"🎨 Interior Design as Deal-Breaker  {severity_badge('Critical')}"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal — Purchase factors**")
        vc_pf = explode_and_count(df, "purchase_factors_top3", top_n=10)
        design_kws = ["design", "aesthetic", "look", "style", "appearance", "interior"]
        design_count = sum(
            cnt for b, cnt in vc_pf.items()
            if any(kw in b.lower() for kw in design_kws)
        )
        st.metric("Design/aesthetics in top-3 factors", design_count)
        fig_pf = go.Figure(go.Bar(
            x=vc_pf.values[::-1], y=vc_pf.index[::-1].tolist(),
            orientation="h", marker_color="#F18F01",
        ))
        fig_pf.update_layout(**LAYOUT_BASE, title="Top purchase factors (survey)", height=360)
        st.plotly_chart(fig_pf, use_container_width=True)

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["design"]["quotes"]:
            render_quote(q)

    st.info("**Tension:** Survey data groups design broadly. Interviews reveal it is specifically the "
            "**black-red interior color scheme** — not design in general — that acts as an active veto. "
            "Two respondents who have never met each other independently named this as their deal-breaker.")

# ── Theme 4: Depreciation ──────────────────────────────────────────────────────
with st.expander(f"📉 Price Depreciation Erodes Trust  {severity_badge('Critical')}"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal — Purchase factor: price/value**")
        price_kws = ["price", "cost", "value", "afford", "budget", "depreciat"]
        vc_pf2 = explode_and_count(df, "purchase_factors_top3", top_n=15)
        price_count = sum(cnt for b, cnt in vc_pf2.items()
                         if any(kw in b.lower() for kw in price_kws))
        st.metric("Price/value mentions in top-3 factors", price_count)

        # Budget distribution
        budget_vc = df["budget_range"].value_counts()
        fig_budget = go.Figure(go.Bar(
            x=budget_vc.values[::-1], y=[s[:35] for s in budget_vc.index[::-1].tolist()],
            orientation="h", marker_color="#A23B72",
        ))
        fig_budget.update_layout(**LAYOUT_BASE, title="Budget range distribution", height=300)
        st.plotly_chart(fig_budget, use_container_width=True)

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["depreciation"]["quotes"]:
            render_quote(q)

    st.info("**Insight:** Price sensitivity in the survey looks like 'buyers want cheaper cars'. "
            "Interviews reveal the real issue is **price stability** — rapid discounts break purchase "
            "confidence retroactively and signal poor quality. The fix is pricing discipline, not lower prices.")

# ── Theme 5: PHEV misunderstood ────────────────────────────────────────────────
with st.expander(f"🔌 PHEV Misunderstood Across All Segments  {severity_badge('High')}"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal — PHEV consideration rate**")
        from survey_utils import PT_ORDER
        cons_exploded = []
        for val in df["powertrain_considering"].dropna():
            for tok in str(val).split(";"):
                t = tok.strip()
                if t:
                    cons_exploded.append(t)
        cons_vc = pd.Series(cons_exploded).value_counts()
        total = len(df)
        for pt in ["BEV", "PHEV", "REEV", "HEV"]:
            matches = sum(cnt for label, cnt in cons_vc.items() if pt.lower() in label.lower())
            st.metric(f"{pt} consideration rate", f"{matches/total*100:.0f}%", f"{matches} mentions")

        phev_familiarity = pd.to_numeric(df["familiarity_phev"], errors="coerce")
        st.metric("Mean PHEV familiarity score (1–5)", f"{phev_familiarity.mean():.2f}")

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["phev"]["quotes"]:
            render_quote(q)

    st.info("**Insight:** PHEV has the lowest familiarity score of all powertrain types. "
            "Interviews show the barrier is not PHEV's actual drawbacks — it is a fundamental "
            "**awareness gap**: most respondents have never seen a clear PHEV vs BEV explanation. "
            "One respondent (Profile #6, age 50) had never heard the term before the interview.")

# ── Theme 6: Brand trust ───────────────────────────────────────────────────────
with st.expander(f"🏷️ Chinese Brand Trust Gap  {severity_badge('Critical')}"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Survey signal — BYD vs. Toyota/Honda consideration**")
        byd_mask = df["brands_considering"].fillna("").str.contains(r"\bBYD\b", case=False, regex=True)
        th_mask = (
            df["brands_considering"].fillna("").str.contains(r"\btoyota\b", case=False, regex=True) |
            df["brands_considering"].fillna("").str.contains(r"\bhonda\b", case=False, regex=True)
        )
        st.metric("BYD consideration rate", f"{byd_mask.mean()*100:.1f}%")
        st.metric("Toyota/Honda consideration rate", f"{th_mask.mean()*100:.1f}%")
        st.metric("Gap (Toyota/Honda advantage)", f"{(th_mask.mean() - byd_mask.mean())*100:.1f} pct points")

        # BYD not-considering reasons
        fig_nc = hbar(df["byd_not_considering_reason"], "Reasons NOT to consider BYD (survey)", color="Reds")
        fig_nc.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_nc, use_container_width=True)

    with col2:
        st.markdown("**Interview quotes**")
        for q in THEMES["brand_trust"]["quotes"]:
            render_quote(q)

    st.info("**Insight:** The survey shows BYD's consideration rate is lower than Toyota/Honda. "
            "Interviews reveal the underlying reason: it is not product quality but **long-term "
            "brand survivability** that is in question. Respondents fear being abandoned — not "
            "outperformed. This requires brand stability signalling, not product improvements.")
