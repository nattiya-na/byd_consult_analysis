"""Structured interview data: profiles, personas, themes, and quote extraction."""
from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).parent.parent

# ── Respondent profiles (from interview_insights.md + docx extraction) ─────────

PROFILES = [
    {"id": 1,  "age": 26, "gender": "M", "income": "20–30K", "housing": "House",      "home_charger": True,  "current_car": "BYD Sealion 7 + Mazda 2",         "km_day": "~50",   "powertrain_pref": "BEV",              "byd_attitude": "Neutral-positive", "byd_score": 6,  "persona": "A", "source": "interviews"},
    {"id": 2,  "age": 26, "gender": "M", "income": ">400K",  "housing": "House",      "home_charger": True,  "current_car": "BYD Seal + Sealion (family)",      "km_day": "45–60", "powertrain_pref": "BEV daily / ICE aspirational", "byd_attitude": "Positive",         "byd_score": 8,  "persona": "D", "source": "interviews"},
    {"id": 3,  "age": 26, "gender": "M", "income": "~20K",   "housing": "Condo",      "home_charger": False, "current_car": "Mitsubishi Triton (family)",        "km_day": "<2 weekday / ~100 weekend", "powertrain_pref": "HEV", "byd_attitude": "Negative",         "byd_score": 3,  "persona": "C", "source": "interviews"},
    {"id": 4,  "age": 47, "gender": "M", "income": "~20K",   "housing": "House",      "home_charger": True,  "current_car": "Mitsubishi Lancer",                "km_day": "<20",   "powertrain_pref": "BEV",              "byd_attitude": "Positive",         "byd_score": 7,  "persona": "D", "source": "interviews"},
    {"id": 5,  "age": 26, "gender": "M", "income": "32K",    "housing": "House",      "home_charger": True,  "current_car": "Chery V23 BEV",                    "km_day": "~30",   "powertrain_pref": "BEV (HEV most proven)", "byd_attitude": "Positive",      "byd_score": 7,  "persona": "A", "source": "interviews"},
    {"id": 6,  "age": 50, "gender": "F", "income": "40–50K", "housing": "House",      "home_charger": True,  "current_car": "Toyota Fortuner",                  "km_day": "~20",   "powertrain_pref": "ICE",              "byd_attitude": "Negative",         "byd_score": 2,  "persona": "B", "source": "interviews"},
    {"id": 7,  "age": 35, "gender": "F", "income": "20–40K", "housing": "House",      "home_charger": False, "current_car": "Toyota (unspecified)",              "km_day": "~20",   "powertrain_pref": "HEV",              "byd_attitude": "Negative",         "byd_score": 3,  "persona": "B", "source": "interviews"},
    {"id": 8,  "age": 30, "gender": "M", "income": "35K",    "housing": "House",      "home_charger": True,  "current_car": "Honda HRV (family)",               "km_day": "<10",   "powertrain_pref": "BEV",              "byd_attitude": "Open (if reputation improves)", "byd_score": 5, "persona": "A", "source": "interviews"},
    {"id": 9,  "age": 26, "gender": "M", "income": "30–40K", "housing": "House",      "home_charger": True,  "current_car": "Deepal REEV S05 + Fortuner",       "km_day": "80–100","powertrain_pref": "REEV / BEV next",  "byd_attitude": "Negative on service", "byd_score": 4, "persona": "A", "source": "interviews"},
    {"id": 10, "age": 32, "gender": "M", "income": "~20K",   "housing": "House",      "home_charger": True,  "current_car": "Honda CRV (family has Tesla)",      "km_day": "60–70", "powertrain_pref": "BEV",              "byd_attitude": "Neutral",          "byd_score": 5,  "persona": "A", "source": "interviews"},
    {"id": 11, "age": 28, "gender": "M", "income": "40K+",   "housing": "House+Condo","home_charger": True,  "current_car": "BMW X6 (family: Porsche/Benz/Alphard)", "km_day": "~60", "powertrain_pref": "BEV",           "byd_attitude": "Negative — would buy 2nd-hand only", "byd_score": 3, "persona": "C", "source": "interviews"},
    {"id": 12, "age": 30, "gender": "F", "income": "50–70K", "housing": "House+Condo","home_charger": True,  "current_car": "Tesla Model Y (father's)",          "km_day": "2×/week ~55", "powertrain_pref": "BEV",        "byd_attitude": "Neutral — no beautiful BYD model found", "byd_score": 5, "persona": "C", "source": "interviews"},
    {"id": 13, "age": 28, "gender": "M", "income": "30K",    "housing": "House",      "home_charger": False, "current_car": "Honda City Hatchback",              "km_day": "~20",   "powertrain_pref": "BEV (needs charger first)", "byd_attitude": "Neutral-positive", "byd_score": 6, "persona": "A", "source": "interviews_2"},
    {"id": 14, "age": 38, "gender": "F", "income": "35K",    "housing": "House",      "home_charger": False, "current_car": "Kia Carnival + Isuzu Mu-X",        "km_day": "30–40", "powertrain_pref": "BEV van",          "byd_attitude": "Pragmatic on Chinese brands", "byd_score": 5, "persona": "B", "source": "interviews_2"},
    {"id": 15, "age": 42, "gender": "M", "income": "45–50K", "housing": "House",      "home_charger": False, "current_car": "Toyota Corolla Cross HEV",          "km_day": "~7",    "powertrain_pref": "BEV next / keep HEV", "byd_attitude": "Neutral-negative; prefers Geely EX02 design", "byd_score": 4, "persona": "D", "source": "interviews_2"},
    {"id": 16, "age": 34, "gender": "F", "income": "N/A",    "housing": "House",      "home_charger": True,  "current_car": "Mitsubishi Xpander 7-seat",         "km_day": "~24",   "powertrain_pref": "BEV / PHEV both open", "byd_attitude": "Not specific; EVs don't fit family needs yet", "byd_score": 5, "persona": "B", "source": "interviews_2"},
    {"id": 17, "age": 28, "gender": "F", "income": "N/A",    "housing": "Condo",      "home_charger": False, "current_car": "Mazda CX-30",                      "km_day": "Standard urban", "powertrain_pref": "ICE (considering EV in 5 yrs)", "byd_attitude": "Not considered — bright interiors deal-breaker", "byd_score": 2, "persona": "B", "source": "interviews_2"},
    {"id": 18, "age": 30, "gender": "M", "income": "50–70K", "housing": "House",      "home_charger": True,  "current_car": "BMW 330e PHEV + AION BEV + Benz",  "km_day": "70–80", "powertrain_pref": "PHEV + BEV",       "byd_attitude": "Positive on tech/network; critical on design", "byd_score": 6, "persona": "D", "source": "interviews_2"},
    {"id": 19, "age": 30, "gender": "F", "income": "80K",    "housing": "Condo",      "home_charger": False, "current_car": "Mazda (9 yrs); brother has Deepal", "km_day": "~30",   "powertrain_pref": "EV interested; Tesla preferred", "byd_attitude": "Positive on reputation; design not compelling", "byd_score": 6, "persona": "C", "source": "interviews_2"},
]

