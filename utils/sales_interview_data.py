"""Structured data from Sales Interview BYD.pdf — BYD dealership staff interviews."""
from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_PDF_PATH = _ROOT / "Sales Interview BYD.pdf"

# ── Dealership staff profiles ─────────────────────────────────────────────────

SALES_PROFILES = [
    {
        "id": "S1",
        "location": "Undisclosed (questions only)",
        "interviewee": "Unknown",
        "experience": "N/A",
        "notes": "Provides structured question framework; answers describe general Thai market patterns",
    },
    {
        "id": "S2",
        "location": "High Class Ladprao, Bangkok",
        "interviewee": "K. Matt",
        "experience": "1 year",
        "expat_share": "~20%",
        "corporate_share": "30%",
        "bev_phev_ratio": "80% BEV / 20% PHEV",
        "top_segments": ["First jobbers", "Families"],
        "notes": "Strong first-jobber focus; 50% buy BEV as first car",
    },
    {
        "id": "S3",
        "location": "Rama 3, Bangkok",
        "interviewee": "Unknown",
        "experience": "N/A",
        "expat_share": "Indian expat cluster (Jewelry Trade Center nearby)",
        "corporate_share": "30%",
        "bev_phev_ratio": "90%+ BEV",
        "top_segments": ["Families", "Ride-hailing (Grab) drivers", "Indian expat business owners"],
        "notes": "Recent influx of lower-budget customers; ride-hailing use case growing",
    },
    {
        "id": "S4",
        "location": "Undisclosed",
        "interviewee": "Unknown",
        "experience": "N/A",
        "corporate_share": "~30%",
        "bev_phev_ratio": "N/A",
        "top_segments": ["Families", "Older hybrid switchers"],
        "notes": "PHEV customers mainly older Japanese-hybrid owners stepping up",
    },
    {
        "id": "S5",
        "location": "Rama 9, Bangkok",
        "interviewee": "Unknown",
        "experience": "N/A",
        "expat_share": "Low",
        "corporate_share": "~30%",
        "bev_phev_ratio": "70–80% BEV / 20–30% PHEV",
        "top_segments": ["Company employees (30+)", "Families"],
        "notes": "Higher-income zone; finance rejection rate low; PHEV understanding improving",
    },
]

# ── Key themes from sales staff perspective ───────────────────────────────────

