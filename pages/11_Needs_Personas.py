"""Page 11 — Needs-Based Personas: Family, Cost, and Time."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils.styles import apply_byd_theme, page_header

st.set_page_config(page_title="Needs-Based Personas", layout="wide")
apply_byd_theme()
page_header(
    "Needs-Based Buyer Personas",
    "Five personas from 19 in-depth interviews — Family, Cost, Time, and two non-family PHEV fits",
)

# ── Shared render helpers ──────────────────────────────────────────────────────

def persona_header(color: str, icon: str, name: str, tagline: str, profiles: str) -> None:
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,{color} 0%,{color}cc 100%);
                    padding:1.4rem 1.8rem 1.2rem;border-radius:12px;margin-bottom:1.2rem;
                    box-shadow:0 4px 16px {color}44">
            <div style="font-size:2rem;margin-bottom:0.3rem">{icon}</div>
            <h2 style="margin:0;color:white;font-size:1.5rem;font-weight:800;
                       border:none;padding:0;line-height:1.2">{name}</h2>
            <p style="margin:0.4rem 0 0;color:rgba(255,255,255,0.85);font-size:0.95rem">
                {tagline}
            </p>
            <div style="margin-top:0.7rem;background:rgba(255,255,255,0.15);
                        display:inline-block;padding:3px 10px;border-radius:20px">
                <span style="color:white;font-size:0.72rem;font-weight:600;
                             letter-spacing:0.06em">BASED ON RESPONDENTS {profiles}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def quote_card(text: str, respondent: str) -> None:
    st.markdown(
        f"""
        <div style="border-left:4px solid #d70c19;padding:0.75rem 1rem;
                    background:#f3f4f6;border-radius:0 8px 8px 0;margin:0.5rem 0">
            <p style="margin:0;font-style:italic;color:#111111;font-size:0.92rem">
                &ldquo;{text}&rdquo;
            </p>
            <p style="margin:0.4rem 0 0;font-size:0.75rem;color:#6b7280;font-weight:600">
                — {respondent}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def need_chip(text: str, icon: str = "✓") -> None:
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:0.5rem;'
        f'padding:0.4rem 0;border-bottom:1px solid #e2ddd6">'
        f'<span style="color:#d70c19;font-weight:700;flex-shrink:0">{icon}</span>'
        f'<span style="color:#111111;font-size:0.9rem">{text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def barrier_chip(text: str, severity: str) -> None:
    colors = {"Critical": "#d70c19", "High": "#f59e0b", "Moderate": "#6b7280"}
    color = colors.get(severity, "#6b7280")
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:0.5rem;padding:0.35rem 0">'
        f'<span style="background:{color};color:white;font-size:0.65rem;font-weight:700;'
        f'padding:1px 6px;border-radius:3px;flex-shrink:0;margin-top:2px">{severity.upper()}</span>'
        f'<span style="color:#111111;font-size:0.88rem">{text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def bydbuy_box(text: str) -> None:
    st.markdown(
        f'<div style="background:#fff8f8;border:1px solid #f5c6cb;border-left:4px solid #d70c19;'
        f'border-radius:0 8px 8px 0;padding:0.85rem 1rem;margin-top:0.75rem">'
        f'<p style="margin:0;font-size:0.85rem;font-weight:700;color:#d70c19;'
        f'text-transform:uppercase;letter-spacing:0.06em">BYD Product-Market Fit</p>'
        f'<p style="margin:0.3rem 0 0;color:#111111;font-size:0.9rem">{text}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def stat_row(stats: list[tuple[str, str]]) -> None:
    cols = st.columns(len(stats))
    for col, (label, val) in zip(cols, stats):
        col.markdown(
            f'<div style="text-align:center;padding:0.6rem;background:#f3f4f6;'
            f'border-radius:8px;border:1px solid #e2ddd6">'
            f'<p style="margin:0;font-size:1.15rem;font-weight:800;color:#111111">{val}</p>'
            f'<p style="margin:0;font-size:0.7rem;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em">{label}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Intro
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div style="background:#f3f4f6;border:1px solid #e2ddd6;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:1.5rem">
        <p style="margin:0;color:#111111;font-size:0.9rem">
            These personas are built from 19 qualitative in-depth interviews conducted across two
            research phases. Unlike archetype-based personas (Pragmatist, Considerer, etc.), these are
            <strong>need-first</strong> — each persona is defined by the single strongest driver
            shaping their purchase decision: <strong>family logistics</strong>, <strong>total cost</strong>,
            or <strong>time and convenience</strong>. Most real buyers blend two drivers, but one always
            dominates. Identifying which one determines the right message, product, and channel.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👨‍👩‍👧 Family Logistics Manager",
    "🧮 Cost Calculator",
    "⚡ Time-Efficient Professional",
    "🚗 Field Professional (PHEV)",
    "🏙️ No-Home-Charging Dweller (PHEV)",
    "🔀 How They Overlap",
])

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 1 — FAMILY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    persona_header(
        color="#7c3aed",
        icon="👨‍👩‍👧",
        name="The Family Logistics Manager",
        tagline="Every car decision is a household vote, not a personal one — the car must work for four people, not just the driver.",
        profiles="#14 (int2), #16 (int2), #15 (int2), #6 (int1), #7 (int1)",
    )

    # Stats
    stat_row([
        ("Avg. age", "36–42"),
        ("Gender split", "Mostly female"),
        ("Household size", "4–5 people"),
        ("Kids", "Yes"),
        ("Current car", "7-seat MPV / SUV"),
        ("km/day", "20–40 km"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Daily reality")
        st.markdown(
            """
            <div style="background:#f3f4f6;border-radius:8px;padding:1rem 1.1rem;
                        border:1px solid #e2ddd6;font-size:0.9rem;color:#111111;line-height:1.7">
                Morning starts at <strong>6:30 AM</strong> — school bags packed, kids in the back seat,
                drop-off by 7:30, then work. Afternoon pick-up at 3:30. Weekend means a family trip
                to the mall, a relative's house upcountry, or kids' activities. Every minute waiting at
                a charging station is a minute of a child's schedule disrupted.<br><br>
                The car isn't hers alone. Her partner, kids, and sometimes her parents all have opinions.
                The purchase decision can take <strong>2–3 years</strong> and is only made when
                every family member is comfortable. A car that one person hates doesn't get bought.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What she needs from a car")
        for need in [
            "7 seats — non-negotiable for family of 4+ plus relatives",
            "Boot space that fits a stroller, school bags, and weekly shopping",
            "Long-distance capability with no charging stops mid-journey (sleeping kids)",
            "Simple, predictable ownership — charge at night, drive in the morning",
            "Passive safety visible enough to reassure a protective parent",
            "Easy fold-flat seats and accessible rear row (Xpander middle row cited as painful)",
            "After-sales service she can trust without needing to research deeply",
        ]:
            need_chip(need)

    with col_r:
        st.markdown("#### Voices from the interviews")
        quote_card(
            "I purchased the Kia Carnival for its convenience based on my family lifestyle — having kids.",
            "Respondent #14 · Female, 38 · Kia Carnival owner · Interviews 2"
        )
        quote_card(
            "PHEV is more suitable for families with children. More convenient for long-distance travel — "
            "especially when children are sleeping — as there is no need to stop for charging during the trip. "
            "Fuel can be used during travel, while charging can be done later upon reaching the destination.",
            "Respondent #16 · Female, 34 · Mitsubishi Xpander owner · Interviews 2"
        )
        quote_card(
            "I didn't choose EV because the interior layouts of many EV models in Thailand are impractical "
            "for family usage — insufficient storage space and difficulty fitting a baby stroller.",
            "Respondent #16 · Female, 34 · Interviews 2"
        )
        quote_card(
            "My third car was purchased after starting a family — I needed a larger, more versatile vehicle "
            "with better comfort and practicality for travel.",
            "Respondent #15 · Male, 42 · Toyota Corolla Cross HEV owner · Interviews 2"
        )
        quote_card(
            "Very significant difference between first and subsequent car purchases — as the family grows, "
            "there is a greater need for more passengers and larger storage capacity.",
            "Respondent #14 · Female, 38 · Interviews 2"
        )

    st.divider()
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### What blocks her from buying EV/PHEV today")
        for b, sev in [
            ("No 7-seat BEV/PHEV van from BYD in Thailand — the product simply doesn't exist for her segment", "Critical"),
            ("Long-trip charging stops are incompatible with sleeping/tired children in the back", "Critical"),
            ("Boot space in current Thai EV models too small — can't fit a stroller", "Critical"),
            ("Never heard of PHEV (#14 had never heard the term before the interview)", "High"),
            ("Battery safety anxiety — story of partner's brother whose battery detached in accident (#16)", "High"),
            ("Joint purchase decision — partner/family veto means one concern kills the deal", "High"),
            ("EV tech evolves too fast — 'like buying a smartphone that's already outdated' (#16)", "Moderate"),
        ]:
            barrier_chip(b, sev)

    with col_b2:
        st.markdown("#### What would make her buy BYD")
        for item in [
            "A 7-seat PHEV or large BEV MPV positioned explicitly as 'the family car'",
            "Marketing that shows kids sleeping in the back on a long trip — no charging stop needed",
            "Boot volume number stated clearly: '680 litres — fits 2 strollers and weekly groceries'",
            "BYD crash safety certificate shown visibly: Euro NCAP 5-star, with real Thai accident case",
            "PHEV explained in one sentence at showroom level: 'Electric in the city. Fuel on the highway.'",
            "Service centre within 20 km of home shown on a map during the test drive",
        ]:
            need_chip(item, icon="→")

        bydbuy_box(
            "<strong>Song Plus DM-i PHEV</strong> is the closest match — but it is not marketed as a family car. "
            "Repositioning it around school runs, road trips, and boot space for families with 2 children "
            "would unlock this segment. A 7-seat BEV van (BYD has the technology) would own it entirely."
        )


# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — COST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    persona_header(
        color="#1a7a4a",
        icon="🧮",
        name="The Cost Calculator",
        tagline="Every baht in has to be justified. The spreadsheet is already open before the showroom visit.",
        profiles="#13 (int2), #18 (int2), #15 (int2), #4 (int1), #5 (int1)",
    )

    stat_row([
        ("Avg. age", "28–47"),
        ("Gender split", "Male-dominant"),
        ("Income", "20–70K THB/mo"),
        ("Cars in HH", "1–3"),
        ("Research period", "3–6 months"),
        ("Primary metric", "TCO over 5 yrs"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Daily reality")
        st.markdown(
            """
            <div style="background:#f3f4f6;border-radius:8px;padding:1rem 1.1rem;
                        border:1px solid #e2ddd6;font-size:0.9rem;color:#111111;line-height:1.7">
                Before visiting a showroom, he's already built an Excel model. Columns: purchase price,
                monthly installment, interest rate, estimated fuel cost per km, annual service cost,
                insurance premium, expected resale value at year 5. The car that wins isn't the one
                he likes most — it's the one where the math is cleanest.<br><br>
                He's attracted to EVs <em>because of the fuel savings promise</em> — but deeply
                skeptical because the savings disappear if maintenance is expensive. He heard his
                friend's EV needed 8 months waiting for a part. That's 8 months of installments
                paid for a car he couldn't use.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What he needs from a car")
        for need in [
            "Transparent, predictable total cost of ownership — fuel + maintenance + insurance",
            "Known battery replacement cost ceiling written into the contract",
            "Stable pricing — a price cut 6 months after purchase invalidates his model",
            "Parts available locally, not shipped from China over months",
            "Financing structure (installments, rate, term) as easy to evaluate as purchase price",
            "Honest, verifiable warranty — not marketing language with 47 asterisks",
        ]:
            need_chip(need)

    with col_r:
        st.markdown("#### Voices from the interviews")
        quote_card(
            "I think everyone just wants the cheapest way of transportation. That's the problem "
            "because everything is expensive now, making everyone price-sensitive.",
            "Respondent #13 · Male, 28 · Honda City owner · Interviews 2"
        )
        quote_card(
            "If service costs are expensive, then the car is not truly economical.",
            "Respondent #13 · Male, 28 · Interviews 2"
        )
        quote_card(
            "I use Excel sheets to calculate fuel costs, maintenance costs, and leasing expenses "
            "before making any purchase decision.",
            "Respondent #18 · Male, 30 · BMW PHEV + AION BEV owner · Interviews 2"
        )
        quote_card(
            "BYD is perceived as more affordable — มีเงินไม่เยอะมากแต่อยากใช้รถไฟฟ้า "
            "(not much money but want to use an EV).",
            "Respondent #13 · Male, 28 · Interviews 2"
        )
        quote_card(
            "He is open to EV adoption but prioritizes strong service center coverage, "
            "durable technology, and brands without major incidents such as battery fires.",
            "Respondent #18 · Male, 30 · Interviews 2"
        )
        quote_card(
            "The battery warranty claim — my friend who works in EV service says the real "
            "success rate is around only 0.05%. Brands deny claims citing technical conditions.",
            "Respondent #13 · Male, 28 · Interviews 2"
        )

    st.divider()
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### What blocks him from buying EV today")
        for b, sev in [
            ("Battery replacement cost is completely unknown — the single largest unknown in his TCO model", "Critical"),
            ("BYD's rapid price cuts retroactively break his spreadsheet — 'the math is now wrong'", "Critical"),
            ("Warranty opacity — lifetime battery warranty is perceived as legally unenforceable marketing", "Critical"),
            ("8-month part wait = 8 months of installments for a car he can't drive", "High"),
            ("Service costs may offset fuel savings entirely — the core EV value proposition collapses", "High"),
            ("No transparent, comparable TCO data published by BYD Thailand", "High"),
            ("Insurance costs are higher for EVs (PHEV especially) — not factored into most comparisons", "Moderate"),
        ]:
            barrier_chip(b, sev)

    with col_b2:
        st.markdown("#### What would make him buy BYD")
        for item in [
            "Published 5-year TCO comparison: BYD Dolphin vs. Honda City in a clear table",
            "Battery replacement cost cap stated in writing in the sales contract (e.g., max 150k THB)",
            "12-month price stability commitment: no model price cut within 12 months of purchase",
            "Guaranteed Resale Value program: minimum buyback price at 3 years stated upfront",
            "Plain-language Thai battery warranty with documented real claim examples from Thai owners",
            "Local parts inventory status visible via app — not 'we'll check and call you back'",
        ]:
            need_chip(item, icon="→")

        bydbuy_box(
            "<strong>BYD Dolphin or Atto 3</strong> — positioned as 'the car the spreadsheet chose.' "
            "Price point fits, fuel savings are real, but only if BYD publishes verifiable TCO data and "
            "caps battery replacement cost in writing. Without cost transparency, the strongest EV value "
            "argument in the market stays invisible to the one buyer who would most appreciate it."
        )


# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 3 — TIME / CONVENIENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    persona_header(
        color="#b45309",
        icon="⚡",
        name="The Time-Efficient Professional",
        tagline="The car is a tool that should run invisibly in the background — charge itself overnight, never need an unexpected repair, and just work.",
        profiles="#18 (int2), #19 (int2), #8 (int1), #10 (int1), #1 (int1)",
    )

    stat_row([
        ("Avg. age", "26–32"),
        ("Gender split", "Mixed"),
        ("Income", "35–80K THB/mo"),
        ("Housing", "House (mostly)"),
        ("km/day", "30–80 km"),
        ("Home charger", "Yes / priority"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Daily reality")
        st.markdown(
            """
            <div style="background:#f3f4f6;border-radius:8px;padding:1rem 1.1rem;
                        border:1px solid #e2ddd6;font-size:0.9rem;color:#111111;line-height:1.7">
                Plugs in at 10 PM, full battery at 7 AM. That's the entire charging experience —
                invisible, automatic, part of the routine like charging a phone. The idea of
                waiting 45 minutes at a public charger is physically uncomfortable.<br><br>
                When something goes wrong with the car, a 1-week repair window is borderline
                acceptable. A 1-month wait is a deal-breaker because the car is how life runs.
                She tracks her monthly fuel spend to the baht (₿3,600/month) and knows immediately
                when switching to EV will pay back. She doesn't want to become an EV expert —
                she just wants the car to handle itself.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What she needs from a car")
        for need in [
            "Home charging as the default — plug-in at night = full charge every morning",
            "Single app for everything: charging, service booking, diagnostics, navigation",
            "OTA software updates — no trip to the service centre for a firmware patch",
            "Repair turnaround under 7 days, with a loaner car if over 3 days",
            "Apple CarPlay / Android Auto — phone connectivity non-negotiable",
            "BEV preferred over PHEV: one system = one thing that can go wrong",
            "No range anxiety within daily routine — 300+ km real-world range is enough",
        ]:
            need_chip(need)

    with col_r:
        st.markdown("#### Voices from the interviews")
        quote_card(
            "Charging at home is convenient. However, charging outside the home is still viewed as "
            "inconvenient. The fragmented charging ecosystem is inconvenient because multiple "
            "charging applications must be downloaded.",
            "Respondent #18 · Male, 30 · 70–80 km/day commuter · Interviews 2"
        )
        quote_card(
            "Deal breaker = service waiting times. I can tolerate around 1 week for repairs, "
            "but if it is more than 1 month, I might not consider because I have to use my vehicle daily.",
            "Respondent #13 · Male, 28 · Honda City owner · Interviews 2"
        )
        quote_card(
            "BEV has only one system, making maintenance simpler. PHEVs feel like "
            "a middle-ground solution — you need to charge AND maintain a combustion engine.",
            "Respondent #15 · Male, 42 · Toyota Corolla Cross HEV · Interviews 2"
        )
        quote_card(
            "I believe consumers should already have home charging available before purchasing an EV. "
            "Since I live outside the city center, charging availability has not significantly affected me.",
            "Respondent #19 · Female, 30 · Mazda owner, EV-interested · Interviews 2"
        )
        quote_card(
            "When I wait 8 months for a part from the service center, it's like paying installments "
            "on a car I'm not using — ผ่อนรถฟรีโดยไม่ได้ใช้.",
            "Respondent #13 · Male, 28 · Interviews 2"
        )

    st.divider()
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### What blocks her from going EV today")
        for b, sev in [
            ("Public charging requires multiple apps — friction is real even if rarely needed", "High"),
            ("Service repair wait times exceed tolerance — parts from China take months", "Critical"),
            ("No loaner car policy visible during service — being without a car for a week is unacceptable", "High"),
            ("PHEV dismissed as 'two problems for one car' — dual system adds cognitive maintenance load", "Moderate"),
            ("App/touchscreen lag post-purchase breaks confidence in the whole product (#2 noted this)", "Moderate"),
            ("Range advertised (1,000 km) vs. real-world (700 km) — feels like a trust violation", "High"),
        ]:
            barrier_chip(b, sev)

    with col_b2:
        st.markdown("#### What would make her buy BYD")
        for item in [
            "Single BYD app: charging status, service booking, OTA updates, remote AC pre-cool",
            "72-hour service turnaround SLA in writing, loaner car guaranteed if over 48 hours",
            "Home charger included in purchase price and installed within 7 days of delivery",
            "Real-world range figure (not WLTP) shown prominently at showroom",
            "Apple CarPlay/Android Auto standard on all models — not a premium trim add-on",
            "Parts availability indicator in the app — live stock status, not 'we'll check'",
        ]:
            need_chip(item, icon="→")

        bydbuy_box(
            "<strong>BYD Seal or Atto 3</strong> — urban BEV for high-mileage daily commuters with "
            "home charging. The car itself is fit for purpose, but the ownership <em>experience</em> "
            "is what will win or lose this buyer. App quality, service speed, and one-click "
            "home charger installation are the actual product for this persona — not the car spec sheet."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FIELD PROFESSIONAL (PHEV)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    persona_header(
        color="#0f766e",
        icon="🚗",
        name="The Variable-Distance Field Professional",
        tagline="His daily mileage is unpredictable. PHEV removes the calculation entirely — electric on easy days, petrol on heavy ones, without a second thought.",
        profiles="#18 (int2), #9 (int1), #1 (int1)",
    )

    stat_row([
        ("Age range", "26–32"),
        ("Gender", "Male"),
        ("Income", "30–70K THB/mo"),
        ("km/day", "25–100 km"),
        ("Work travel", "Client visits / field"),
        ("PHEV status", "1 already owns one"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Daily reality")
        st.markdown(
            """
            <div style="background:#f3f4f6;border-radius:8px;padding:1rem 1.1rem;
                        border:1px solid #e2ddd6;font-size:0.9rem;color:#111111;line-height:1.7">
                Monday: office commute, 25 km round trip. Tuesday: client in Samut Sakhon,
                80 km. Wednesday: factory visit in Pathum Thani, 70 km. Thursday: office.
                Friday: two client meetings, 90 km. <br><br>
                A BEV with 400 km real-world range would technically cover all of this.
                But the mental overhead of checking battery on every heavy-travel day adds
                friction he doesn't want. PHEV eliminates the calculation: most days run on
                electricity, heavy days run on petrol, and he never thinks about it.
                The car is a <strong>work tool</strong> — it has to be invisible.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What he needs from a car")
        for need in [
            "Zero daily charging anxiety — the car just works regardless of tomorrow's calendar",
            "EV economics on short commute days (the majority), petrol fallback on heavy days",
            "100+ km electric range to cover most days without touching petrol",
            "Full tank + full battery = 1,000+ km range (BYD DM-i's actual spec — covers any Thai route)",
            "Reliable after-sales: a broken work car is a missed client meeting",
            "Professional exterior — must not look like a city runaround",
            "Fuel cost calculation that works even for variable usage patterns",
        ]:
            need_chip(need)

    with col_r:
        st.markdown("#### Voices from the interviews")
        quote_card(
            "Drives approximately 70–80 km per day. Main destinations include Sasin and factory visits. "
            "The round trip between home and work is approximately 25 km. "
            "Occasionally travels to visit clients in Samut Sakhon and Samut Prakan.",
            "Respondent #18 · Male, 30 · BMW 330e PHEV owner · Interviews 2"
        )
        quote_card(
            "Initially intended to purchase a BEV — specifically considering Chery and MG IM6. "
            "However, after visiting BMW, decided to purchase the BMW PHEV instead. "
            "The previous purchase occurred somewhat unexpectedly because of the promotions.",
            "Respondent #18 · Male, 30 · Interviews 2"
        )
        quote_card(
            "If purchasing another vehicle, he would prefer one with a larger battery capacity "
            "after experiencing EV usage — showing PHEV is his stepping stone, not his destination.",
            "Respondent #18 · Male, 30 · Interviews 2"
        )
        quote_card(
            "He uses Excel sheets to calculate fuel costs, maintenance costs, and leasing expenses. "
            "For work-related usage, purchase price becomes the priority. "
            "For daily commuting, design and fuel economy become more important.",
            "Respondent #18 · Male, 30 · Interviews 2"
        )
        quote_card(
            "Drives 80–100 km per day for work. Chose REEV specifically for range flexibility "
            "across variable-distance work routes — pure BEV created too much daily uncertainty.",
            "Respondent #9 · Male, 26 · Deepal REEV owner · Interviews 1"
        )

    st.divider()
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### What blocks him from choosing PHEV/BEV today")
        for b, sev in [
            ("BYD design not aspirational enough for a professional work context — 'rounded and mass-market'", "High"),
            ("PHEV resale value is lower due to smaller battery and faster degradation (#18 cited this)", "High"),
            ("Higher maintenance cost — maintaining two systems simultaneously (#18's stated concern)", "Moderate"),
            ("After-sales service quality — missing a client meeting due to a car in the shop is unacceptable", "Critical"),
            ("Insurance costs are disproportionately high for PHEVs vs. ICE equivalents", "Moderate"),
        ]:
            barrier_chip(b, sev)

    with col_b2:
        st.markdown("#### What would make him choose BYD PHEV")
        for item in [
            "Song Plus DM-i marketed as a professional tool, not a family crossover",
            "DM-i system explained as '1,200 km total range — never plan your route around a charger again'",
            "Exterior shown in professional lifestyle context: city parking, client meetings, highway driving",
            "Guaranteed buy-back value at 3 years to address PHEV resale anxiety",
            "Service SLA with loaner car — no missed client meetings due to repair wait",
            "Work-expense-deductible positioning (corporate fleet eligible): the car is a business asset",
        ]:
            need_chip(item, icon="→")

        bydbuy_box(
            "<strong>BYD Song Plus DM-i or Seal 06 DM-i</strong> — positioned as the professional's "
            "PHEV, not the family PHEV. The product case is strong: 1,200 km combined range, "
            "electric for city days, petrol on heavy-travel days. "
            "The gap is entirely in messaging and professional context — "
            "BYD currently markets the Song DM-i to families, leaving this segment invisible."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — NO-HOME-CHARGING URBAN DWELLER (PHEV)
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    persona_header(
        color="#6d28d9",
        icon="🏙️",
        name="The No-Home-Charging Urban Dweller",
        tagline="She can't install a wall charger. Nobody has told her that PHEV doesn't require one.",
        profiles="#3 (int1), #17 (int2), #19 (int2)",
    )

    stat_row([
        ("Age range", "26–30"),
        ("Gender", "Mixed (M + F)"),
        ("Housing", "Condo / rental"),
        ("Home charger", "None — no option"),
        ("km/day", "20–30 km"),
        ("EV status", "Excluded themselves"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Daily reality")
        st.markdown(
            """
            <div style="background:#f3f4f6;border-radius:8px;padding:1rem 1.1rem;
                        border:1px solid #e2ddd6;font-size:0.9rem;color:#111111;line-height:1.7">
                She lives in a rented condo. The parking lot has no charger. The management
                committee has never discussed installing one. She asked — they said no.<br><br>
                In her mind, the EV market has two options: BEV (impossible without a charger)
                or ICE (stay with what she has). She has mentally excluded herself from the EV
                transition because she can't charge at home.<br><br>
                What she doesn't know: <strong>PHEV doesn't need daily charging.</strong>
                She could charge at the office twice a week, at a mall charger on Saturday,
                and run on petrol the rest of the time. Her urban commute (20–30 km/day) would
                be covered by electric almost every day. She's the ideal PHEV buyer who
                doesn't know PHEV exists as a solution for her.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What she actually needs")
        for need in [
            "An EV entry point that does NOT require a home charger or dedicated parking slot",
            "Petrol as a reliable daily fallback — she cannot be stranded on a charging-unavailable day",
            "Opportunity charging: plug in at the office, at malls, or at a friend's house when possible",
            "Clear explanation that PHEV ≠ BEV — she can drive normally and charge as a bonus, not a requirement",
            "Short urban commute covered by electric on days she does charge (20–30 km easily within range)",
            "Affordable entry price: she's in the 20K–35K THB/month income range",
        ]:
            need_chip(need)

    with col_r:
        st.markdown("#### Voices from the interviews")
        quote_card(
            "ไม่มีที่chargeที่คอนโดให้ — There is no charger at the condo. "
            "Considers HEV as the only practical option because it doesn't require charging.",
            "Respondent #3 · Male, 26 · Condo, no charger · Interviews 1"
        )
        quote_card(
            "Not considering EV because her father did not recommend EVs — believes they are "
            "difficult to repair and battery replacement is expensive. Currently prefers ICE. "
            "Would consider switching to EV only in the next 5 years.",
            "Respondent #17 · Female, 28 · Condo, no charger · Interviews 2"
        )
        quote_card(
            "She believes consumers should already have home charging available before "
            "purchasing an EV — implying without it, EV is not for her.",
            "Respondent #19 · Female, 30 · Condo, charges at brother's house · Interviews 2"
        )
        quote_card(
            "ไม่มีที่ชาร์จให้ที่คอนโด หรือบ้านก็ต้องติดเอง มันก็เลยไม่สะดวก — "
            "Even at home you'd have to install it yourself. That's inconvenient. "
            "Views HEV as the best option because it requires no external charging.",
            "Respondent #3 · Male, 26 · Interviews 1"
        )

    st.markdown(
        """
        <div style="background:#faf5ff;border:1px solid #d8b4fe;border-left:4px solid #6d28d9;
                    border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin:1rem 0">
            <p style="margin:0;font-size:0.9rem;font-weight:700;color:#6d28d9">
                The awareness gap — this segment's core problem
            </p>
            <p style="margin:0.5rem 0 0;color:#111111;font-size:0.88rem;line-height:1.6">
                None of these respondents have been shown that PHEV solves their specific problem.
                They believe their two options are "BEV (impractical)" or "ICE (stay put)."
                PHEV is the third option they haven't considered — not because they rejected it,
                but because nobody explained it in the context of condo living.
                This is a <strong>pure education gap</strong>, not a product or price gap.
                BYD's PHEV communication needs one condo-specific message:
                <em>"Charge when convenient. Drive on petrol when you can't. No wall charger required."</em>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### What blocks her from choosing PHEV today")
        for b, sev in [
            ("She has never been told PHEV doesn't require daily home charging — pure awareness gap", "Critical"),
            ("Conflates PHEV with BEV: assumes both require a dedicated charger at home", "Critical"),
            ("Father's influence: trusted adults in her life say 'EVs are unreliable' — applies to PHEV by association", "High"),
            ("Chinese brand skepticism: BYD's PHEV hasn't been positioned with enough brand reassurance", "High"),
            ("Showroom communication: BYD's sales staff likely pitch PHEV to home-charger owners, not condo dwellers", "Moderate"),
        ]:
            barrier_chip(b, sev)

    with col_b2:
        st.markdown("#### What would make her choose BYD PHEV")
        for item in [
            "'No home charger needed' stated as the headline — not buried in the brochure",
            "Condo-specific campaign: 'If you live in a condo, this is the EV built for you'",
            "Workplace charging partnership: BYD + corporate parking lots that have chargers already",
            "Petrol range prominently shown: 1,000+ km combined means you never need to plan around charging",
            "Affordable entry price (Seal 06 DM-i or Atto 3 DM-i at entry trim) within her budget",
            "Influencer content: condo-dwelling KOL shows a week of PHEV ownership without a wall charger",
        ]:
            need_chip(item, icon="→")

        bydbuy_box(
            "<strong>BYD Atto 3 DM-i or Seal 06 DM-i</strong> at an accessible price. "
            "This persona is not a difficult conversion — she just needs a different message. "
            "The product already solves her problem perfectly. "
            "A single targeted content piece — 'A week in my PHEV with no home charger' "
            "by a condo-living KOL — could unlock an entire unaddressed segment."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — OVERLAP MATRIX
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### How all five personas interact across respondents")
    st.caption(
        "Most buyers are driven by one primary need but share secondary needs. "
        "Understanding which driver dominates determines channel, message, and product priority."
    )

    st.markdown(
        """
        <table style="width:100%;border-collapse:collapse;font-size:0.88rem;margin:1rem 0">
            <thead>
                <tr style="background:#1a1a1a;color:white">
                    <th style="padding:10px 12px;text-align:left">Respondent</th>
                    <th style="padding:10px 12px">Primary need</th>
                    <th style="padding:10px 12px">Secondary need</th>
                    <th style="padding:10px 12px">Car they'd buy</th>
                    <th style="padding:10px 12px;text-align:left">Unlock message</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background:#fdf7ef;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#14 · F38 · Kia Carnival</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#7c3aed;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Family</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BEV van / PHEV MPV</td>
                    <td style="padding:9px 12px">Show ZEEKR / Song as school-run car with PHEV highway range</td>
                </tr>
                <tr style="background:#ffffff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#16 · F34 · Xpander</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#7c3aed;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Family</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#b45309;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Time</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">PHEV 7-seat</td>
                    <td style="padding:9px 12px">Kids sleeping on highway = no charging stop. Song DM-i in family context</td>
                </tr>
                <tr style="background:#fdf7ef;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#15 · M42 · Corolla Cross</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#b45309;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Time</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BEV (2nd car) + keep HEV</td>
                    <td style="padding:9px 12px">Free wall charger + installation removes his main PHEV objection</td>
                </tr>
                <tr style="background:#ffffff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#13 · M28 · Honda City</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#b45309;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Time</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BYD Dolphin / Atto 3</td>
                    <td style="padding:9px 12px">Published TCO table + 72hr service SLA removes both blockers</td>
                </tr>
                <tr style="background:#fdf7ef;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#18 · M30 · BMW PHEV</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#b45309;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Time</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BEV (already bought AION)</td>
                    <td style="padding:9px 12px">Better design + service network = would have chosen BYD over AION</td>
                </tr>
                <tr style="background:#ffffff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#19 · F30 · Mazda</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#b45309;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Time</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#d70c19;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Design</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">Tesla / BYD Seal</td>
                    <td style="padding:9px 12px">BYD Seal timeless design story + seamless app experience</td>
                </tr>
                <tr style="background:#f0fdfa;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#18 · M30 · BMW PHEV (field work)</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#0f766e;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Field</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BYD Song DM-i</td>
                    <td style="padding:9px 12px">Professional PHEV pitch: 1,200 km range, variable daily distance solved</td>
                </tr>
                <tr style="background:#faf5ff;border-bottom:1px solid #e2ddd6">
                    <td style="padding:9px 12px;font-weight:600">#3 · M26 · Condo, no charger</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#6d28d9;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Condo</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#1a7a4a;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Cost</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">BYD Atto 3 DM-i</td>
                    <td style="padding:9px 12px">"No home charger needed" headline + condo KOL content</td>
                </tr>
                <tr style="background:#faf5ff">
                    <td style="padding:9px 12px;font-weight:600">#17 · F28 · Condo, no charger</td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#6d28d9;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Condo</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">
                        <span style="background:#d70c19;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem">Design</span>
                    </td>
                    <td style="padding:9px 12px;text-align:center">PHEV (doesn't know it yet)</td>
                    <td style="padding:9px 12px">Father's trust + PHEV awareness = pure education unlock</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### Single most important unlock per persona")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            """
            <div style="background:#f3e8ff;border:1px solid #c4b5fd;border-left:4px solid #7c3aed;
                        border-radius:0 8px 8px 0;padding:1rem 1.1rem">
                <p style="margin:0;font-size:0.78rem;font-weight:700;color:#7c3aed;
                           text-transform:uppercase;letter-spacing:0.06em">Family</p>
                <p style="margin:0.4rem 0 0;font-size:1rem;font-weight:700;color:#111111">
                    A 7-seat PHEV or BEV MPV
                </p>
                <p style="margin:0.4rem 0 0;font-size:0.86rem;color:#6b7280">
                    Without this product in Thailand, the Family persona cannot buy BYD.
                    Everything else — messaging, service, design — is irrelevant if the car
                    doesn't have 7 seats and enough boot space for a stroller.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div style="background:#dcfce7;border:1px solid #86efac;border-left:4px solid #1a7a4a;
                        border-radius:0 8px 8px 0;padding:1rem 1.1rem">
                <p style="margin:0;font-size:0.78rem;font-weight:700;color:#1a7a4a;
                           text-transform:uppercase;letter-spacing:0.06em">Cost</p>
                <p style="margin:0.4rem 0 0;font-size:1rem;font-weight:700;color:#111111">
                    Battery replacement cost cap in writing
                </p>
                <p style="margin:0.4rem 0 0;font-size:0.86rem;color:#6b7280">
                    The Cost Calculator's spreadsheet has one unresolvable unknown: battery
                    replacement. Cap it in the sales contract (e.g., 150,000 THB max) and
                    the biggest variable in his model disappears overnight.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div style="background:#fff7ed;border:1px solid #fed7aa;border-left:4px solid #b45309;
                        border-radius:0 8px 8px 0;padding:1rem 1.1rem">
                <p style="margin:0;font-size:0.78rem;font-weight:700;color:#b45309;
                           text-transform:uppercase;letter-spacing:0.06em">Time</p>
                <p style="margin:0.4rem 0 0;font-size:1rem;font-weight:700;color:#111111">
                    72-hour service SLA + home charger on delivery
                </p>
                <p style="margin:0.4rem 0 0;font-size:0.86rem;color:#6b7280">
                    This persona's entire purchase anxiety is about downtime. A written
                    72-hour turnaround commitment and a wall charger installed before
                    delivery day removes the two biggest time-cost risks simultaneously.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """
            <div style="background:#f0fdfa;border:1px solid #99f6e4;border-left:4px solid #0f766e;
                        border-radius:0 8px 8px 0;padding:1rem 1.1rem">
                <p style="margin:0;font-size:0.78rem;font-weight:700;color:#0f766e;
                           text-transform:uppercase;letter-spacing:0.06em">Field</p>
                <p style="margin:0.4rem 0 0;font-size:1rem;font-weight:700;color:#111111">
                    Professional PHEV context — not family
                </p>
                <p style="margin:0.4rem 0 0;font-size:0.86rem;color:#6b7280">
                    Song DM-i must appear in a work travel context — client visits, highway
                    driving, city commuting — not next to a school and a stroller.
                    The message is range flexibility for unpredictable working days.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            """
            <div style="background:#faf5ff;border:1px solid #d8b4fe;border-left:4px solid #6d28d9;
                        border-radius:0 8px 8px 0;padding:1rem 1.1rem">
                <p style="margin:0;font-size:0.78rem;font-weight:700;color:#6d28d9;
                           text-transform:uppercase;letter-spacing:0.06em">Condo</p>
                <p style="margin:0.4rem 0 0;font-size:1rem;font-weight:700;color:#111111">
                    "No home charger needed" as headline
                </p>
                <p style="margin:0.4rem 0 0;font-size:0.86rem;color:#6b7280">
                    One condo-KOL content piece showing a full week of PHEV life without
                    a wall charger. This alone could flip an entire excluded segment
                    who have never heard PHEV framed this way.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