# ── Persona definitions ────────────────────────────────────────────────────────

PERSONAS = {
    "A": {
        "name": "The Pragmatic Early Adopter",
        "color": "#2E86AB",
        "profiles": [1, 5, 8, 9, 10, 13],
        "who": "Males, 26–32, income 20–40K THB/month. Already own or actively planning their first EV. Live in houses with home charging installed or ready. Research-heavy: YouTube reviews, spec sheets, spreadsheets. Car is a functional tool — but should look respectable.",
        "needs": [
            "Reliable daily transport for 20–80 km urban commutes",
            "Trustworthy after-sales with no multi-month wait times",
            "400 km+ real-world range for occasional inter-city trips",
            "Low total running cost (electricity vs. fuel already calculated)",
        ],
        "barriers": [
            ("After-sales service quality (scratched cars, deposits not refunded, 3-month part waits)", "Critical"),
            ("Interior aesthetics — black-red 'gamer seat' color scheme actively rejected", "High"),
            ("Warranty opacity — 0.05% battery claim success rate rumor", "High"),
            ("Parts supply chain — China-origin delays create anxiety", "Moderate"),
        ],
        "key_message": "BYD Thailand now has certified service centers with a written 72-hour turnaround commitment. Every technician is BYD-trained. Your battery is guaranteed for 8 years — with real Thai owner claim examples. The Sealion 06 now comes in Lunar Gray interior.",
    },
    "B": {
        "name": "The Cautious Considerer",
        "color": "#A23B72",
        "profiles": [6, 7, 14, 16, 17],
        "who": "Females (primarily), 28–50, income 20–50K THB/month. Safety-first, family-logistics drivers. Toyota and Japanese brand loyalists. Conservative decisions guided by family. Keep cars 7–12 years. Not technically knowledgeable — buy based on brand trust and word-of-mouth.",
        "needs": [
            "A car the whole family can rely on without anxiety",
            "Practical interiors: 7-seat, fold-flat seats, stroller-compatible boot",
            "Simple ownership — charge at home and forget, no complicated routines",
            "Brand stability ('will this brand still exist in 10 years?')",
            "Visible safety proof: crash test results, real accident outcomes",
        ],
        "barriers": [
            ("Chinese brand stability fear — BYD layoff news interpreted as brand failing", "Critical"),
            ("No home charger (condo/apartment) — EV ownership feels impractical", "High"),
            ("No BYD family MPV/van — this segment wants a 7-seat van; BYD has none", "High"),
            ("EV = fast-depreciating technology ('like buying an old smartphone')", "Moderate"),
            ("Battery safety incidents — stories of batteries detaching in accidents", "Moderate"),
        ],
        "key_message": "BYD has operated in Thailand since 2022 — here are 500 Thai families who've driven their BYD every day for 3 years. Your Atto 3 seats 5 comfortably, fits 2 strollers in the boot, and charges overnight at home. Our battery passed Euro NCAP 5-star crash safety.",
    },
    "C": {
        "name": "The Aspirational Aesthete",
        "color": "#F18F01",
        "profiles": [3, 11, 12, 19],
        "who": "Male and female, 26–30, income ranging widely. Driven by design, status, and brand perception. They buy cars as an extension of personal identity. Current reference cars: Tesla, BMW, Mazda, Porsche. BYD's mass-market positioning actively repels them even if product quality is good.",
        "needs": [
            "Clean, sophisticated interior — minimalist like Tesla or premium like Audi",
            "Neutral interior color palette: gray, black, ivory, beige — never loud colors",
            "Owning this car signals taste, not just affordability",
            "Performance that feels composed (no body roll, no floating sensation)",
        ],
        "barriers": [
            ("BYD design not aspirational — 'rounded and Tesla-copying'", "Critical"),
            ("Black-red + bright-color interiors are active deal-breakers (named independently)", "Critical"),
            ("BYD = affordable mass market — repels aspirational buyers", "Critical"),
            ("Rapid depreciation narrative — a car losing 40–50% in year one cannot be 'premium'", "High"),
            ("No 'design story' — no generational sports car heritage", "Moderate"),
        ],
        "key_message": "BYD's design language — Ocean Aesthetics — was shaped by ex-Audi and ex-Mercedes-Benz creative directors. The Seal 07's roofline is a pure coupe. The new interior palette is Ivory + Carbon Black. This is quiet luxury at an intelligent price — for people who know the difference.",
    },
    "D": {
        "name": "The Analytical Optimizer",
        "color": "#6A994E",
        "profiles": [2, 4, 15, 18],
        "who": "Male-dominant, 26–47, income 20K–400K+ THB/month. Data-driven decision makers who calculate fuel, maintenance, insurance, and depreciation before committing. Some use Excel; all make deliberate, documented choices. Research period: 3 weeks to 6+ months.",
        "needs": [
            "Verifiable, stable total cost of ownership",
            "Brand pricing discipline — rapid discounts retroactively invalidate their math",
            "Known battery replacement cost ceiling (the single largest TCO unknown)",
            "Service center density and parts lead time as measurable KPIs",
            "Financing options (installment terms, interest rates) treated equally with base price",
        ],
        "barriers": [
            ("BYD's rapid price cuts break their TCO model — '300K drop in 8 months'", "Critical"),
            ("Battery replacement cost = unquantifiable risk (refuses to commit)", "High"),
            ("Parts lead times from China — unplanned downtime has a cost they can't model", "High"),
            ("App/UX performance lag — touchscreen lag broke purchase confidence post-delivery", "Moderate"),
            ("Long-term resale value — PHEV resale lower due to invisible battery degradation", "Moderate"),
        ],
        "key_message": "Here is BYD's verified 5-year TCO: fuel savings vs. Toyota Camry Hybrid, maintenance cost, insurance benchmark, and depreciation curve. Your battery is warranted 8 years with a maximum replacement cost cap of 150,000 THB — in writing. Pricing locked for 12 months post-launch.",
    },
}