SALES_THEMES = {
    "customer_segments": {
        "label": "Who Walks Through the Door",
        "icon": "👤",
        "findings": [
            "First jobbers (20s–early 30s) are the most decisive BEV buyers — motivated by fuel savings",
            "Families (collective household decision) are the largest segment by volume",
            "Ride-hailing (Grab) drivers are a fast-growing new segment buying BEVs as a cost tool",
            "Indian expat business owners near Jewelry Trade Center prefer PHEVs / hybrids",
            "Corporate clients (~30% of sales) buy for employee fleets or leasing",
            "Older customers (40s–60s) need more education time but can be converted — oldest BEV sale reported was 70 years old",
        ],
    },
    "powertrain_understanding": {
        "label": "Customer Powertrain Knowledge",
        "icon": "🔋",
        "findings": [
            "BEV knowledge is now well-established — BYD has operated in Thailand 3–4 years",
            "PHEV is still widely confused with HEV; many customers think BYD only sells 'full electric'",
            "Customers who came for 'hybrid' left for Toyota when they saw similar km/l figures — did not understand PHEV runs on electric first",
            "Sales staff must dedicate significant time to PHEV education before closing",
            "Newer sales tool: side-by-side PHEV vs. HEV savings calculator shown at point-of-sale",
            "BEV vs PHEV ratio: consistently 70–80% BEV / 20–30% PHEV across all interviewed dealerships",
        ],
    },
    "price_sensitivity": {
        "label": "Price Sensitivity & Purchase Triggers",
        "icon": "💰",
        "findings": [
            "Price sensitivity is extremely high — the upfront starting price is the #1 purchase decision factor",
            "BYD's history of sudden price cuts (sometimes within 6 months of launch) has conditioned customers to wait",
            "Existing owners whose cars dropped 300K THB in value complain to the dealership directly",
            "Customers delay purchases to wait for Motor Show or year-end government subsidy windows",
            "Sales pitch for BEV: calculate monthly fuel savings vs. petrol to show half (or all) of installment is covered",
            "For PHEV: trigger is reviewing the long-term scheduled maintenance cost table, not the sticker price",
            "Key competitive pressure: Deepal offers 400K THB hidden 'back-end' discounts; MG offers zero-down-payment",
        ],
    },
    "brand_perception": {
        "label": "BYD Brand Perception (Sales-Side View)",
        "icon": "🏷️",
        "findings": [
            "BYD = EV synonymous — when buyers decide to go electric, BYD is typically their first name",
            "BYD's extensive service center network is its #1 competitive advantage, especially upcountry",
            "Mass-market / 'Eua-Athon' perception: customers see BYD as affordable Chinese EV, not premium",
            "Battery technology trust is strong — BYD seen as global battery leader; no need to explain Blade Battery",
            "Customers are skeptical of BYD's ICE engine in PHEVs, preferring BYD purely for electric components",
            "BYD wins against Aion on battery warranty explanation; loses to Deepal/MG on discount packages",
        ],
    },
    "competition": {
        "label": "Competitor Landscape",
        "icon": "⚔️",
        "findings": [
            "Changan: frequently cross-shopped, often wins on promotional accessories packages",
            "Deepal: biggest current threat — offers up to 400,000 THB hidden back-end discounts",
            "MG: wins price-sensitive buyers with zero-down-payment financing",
            "Omoda / Jaecoo: cross-shopped in the sub-800K THB range",
            "Aion: attracts with design but BYD wins back on battery warranty explanation",
            "Japanese brands (Toyota, Honda HRV): still 'scary' competitors, especially for PHEV consideration",
            "BMW / Mercedes-Benz PHEVs: BYD explicitly uses price advantage to convert high-end PHEV shoppers",
            "BYD's stated competitive moat: service center density beats all Chinese rivals",
        ],
    },
    "ideal_customers": {
        "label": "Ideal Customer Profiles (Sales Perspective)",
        "icon": "🎯",
        "findings": [
            "Ideal BEV customer: established working professional, family, 30+ years old, 30K+ THB/month, tech-savvy, planning to replace petrol car entirely",
            "Upcountry BEV buyers are often the most decisive — arrive at Bangkok showroom ready to purchase",
            "Ideal PHEV customer type 1: 40s+ veteran driver currently on Japanese hybrid, wants ICE backup as psychological safety net",
            "Ideal PHEV customer type 2: Indian expat business owner, high purchasing power, cross-shopping with BMW/Mercedes PHEV",
            "Ride-hailing (Grab) BEV buyer: calculates monthly fuel savings to cover installment payment as additional income",
            "Worst-converting customer: young first jobber under 25 who wants BEV but lacks financial approval from bank",
        ],
    },
    "sales_wishlist": {
        "label": "What Sales Staff Want from BYD HQ",
        "icon": "📋",
        "findings": [
            "Extended driving range: customers frequently ask for BEVs capable of 1,000 km per charge — staff say customers would pay more",
            "Advanced software / tech features: competitors win with auto-parking, camping mode — BYD must match or exceed",
            "Minimalist color palette: current lineup is too basic (white/grey/black) or too loud ('pop green') — needs mid-range aesthetic options",
            "Price stability commitment: rapid discounts have eroded customer confidence and dealer relationships with existing buyers",
            "Better financing terms: zero-down or near-zero-down promotions to compete with MG and Deepal",
            "PHEV education campaign: sales teams spend disproportionate time explaining PHEV vs. hybrid basics",
        ],
    },
}

# ── Lost sales reasons (cross-dealership patterns) ────────────────────────────

LOST_SALES_REASONS = [
    {"reason": "Waiting for Motor Show price announcement", "frequency": "Most common", "severity": "High"},
    {"reason": "Deepal's hidden discounts (up to 400K THB)", "frequency": "Very common", "severity": "High"},
    {"reason": "MG's zero-down-payment offers", "frequency": "Common (budget segment)", "severity": "High"},
    {"reason": "After-sales anxiety (parts, wait times)", "frequency": "Occasional", "severity": "Moderate"},
    {"reason": "Family/spouse preference for Japanese brand", "frequency": "Occasional", "severity": "Moderate"},
    {"reason": "Waiting for year-end government subsidies", "frequency": "Seasonal", "severity": "Moderate"},
    {"reason": "Price cut anxiety ('I'll wait for next drop')", "frequency": "Increasingly common", "severity": "High"},
]


def load_sales_pdf_text() -> dict[str, str]:
    """Return {interview_id: clean_text} for each interview in the PDF."""
    try:
        import pypdf  # type: ignore
    except ImportError:
        return {}

    try:
        with open(_PDF_PATH, "rb") as f:
            reader = pypdf.PdfReader(f)
            pages: list[str] = []
            for page in reader.pages:
                raw = page.extract_text() or ""
                # Collapse whitespace between individual characters (pypdf extraction artifact)
                cleaned = re.sub(r"(?<=[A-Za-z0-9,.'\"!?])\s{1,3}(?=[A-Za-z0-9,.'\"!?])", " ", raw)
                cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
                pages.append(cleaned)
    except Exception:
        return {}

    full_text = "\n\n--- PAGE BREAK ---\n\n".join(pages)

    # Split into per-interview sections
    interview_pattern = re.compile(r"INTERVIEW\s+No\.?\s*(\d+)", re.IGNORECASE)
    splits = list(interview_pattern.finditer(full_text))

    result: dict[str, str] = {}
    for i, match in enumerate(splits):
        interview_num = match.group(1)
        start = match.start()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(full_text)
        result[f"S{interview_num}"] = full_text[start:end].strip()

    return result
