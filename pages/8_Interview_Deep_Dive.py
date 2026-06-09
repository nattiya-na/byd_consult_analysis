"""Page 8 — Interview deep dive: profiles, personas, theme browser, barriers heatmap, sales staff."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.interview_data import (
    PROFILES, PERSONAS, BARRIERS_TABLE, THEMES, RECOMMENDATIONS,
    COHORT_QUOTES, get_theme_quotes, load_all_raw_quotes,
)
from utils.sales_interview_data import (
    SALES_PROFILES, SALES_THEMES, LOST_SALES_REASONS, load_sales_pdf_text,
)
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Interview Deep Dive", layout="wide")
apply_byd_theme()
page_header(
    "Interview Deep Dive",
    "19 consumer in-depth interviews + 5 BYD sales staff interviews — profiles, personas, barrier analysis, and dealer-side insights",
)

SEVERITY_ICON = {"Critical": "🔴", "High": "🟠", "Moderate": "🟡"}

# ══════════════════════════════════════════════════════════════════════════════
tab_profiles, tab_personas, tab_themes, tab_barriers, tab_recs, tab_sales, tab_age = st.tabs([
    "Respondent Profiles",
    "Four Personas",
    "Theme Browser",
    "Barriers Heatmap",
    "Strategic Recommendations",
    "Sales Staff Insights",
    "Voices by Age",
])

# ── Respondent Profiles ────────────────────────────────────────────────────────
with tab_profiles:
    st.subheader("All 19 in-depth interview respondents")

    prof_df = pd.DataFrame(PROFILES)
    prof_df["home_charger"] = prof_df["home_charger"].map({True: "✅", False: "❌"})
    prof_df["byd_score"] = prof_df["byd_score"].apply(lambda x: "⭐" * x + "☆" * (10 - x))
    display_cols = ["id", "age", "gender", "income", "housing", "home_charger",
                    "current_car", "km_day", "powertrain_pref", "byd_attitude", "persona", "source"]
    prof_display = prof_df[display_cols].rename(columns={
        "id": "#", "age": "Age", "gender": "G", "income": "Income (THB)",
        "housing": "Housing", "home_charger": "Charger", "current_car": "Current car",
        "km_day": "km/day", "powertrain_pref": "Pref powertrain",
        "byd_attitude": "BYD attitude", "persona": "Persona", "source": "Source",
    })

    col_f1, col_f2, col_f3 = st.columns(3)
    persona_filter = col_f1.multiselect("Filter by persona", ["A", "B", "C", "D"], default=["A", "B", "C", "D"])
    gender_filter = col_f2.multiselect("Gender", ["M", "F"], default=["M", "F"])
    charger_filter = col_f3.multiselect("Home charger", ["✅", "❌"], default=["✅", "❌"])

    mask = (
        prof_df["persona"].isin(persona_filter) &
        prof_df["gender"].isin(gender_filter) &
        prof_df["home_charger"].isin(charger_filter)
    )
    st.dataframe(prof_display[mask], use_container_width=True, height=500)

    # Summary stats
    st.divider()
    raw_df = pd.DataFrame(PROFILES)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total respondents", len(raw_df))
    c2.metric("With home charger", f"{raw_df['home_charger'].sum()} / {len(raw_df)}")
    c3.metric("Mean BYD attitude score", f"{raw_df['byd_score'].mean():.1f} / 10")
    c4.metric("Age range", f"{raw_df['age'].min()}–{raw_df['age'].max()} years")

# ── Four Personas ──────────────────────────────────────────────────────────────
with tab_personas:
    st.subheader("The four buyer personas")

    for key, persona in PERSONAS.items():
        color = persona["color"]
        profiles_in = [p for p in PROFILES if p["id"] in persona["profiles"]]
        avg_byd = np.mean([p["byd_score"] for p in profiles_in])

        with st.expander(
            f"**Persona {key} — {persona['name']}**   "
            f"({len(persona['profiles'])} respondents · BYD score avg {avg_byd:.1f}/10)",
            expanded=(key == "A"),
        ):
            cols = st.columns([2, 1])
            with cols[0]:
                st.markdown(f"**Who they are:** {persona['who']}")
                st.markdown("**Lifestyle needs:**")
                for need in persona["needs"]:
                    st.markdown(f"- {need}")

            with cols[1]:
                st.markdown("**Respondent IDs in this persona:**")
                for p in profiles_in:
                    st.markdown(f"- #{p['id']}: Age {p['age']} · {p['gender']} · {p['income']}")

            st.markdown("**Key barriers (ranked by severity):**")
            for barrier, severity in persona["barriers"]:
                icon = SEVERITY_ICON.get(severity, "⚪")
                st.markdown(f"{icon} **{severity}** — {barrier}")

            st.markdown("---")
            st.markdown(f"**Key message to convert them:**")
            st.info(persona["key_message"])

# ── Theme Browser ──────────────────────────────────────────────────────────────
with tab_themes:
    st.subheader("Browse themes and quotes")

    theme_options = {f"{v['icon']} {v['label']}": k for k, v in THEMES.items()}
    selected_theme_label = st.selectbox("Select a theme", list(theme_options.keys()))
    selected_theme = theme_options[selected_theme_label]
    theme_data = THEMES[selected_theme]

    sev = theme_data["severity"]
    st.markdown(
        f"**Severity:** {SEVERITY_ICON.get(sev, '')} {sev} &nbsp;|&nbsp; "
        f"**Survey signal:** _{theme_data['survey_signal']}_",
        unsafe_allow_html=True,
    )
    st.divider()

    quotes = get_theme_quotes(selected_theme)
    for q in quotes:
        col_q, col_meta = st.columns([3, 1])
        with col_q:
            st.markdown(
                f'<div style="border-left:4px solid {PERSONAS.get(q.get("persona","A"), {}).get("color","#00A851")};'
                f'padding:10px 14px;margin:8px 0;background:#F8FBF8;border-radius:0 6px 6px 0">'
                f'<em style="color:#1A1A2E">"{q["text"]}"</em>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_meta:
            persona_name = PERSONAS.get(q.get("persona", ""), {}).get("name", "Unknown")
            st.markdown(
                f"**#{q['id']}** · Age {q.get('age','?')} · {q.get('gender','?')}\n\n"
                f"**Persona {q.get('persona','?')}:** {persona_name}\n\n"
                f"**Pref:** {q.get('powertrain_pref','?')}"
            )
        st.markdown("")

    # Raw transcript excerpts (English interviews only)
    st.divider()
    with st.expander("View raw interview excerpts (English interviews — IDs 13–19)"):
        raw_quotes = load_all_raw_quotes()
        english_ids = list(range(13, 20))
        theme_keywords = {
            "after_sales": ["service", "maintenance", "repair", "center", "technician", "scratch", "wait", "parts"],
            "charging": ["charg", "charging station", "public charge", "range", "km", "battery"],
            "design": ["design", "interior", "color", "colour", "look", "aesthetic", "black", "red", "seat"],
            "depreciation": ["price", "depreciat", "drop", "resale", "value", "discount"],
            "phev": ["phev", "plug-in", "plug in", "hybrid", "two system", "complex"],
            "brand_trust": ["chinese", "japanese", "toyota", "honda", "trust", "stable", "stability", "leave"],
        }
        kws = theme_keywords.get(selected_theme, [])
        shown = 0
        for rid in english_ids:
            paragraphs = raw_quotes.get(rid, [])
            for para in paragraphs:
                if any(kw.lower() in para.lower() for kw in kws) and len(para) > 40:
                    prof = next((p for p in PROFILES if p["id"] == rid), {})
                    st.markdown(
                        f'<div style="border-left:3px solid #002D62;padding:8px 12px;margin:4px 0;'
                        f'background:#F5F7FA;font-size:0.88em;border-radius:0 6px 6px 0;color:#1A1A2E">'
                        f'{para}'
                        f'<br><small style="color:#6B7280;margin-top:3px;display:block">Respondent #{rid} · Age {prof.get("age","?")} · {prof.get("gender","?")}</small>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    shown += 1
                    if shown >= 15:
                        break
            if shown >= 15:
                break
        if shown == 0:
            st.caption("No English transcript excerpts matched this theme.")

# ── Barriers Heatmap ───────────────────────────────────────────────────────────
with tab_barriers:
    st.subheader("Barriers × Personas — severity heatmap")
    st.caption("Based on qualitative analysis of 19 in-depth interviews (interview_insights.md)")

    all_barriers = [b["barrier"] for b in BARRIERS_TABLE]
    all_personas = ["A", "B", "C", "D"]
    severity_to_num = {"Critical": 3, "High": 2, "Moderate": 1, "None": 0}
    num_to_label = {3: "Critical", 2: "High", 1: "Moderate", 0: "–"}

    z = []
    text = []
    for barrier_row in BARRIERS_TABLE:
        row_z = []
        row_t = []
        for p in all_personas:
            if p in barrier_row["personas"]:
                sev = barrier_row["severity"]
                row_z.append(severity_to_num[sev])
                row_t.append(sev)
            else:
                row_z.append(0)
                row_t.append("–")
        z.append(row_z)
        text.append(row_t)

    fig_heat = go.Figure(go.Heatmap(
        z=z,
        x=[f"Persona {p} — {PERSONAS[p]['name']}" for p in all_personas],
        y=[b[:55] + ("…" if len(b) > 55 else "") for b in all_barriers],
        text=text,
        texttemplate="%{text}",
        colorscale=[[0, "#f0f0f0"], [0.34, "#6A994E"], [0.67, "#F18F01"], [1.0, "#BC4749"]],
        colorbar=dict(
            tickvals=[0, 1, 2, 3],
            ticktext=["–", "Moderate", "High", "Critical"],
            title="Severity",
        ),
        hovertemplate="Barrier: %{y}<br>Persona: %{x}<br>Severity: %{text}<extra></extra>",
        zmin=0, zmax=3,
    ))
    fig_heat.update_layout(
        title="Barrier severity by persona",
        height=max(500, 32 * len(all_barriers)),
        margin=dict(l=20, r=20, t=55, b=40),
        font=dict(size=11),
        template="plotly_white",
    )
    fig_heat.update_xaxes(tickangle=-15)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.dataframe(
        pd.DataFrame(BARRIERS_TABLE)[["barrier", "personas", "severity"]].assign(
            personas=lambda d: d["personas"].apply(lambda x: ", ".join(x))
        ),
        use_container_width=True,
    )

# ── Strategic Recommendations ─────────────────────────────────────────────────
with tab_recs:
    st.subheader("Strategic recommendations from qualitative research")

    priority_filter = st.multiselect(
        "Filter by priority", ["Critical", "High", "Moderate"],
        default=["Critical", "High", "Moderate"]
    )

    for rec in RECOMMENDATIONS:
        if rec["priority"] not in priority_filter:
            continue
        icon = SEVERITY_ICON.get(rec["priority"], "⚪")
        personas_str = " · ".join(
            f"Persona {p} ({PERSONAS[p]['name']})" for p in rec["affected_personas"]
        )
        with st.expander(f"{icon} **#{rec['number']} — {rec['title']}** _{rec['priority']}_"):
            st.markdown(f"**Affects:** {personas_str}")
            st.markdown(rec["detail"])

# ── Sales Staff Insights ───────────────────────────────────────────────────────
with tab_sales:
    st.subheader("BYD Dealership Staff Interviews")
    st.caption(
        "5 semi-structured interviews with BYD sales representatives across Bangkok dealerships "
        "(High Class Ladprao, Rama 3, Rama 9, and others). Source: Sales Interview BYD.pdf"
    )

    sub_overview, sub_themes, sub_lost, sub_raw = st.tabs([
        "Dealership Profiles",
        "Key Themes",
        "Lost Sales Analysis",
        "Raw Transcript",
    ])

    with sub_overview:
        st.markdown("#### Interviewed dealerships")
        for sp in SALES_PROFILES:
            with st.expander(f"**{sp['id']}** — {sp['location']}", expanded=(sp["id"] == "S2")):
                cols = st.columns(2)
                with cols[0]:
                    if sp.get("interviewee") and sp["interviewee"] != "Unknown":
                        st.markdown(f"**Interviewee:** {sp['interviewee']}")
                    if sp.get("experience") and sp["experience"] != "N/A":
                        st.markdown(f"**Experience:** {sp['experience']}")
                    if sp.get("expat_share"):
                        st.markdown(f"**Expat share:** {sp['expat_share']}")
                    if sp.get("corporate_share"):
                        st.markdown(f"**Corporate / Individual:** {sp['corporate_share']} corporate")
                with cols[1]:
                    if sp.get("bev_phev_ratio"):
                        st.markdown(f"**BEV / PHEV ratio:** {sp['bev_phev_ratio']}")
                    if sp.get("top_segments"):
                        st.markdown("**Top customer segments:**")
                        for seg in sp["top_segments"]:
                            st.markdown(f"- {seg}")
                st.info(sp["notes"])

        st.divider()
        st.markdown("#### Cross-dealership snapshot")
        snap_data = {
            "Metric": [
                "BEV preference (out of 10 customers)",
                "Corporate vs. individual split",
                "First car vs. second car (BEV)",
                "Charging convenience weight in decision",
                "PHEV customer understanding",
            ],
            "Consensus finding": [
                "7–8 / 10 prefer BEV outright",
                "~70% individual / ~30% corporate",
                "~50 / 50 (growing toward first-car use)",
                "7–8 / 10 importance score",
                "Low — still confused with standard HEV",
            ],
        }
        st.dataframe(pd.DataFrame(snap_data), use_container_width=True, hide_index=True)

    with sub_themes:
        theme_keys = list(SALES_THEMES.keys())
        theme_labels = [f"{v['icon']} {v['label']}" for v in SALES_THEMES.values()]
        selected_label = st.selectbox("Select theme", theme_labels)
        selected_key = theme_keys[theme_labels.index(selected_label)]
        theme = SALES_THEMES[selected_key]

        st.markdown(f"### {theme['icon']} {theme['label']}")
        st.divider()
        for finding in theme["findings"]:
            st.markdown(
                f'<div style="border-left:4px solid #d70c19;padding:8px 14px;margin:6px 0;'
                f'background:#fdf5f5;border-radius:0 6px 6px 0;color:#1a1a1a">'
                f'{finding}'
                f'</div>',
                unsafe_allow_html=True,
            )

    with sub_lost:
        st.markdown("#### Why customers leave without buying — cross-dealership patterns")
        freq_filter = st.multiselect(
            "Filter by severity",
            ["High", "Moderate"],
            default=["High", "Moderate"],
        )
        for row in LOST_SALES_REASONS:
            if row["severity"] not in freq_filter:
                continue
            icon = "🟠" if row["severity"] == "High" else "🟡"
            st.markdown(
                f'<div style="display:flex;gap:0.75rem;padding:0.5rem 0;border-bottom:1px solid #e2ddd6">'
                f'<span style="font-size:1.1rem">{icon}</span>'
                f'<div><strong style="color:#111">{row["reason"]}</strong>'
                f'<br><span style="color:#6b7280;font-size:0.78rem">Frequency: {row["frequency"]} &nbsp;·&nbsp; Severity: {row["severity"]}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    with sub_raw:
        st.markdown("#### Raw PDF transcript excerpts (English sections)")
        st.caption(
            "Text extracted from Sales Interview BYD.pdf via pypdf. Thai passages are filtered out. "
            "Interview 4 is predominantly Thai and is embedded within Interview 3's section."
        )
        raw_texts = load_sales_pdf_text()
        if not raw_texts:
            st.warning(
                "pypdf is not installed in this environment — install it with `pip install pypdf` to view raw transcripts."
            )
        else:
            interview_choice = st.selectbox(
                "Select interview",
                list(raw_texts.keys()),
                format_func=lambda k: f"Interview {k} — {next((p['location'] for p in SALES_PROFILES if p['id'] == k), 'Unknown')}",
            )
            text = raw_texts.get(interview_choice, "")
            paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 60]
            english_paras = [
                p for p in paragraphs
                if sum(1 for c in p if ord(c) < 128) / max(len(p), 1) > 0.6
            ]
            if english_paras:
                st.text_area(
                    "Transcript (English passages)",
                    "\n\n".join(english_paras[:60]),
                    height=500,
                )
            else:
                st.info("No sufficiently long English passages found for this interview section.")

# ── Voices by Age ──────────────────────────────────────────────────────────────
with tab_age:
    st.subheader("Interview voices — curated by age cohort")
    st.caption(
        "18 respondents with usable answers across cohorts (25–34, 35–44, 45–54). "
        "No 18–24 or 55+ respondents in the interview sample. "
        "Quotes selected to illustrate purchase factor patterns from the quantitative cross-tab (Phase 4c)."
    )

    _QUOTE_STYLE = (
        "border-left:4px solid {color};padding:10px 16px;margin:8px 0;"
        "background:#FAFBFD;border-radius:0 6px 6px 0;"
    )
    _SLIDE_QUOTE_STYLE = (
        "border-left:4px solid {color};padding:10px 16px;margin:8px 0;"
        "background:#F0F7FF;border-radius:0 6px 6px 0;"
        "box-shadow:0 1px 4px rgba(0,0,0,0.08);"
    )

    cohort_keys = list(COHORT_QUOTES.keys())
    cohort_tabs = st.tabs([f"Age {k}" for k in cohort_keys])

    for cohort_tab, cohort_key in zip(cohort_tabs, cohort_keys):
        cohort = COHORT_QUOTES[cohort_key]
        color = cohort["color"]

        with cohort_tab:
            # Header row
            col_left, col_right = st.columns([3, 2])
            with col_left:
                st.markdown(f"**{cohort['respondents']}**")
                st.markdown(
                    f"**Dominant purchase factors:** "
                    + " · ".join(f"`{f}`" for f in cohort["dominant_factors"])
                )
            with col_right:
                st.info(cohort["key_insight"])

            st.divider()

            # Themes
            st.markdown("#### Themes from the interviews")
            for theme in cohort["themes"]:
                with st.expander(f"**{theme['title']}**", expanded=False):
                    for q in theme["quotes"]:
                        meta = f"Respondent #{q['id']} · Age {q['age']} · {'Male' if q['gender'] == 'M' else 'Female'}"
                        st.markdown(
                            f'<div style="{_QUOTE_STYLE.format(color=color)}">'
                            f'<em style="color:#1A1A2E;font-size:0.97em">"{q["text"]}"</em>'
                            f'<br><small style="color:#6B7280;margin-top:4px;display:block">{meta}</small>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            st.divider()

            # Slide-ready quotes
            st.markdown("#### Recommended quotes for the report slide")
            st.caption("Selected for clarity, specificity, and maximum contrast with other cohorts.")
            for q in cohort["slide_quotes"]:
                meta = f"Respondent #{q['id']} · Age {q['age']} · {'Male' if q['gender'] == 'M' else 'Female'}"
                st.markdown(
                    f'<div style="{_SLIDE_QUOTE_STYLE.format(color=color)}">'
                    f'<em style="color:#1A1A2E;font-size:1.0em">"{q["text"]}"</em>'
                    f'<br><small style="color:#6B7280;margin-top:4px;display:block">{meta}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Cross-cohort comparison table
    st.divider()
    st.markdown("#### Cross-cohort comparison")
    comparison = {
        "Theme": [
            "#1 purchase factor",
            "Technology interest",
            "PHEV awareness",
            "BYD awareness",
            "Charging anxiety",
            "Price cut reaction",
            "Key conversion trigger",
        ],
        "25–34 (n=12)": [
            "Running cost + price",
            "High — spec-comparison enjoyment",
            "Low but educatable",
            "Strong — owned or cross-shopped",
            "Public etiquette (not infra)",
            "Frustration (existing owners)",
            "Charging ecosystem + tech features",
        ],
        "35–44 (n=3)": [
            "After-sales service",
            "Moderate — features matter",
            "Near-zero — confused with HEV",
            "Moderate — tech respected, design gap",
            "Home install cost",
            "Caution — wait-and-see",
            "Free wall charger + service proof",
        ],
        "45–54 (n=2)": [
            "Economy + service",
            "Low — proven tech only",
            "Zero",
            "Exists as 'EV brand' only",
            "Infra + station congestion",
            "Strong distrust",
            "Brand longevity proof + stable pricing",
        ],
    }
    st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)