# ── Barrier severity table (Part III of interview_insights.md) ────────────────

BARRIERS_TABLE = [
    {"barrier": "After-sales service (damage, delays, staff training)", "personas": ["A", "B"], "severity": "Critical"},
    {"barrier": "BYD design not aesthetically compelling",              "personas": ["C", "A"], "severity": "Critical"},
    {"barrier": "Chinese brand stability / longevity perception",       "personas": ["B"],       "severity": "Critical"},
    {"barrier": "Rapid price depreciation / brand equity damage",       "personas": ["C", "D"], "severity": "Critical"},
    {"barrier": "No home charger (condo / no parking installation)",    "personas": ["B", "C"], "severity": "High"},
    {"barrier": "Interior color scheme (black-red = deal-breaker)",     "personas": ["A", "C"], "severity": "High"},
    {"barrier": "Battery warranty opacity / low perceived claim success","personas": ["A", "D"], "severity": "High"},
    {"barrier": "Battery replacement cost unknown (TCO risk)",          "personas": ["D"],       "severity": "High"},
    {"barrier": "No BYD family MPV/van in Thailand",                   "personas": ["B"],       "severity": "Moderate"},
    {"barrier": "Suspension / body roll perception",                    "personas": ["C", "A"], "severity": "Moderate"},
    {"barrier": "Parts from China = long repair timeline",              "personas": ["A", "D"], "severity": "Moderate"},
    {"barrier": "PHEV = 'two systems, double problems' misperception",  "personas": ["A", "B", "C", "D"], "severity": "Moderate"},
    {"barrier": "BYD = 'affordable mass market' brand positioning",     "personas": ["C", "D"], "severity": "Moderate"},
    {"barrier": "Technology evolves too fast (EV = smartphone depreciation)", "personas": ["B"], "severity": "Moderate"},
]

# ── Key themes with survey-interview pairs ────────────────────────────────────

THEMES = {
    "after_sales": {
        "label": "After-Sales Service Quality",
        "icon": "🔧",
        "severity": "Critical",
        "survey_signal": "Top EV adoption barrier across all age/income groups in survey",
        "quotes": [
            {"id": 1,  "text": "The ratio is almost 10 to 1 — sales centers to maintenance centers. I had to wait 3 months for a part from China.", "theme_tags": ["after_sales", "parts"]},
            {"id": 9,  "text": "If I have to wait 8 months from the service centers, it's like paying car installments for free without using the car.", "theme_tags": ["after_sales", "parts", "cost"]},
            {"id": 13, "text": "Service centers are the biggest issue — 95% to 99% of my concern. I have to wait one month just to book a service appointment.", "theme_tags": ["after_sales"]},
            {"id": 1,  "text": "They scratched my car during washing because they didn't apply chemical first. Staff not adequately trained.", "theme_tags": ["after_sales", "service_quality"]},
            {"id": 8,  "text": "BYD is secondary to Tesla right now; open if reputation improves — which is entirely about the after-sales story.", "theme_tags": ["after_sales", "brand"]},
        ],
    },
    "charging": {
        "label": "Charging Infrastructure & Range Anxiety",
        "icon": "⚡",
        "severity": "Critical",
        "survey_signal": "Charging convenience score strongest predictor of EV readiness index (35% weight)",
        "quotes": [
            {"id": 1,  "text": "I'm confident 60–80% at best in public charging. People block spots they don't use, and sway charging speed drops from 30 min to 2 hours when multiple chargers run.", "theme_tags": ["charging", "infrastructure"]},
            {"id": 13, "text": "Charging stations are quite problematic. Public charging requires 1–2 hours — gas takes 10 minutes. ICE cars remain more practical for long-distance travel.", "theme_tags": ["charging", "range"]},
            {"id": 15, "text": "EVs won't become mainstream in Thailand — infrastructure too limited outside Bangkok. ICE is still safer for provincial travel.", "theme_tags": ["charging", "infrastructure", "provincial"]},
            {"id": 10, "text": "For range to answer my needs, I need at least 400 km real-world — not the advertised number. The gap between spec and reality creates anxiety.", "theme_tags": ["range", "charging"]},
        ],
    },
    "design": {
        "label": "Interior Design as Deal-Breaker",
        "icon": "🎨",
        "severity": "Critical",
        "survey_signal": "Design and aesthetics cited in top-3 purchase factors by 35%+ of respondents",
        "quotes": [
            {"id": 9,  "text": "The black-red interior is an active veto. I walked out of the showroom because of it. It looks like a gaming chair, not a car.", "theme_tags": ["design", "interior"]},
            {"id": 17, "text": "Bright colors — orange, green seats — are not for me. Immediately eliminated BYD from my list. Interior should be calm and neutral.", "theme_tags": ["design", "interior"]},
            {"id": 3,  "text": "BYD looks rounded — like it's copying Tesla but not quite getting there. I'd rather have an angular, purposeful shape like BMW.", "theme_tags": ["design", "exterior"]},
            {"id": 11, "text": "BYD has no design story. There's no equivalent of the MX-5 or the Supra — no generational car that defines their aesthetic.", "theme_tags": ["design", "brand_heritage"]},
            {"id": 12, "text": "I haven't found a beautiful BYD model yet. The Seal 07 is close — the roofline is interesting. But it's not there yet.", "theme_tags": ["design"]},
        ],
    },
    "depreciation": {
        "label": "Price Depreciation Erodes Trust",
        "icon": "📉",
        "severity": "Critical",
        "survey_signal": "Price/value cited as top purchase factor across all income bands",
        "quotes": [
            {"id": 2,  "text": "I calculated everything and then the car dropped 300,000 THB in 8 months. The math is now wrong. My purchase decision was invalidated retroactively.", "theme_tags": ["depreciation", "price", "trust"]},
            {"id": 11, "text": "BYD loses 40–50% of value in year one. A car that depreciates that fast cannot be called premium — it signals that the market doesn't believe in its quality.", "theme_tags": ["depreciation", "brand"]},
            {"id": 15, "text": "EV is like buying a smartphone that's already old when you get it. Everyone waits for the next model to drop the current price further.", "theme_tags": ["depreciation", "technology"]},
            {"id": 4,  "text": "Everyone's price-sensitive now; everything is expensive. If BYD cuts prices again, the people who paid full price feel cheated.", "theme_tags": ["depreciation", "price", "trust"]},
        ],
    },
    "phev": {
        "label": "PHEV Misunderstood Across All Segments",
        "icon": "🔌",
        "severity": "High",
        "survey_signal": "PHEV consideration rate significantly lower than BEV despite matching real-world needs",
        "quotes": [
            {"id": 13, "text": "PHEVs are viewed as having 'two systems' — potentially higher repair complexity and more failure points. BEV is mechanically simpler.", "theme_tags": ["phev", "technology"]},
            {"id": 15, "text": "PHEV feels like a compromised middle ground without a clear advantage. BEV forces you to plan charging; PHEV tempts you to just use fuel instead.", "theme_tags": ["phev", "behavior"]},
            {"id": 6,  "text": "I had never heard the term PHEV before this interview. I thought BYD only made full electric cars.", "theme_tags": ["phev", "awareness"]},
            {"id": 18, "text": "I own both a PHEV and a BEV — they serve completely different use cases. For city commuting the BEV is better; PHEV for long trips. Most people don't realize this.", "theme_tags": ["phev", "use_case"]},
        ],
    },
    "brand_trust": {
        "label": "Chinese Brand Trust Gap vs. Japanese",
        "icon": "🏷️",
        "severity": "Critical",
        "survey_signal": "BYD consideration rate significantly below Toyota/Honda despite competitive pricing",
        "quotes": [
            {"id": 7,  "text": "Chinese brands = unstable. They come into Thailand, sell a lot, then if it's not profitable they might leave and you're stuck without service.", "theme_tags": ["brand_trust", "stability"]},
            {"id": 14, "text": "Japanese brands I can guarantee will exist in 10–20 years. Chinese brands I genuinely cannot guarantee that. That's a rational fear, not a prejudice.", "theme_tags": ["brand_trust", "japanese_comparison"]},
            {"id": 6,  "text": "I saw news about BYD layoffs. My immediate thought was: the brand is in trouble. I rated their after-sales 0 out of 10 based on that news alone.", "theme_tags": ["brand_trust", "media", "perception"]},
            {"id": 3,  "text": "People remember BYD as 'Chinese car', not as a brand name. That's BYD's image problem — it's absorbed into a generic category perception.", "theme_tags": ["brand_trust", "positioning"]},
            {"id": 10, "text": "BYD has Blade Battery technology — I know about it. But knowing about a technology and trusting a brand long-term are different things.", "theme_tags": ["brand_trust", "technology"]},
        ],
    },
}

# ── Strategic recommendations ─────────────────────────────────────────────────

RECOMMENDATIONS = [
    {
        "number": 1,
        "title": "Make after-sales service a visible brand promise",
        "priority": "Critical",
        "affected_personas": ["A", "B"],
        "detail": "Seven of nineteen respondents raised aftersales as a primary purchase veto. Required actions: publish a written 'Service Quality Charter' with SLAs (72-hour turnaround, staff certification); implement a car-handling guarantee (if your car is damaged at our center, we pay full restoration); proactively show BYD technician training in social content.",
    },
    {
        "number": 2,
        "title": "Introduce a neutral interior option prominently",
        "priority": "Critical",
        "affected_personas": ["A", "C"],
        "detail": "The black-red interior is an active sales barrier documented across multiple unconnected respondents. 'Lunar Gray' or 'Ivory + Carbon' interior trim should be the featured trim in all lifestyle photography and positioned as 'sophisticated' rather than 'basic'.",
    },
    {
        "number": 3,
        "title": "Address price depreciation directly",
        "priority": "Critical",
        "affected_personas": ["C", "D"],
        "detail": "Multiple respondents across income levels cited rapid discounting as a quality signal. Recommended: publish a 'Price Stability' commitment (no discount on current models within 12 months of launch), or offer a Guaranteed Resale Value program (minimum buyback price at 3 years).",
    },
    {
        "number": 4,
        "title": "Demystify the battery warranty",
        "priority": "High",
        "affected_personas": ["A", "D"],
        "detail": "No respondent fully trusted BYD's battery warranty; one cited a 0.05% claim success rate rumor. Required: publish plain-language Thai-language warranty FAQ with real documented claim examples; state explicitly the maximum out-of-pocket battery replacement cost cap; display warranty terms at point-of-sale with interactive Q&A.",
    },
    {
        "number": 5,
        "title": "Communicate design heritage — not just price",
        "priority": "High",
        "affected_personas": ["C", "D"],
        "detail": "BYD is perceived as 'affordable mass market' which repels the design-driven segment. Lead communication with design story (Wolfgang Egger-era ex-designers); show Seal 07 in aspirational lifestyle contexts; use 'intelligent premium' or 'quiet luxury' rather than 'affordable EV'.",
    },
    {
        "number": 6,
        "title": "Create a dedicated PHEV education campaign",
        "priority": "High",
        "affected_personas": ["A", "B", "C", "D"],
        "detail": "PHEV is misunderstood by most respondents — either unknown (Profile #6 never heard the term) or rejected as 'two systems, double problems'. Simplified message: 'Charge at home like a BEV. Refuel like a normal car on long trips. One car. One decision. No compromises.'",
    },
    {
        "number": 7,
        "title": "Consider a 7-seat family MPV for the Thai market",
        "priority": "Moderate",
        "affected_personas": ["B"],
        "detail": "Persona B respondents are actively shopping for a large family van. Chinese brands are on their radar. BYD has no competitive product here in Thailand — this is an unserved demand pocket that aligns with BYD's manufacturing capabilities (Zeekr 009 is on some respondents' radar).",
    },
]

# ── Quote extraction from raw docx files ──────────────────────────────────────

def _read_docx_text(path: Path) -> list[str]:
    """Return non-empty paragraph texts from a docx file (English or Thai)."""
    try:
        from docx import Document
        doc = Document(str(path))
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    except Exception:
        return []


def load_all_raw_quotes() -> dict[int, list[str]]:
    """Return {respondent_id: [paragraph_text, ...]} for all interview files."""
    quotes: dict[int, list[str]] = {}

    # interviews/ folder: Thai language, IDs 1–12
    interviews_dir = _ROOT / "interviews"
    for p in sorted(interviews_dir.glob("*.docx")):
        name = p.stem
        import re
        m = re.search(r"#(\d+)", name)
        if m:
            rid = int(m.group(1))
            quotes[rid] = _read_docx_text(p)

    # interviews_2/ folder: English language, IDs 13–19
    interviews_2_dir = _ROOT / "interviews_2"
    for p in sorted(interviews_2_dir.glob("Interview *.docx")):
        m = re.search(r"Interview (\d+)", p.stem)
        if m:
            rid = 12 + int(m.group(1))  # Interview 1 → ID 13
            quotes[rid] = _read_docx_text(p)

    return quotes


def get_theme_quotes(theme_key: str) -> list[dict]:
    """Return quotes for a given theme key, enriched with profile info."""
    theme = THEMES.get(theme_key, {})
    raw_quotes = theme.get("quotes", [])
    profiles_by_id = {p["id"]: p for p in PROFILES}
    result = []
    for q in raw_quotes:
        prof = profiles_by_id.get(q["id"], {})
        result.append({
            **q,
            "age": prof.get("age"),
            "gender": prof.get("gender"),
            "income": prof.get("income"),
            "persona": prof.get("persona"),
            "powertrain_pref": prof.get("powertrain_pref"),
        })
    return result
