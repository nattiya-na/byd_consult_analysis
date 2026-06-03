"""Page 12 — Thailand Car Registration Market Intelligence.

Data source: DLT (Department of Land Transport) new registration data
- Yearly brand/model: sttt_car_new_reg_yy_25XX_full.csv (2022–2025)
- Monthly brand/model: sttt_car_new_reg_mm_2569_XX.csv (2026)
- Annual fuel type: Fuel_Car_XXXX.xls (2022–2025)
- Monthly fuel type: Fuel_Car_XXX69.xlsx (Jan–May 2026)
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import glob
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.styles import apply_byd_theme, page_header

# ── Constants ──────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent / "register_car_data"
CAR_TYPE = "รถยนต์นั่งส่วนบุคคลไม่เกิน 7 คน"

LAYOUT = dict(
    font=dict(family="Noto Sans Thai, Tahoma, sans-serif", size=12, color="#111111"),
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=20, r=20, t=50, b=40),
    title_font=dict(size=13, color="#d70c19"),
)

BYD_RED  = "#d70c19"
GOLD     = "#f59e0b"

PT_COLORS = {
    "BEV":  "#2E86AB",
    "HEV":  "#52B788",
    "PHEV": "#A23B72",
    "ICE":  "#BC4749",
    "DHEV": "#6A994E",
}

BRAND_COLORS = {
    "BYD":    BYD_RED,
    "TOYOTA": "#CC0000",
    "HONDA":  "#003087",
    "ISUZU":  "#D4A017",
    "AION":   "#00B4D8",
    "DEEPAL": "#7B2D8B",
    "TESLA":  "#E31937",
    "MG":     "#FF6B35",
    "NETA":   "#06D6A0",
    "ORA":    "#F72585",
    "JAECOO": "#4361EE",
    "XPENG":  "#3A86FF",
    "ZEEKR":  "#480CA8",
    "CHERY":  "#F77F00",
    "GWM":    "#6A994E",
    "HAVAL":  "#8B5E3C",
}

PHEV_KEYWORDS = ["DM-I", "DMI", "PLUG-IN", "PHEV"]

MONTH_FILES = {
    "Jan 2026": BASE / "Fuel_Car_Jan69.xlsx",
    "Feb 2026": BASE / "Fuel_Car_Feb69.xlsx",
    "Mar 2026": BASE / "Fuel_Car_Mar69.xlsx",
    "Apr 2026": BASE / "Fuel_Car_Apr69.xlsx",
    "May 2026": BASE / "Fuel_Car_May69.xlsx",
}

ANNUAL_FUEL_FILES = {
    2022: BASE / "Fuel_Car_2565.xls",
    2023: BASE / "Fuel_Car_2566.xls",
    2024: BASE / "Fuel_Car_2567.xls",
    2025: BASE / "Fuel_Car_2568.xls",
}

EV_BRANDS = [
    "BYD", "AION", "DEEPAL", "TESLA", "MG", "NETA", "ORA",
    "JAECOO", "XPENG", "ZEEKR", "CHERY", "GWM", "OMODA", "CHANGAN",
]

# Static competitor map — BYD top models vs Toyota / Honda / Isuzu equivalents
BYD_COMPETITOR_MAP = [
    {
        "byd_model": "DOLPHIN",
        "segment": "B-Segment Hatchback",
        "powertrain": "BEV",
        "price_range": "฿599K–749K",
        "competitors": [
            {"brand": "TOYOTA", "model": "Yaris Ativ",  "vol_kw": ("TOYOTA", "YARIS ATIV"),  "powertrain": "ICE",     "price": "฿489K–599K"},
            {"brand": "TOYOTA", "model": "Yaris Cross", "vol_kw": ("TOYOTA", "YARIS CROSS"), "powertrain": "HEV",     "price": "฿749K–869K"},
            {"brand": "HONDA",  "model": "City",        "vol_kw": ("HONDA",  "CITY"),        "powertrain": "ICE/HEV", "price": "฿569K–799K"},
            {"brand": "MG",     "model": "MG4 Electric","vol_kw": ("MG",     "MG4"),         "powertrain": "BEV",     "price": "฿799K–849K"},
            {"brand": "AION",   "model": "Aion UT",     "vol_kw": ("AION",   "AION UT"),     "powertrain": "BEV",     "price": "฿699K–849K"},
        ],
    },
    {
        "byd_model": "ATTO 3",
        "segment": "C-Segment Compact SUV",
        "powertrain": "BEV",
        "price_range": "฿629K–849K",
        "competitors": [
            {"brand": "TOYOTA", "model": "Yaris Cross",   "vol_kw": ("TOYOTA", "YARIS CROSS"),   "powertrain": "HEV", "price": "฿749K–869K"},
            {"brand": "TOYOTA", "model": "Corolla Cross", "vol_kw": ("TOYOTA", "COROLLA CROSS"), "powertrain": "HEV", "price": "฿869K–1,069K"},
            {"brand": "HONDA",  "model": "HR-V",          "vol_kw": ("HONDA",  "HR-V"),          "powertrain": "HEV", "price": "฿879K–1,009K"},
            {"brand": "MG",     "model": "MG S5 EV",      "vol_kw": ("MG",     "S5 EV"),         "powertrain": "BEV", "price": "฿779K–899K"},
            {"brand": "AION",   "model": "Aion Y Plus",   "vol_kw": ("AION",   "AION Y"),        "powertrain": "BEV", "price": "฿749K–899K"},
            {"brand": "JAECOO", "model": "Jaecoo 5 EV",   "vol_kw": ("JAECOO", "5 EV"),          "powertrain": "BEV", "price": "฿779K–899K"},
            {"brand": "DEEPAL", "model": "Deepal S05",    "vol_kw": ("DEEPAL", "S05"),           "powertrain": "BEV", "price": "฿779K–999K"},
        ],
    },
    {
        "byd_model": "SEALION 6 DM-I",
        "segment": "C-Segment Compact SUV (PHEV)",
        "powertrain": "PHEV",
        "price_range": "฿879K–1,099K",
        "competitors": [
            {"brand": "TOYOTA", "model": "Corolla Cross",  "vol_kw": ("TOYOTA", "COROLLA CROSS"), "powertrain": "HEV",      "price": "฿869K–1,069K"},
            {"brand": "HONDA",  "model": "HR-V",           "vol_kw": ("HONDA",  "HR-V"),          "powertrain": "HEV",      "price": "฿879K–1,009K"},
            {"brand": "HONDA",  "model": "CR-V",           "vol_kw": ("HONDA",  "CR-V"),          "powertrain": "HEV/PHEV", "price": "฿1,399K–1,699K"},
            {"brand": "ISUZU",  "model": "MU-X",           "vol_kw": ("ISUZU",  "MU-X"),          "powertrain": "Diesel",   "price": "฿979K–1,329K"},
            {"brand": "DEEPAL", "model": "Deepal S05 REEV","vol_kw": ("DEEPAL", "S05 REEV"),      "powertrain": "REEV",     "price": "฿979K–1,099K"},
            {"brand": "JAECOO", "model": "Jaecoo 7 SHS",   "vol_kw": ("JAECOO", "7 SHS"),         "powertrain": "PHEV",     "price": "฿899K–1,099K"},
        ],
    },
    {
        "byd_model": "SEALION 7",
        "segment": "D-Segment Midsize SUV",
        "powertrain": "BEV",
        "price_range": "฿1,099K–1,399K",
        "competitors": [
            {"brand": "TOYOTA", "model": "RAV4",       "vol_kw": ("TOYOTA", "RAV4"),    "powertrain": "HEV/PHEV", "price": "฿1,299K–1,799K"},
            {"brand": "TOYOTA", "model": "Harrier",    "vol_kw": ("TOYOTA", "HARRIER"), "powertrain": "HEV",      "price": "฿1,599K–1,799K"},
            {"brand": "HONDA",  "model": "CR-V",       "vol_kw": ("HONDA",  "CR-V"),    "powertrain": "HEV/PHEV", "price": "฿1,399K–1,699K"},
            {"brand": "ISUZU",  "model": "MU-X",       "vol_kw": ("ISUZU",  "MU-X"),   "powertrain": "Diesel",   "price": "฿979K–1,329K"},
            {"brand": "AION",   "model": "Aion V",     "vol_kw": ("AION",   "AION V"),  "powertrain": "BEV",      "price": "฿999K–1,199K"},
            {"brand": "DEEPAL", "model": "Deepal S07", "vol_kw": ("DEEPAL", "S07"),     "powertrain": "BEV",      "price": "฿999K–1,299K"},
            {"brand": "JAECOO", "model": "Jaecoo 6 EV","vol_kw": ("JAECOO", "6 EV"),   "powertrain": "BEV",      "price": "฿899K–1,099K"},
        ],
    },
    {
        "byd_model": "SEAL",
        "segment": "D-Segment Midsize Sedan",
        "powertrain": "BEV",
        "price_range": "฿1,099K–1,599K",
        "competitors": [
            {"brand": "TOYOTA", "model": "Camry",  "vol_kw": ("TOYOTA", "CAMRY"),  "powertrain": "HEV", "price": "฿1,699K–2,249K"},
            {"brand": "HONDA",  "model": "Accord", "vol_kw": ("HONDA",  "ACCORD"), "powertrain": "HEV", "price": "฿1,799K–2,049K"},
        ],
    },
]

# ── Data loading ───────────────────────────────────────────────────────────────

@st.cache_data
def load_brand_data() -> pd.DataFrame:
    dfs = []
    for f in sorted(glob.glob(str(BASE / "sttt_car_new_reg_yy_*.csv"))):
        df = pd.read_csv(f, encoding="utf-8-sig")
        df = df[df["ประเภทรถ"] == CAR_TYPE]
        dfs.append(df)
    for f in sorted(glob.glob(str(BASE / "sttt_car_new_reg_mm_*.csv"))):
        df = pd.read_csv(f, encoding="utf-8-sig")
        df = df[df["ประเภทรถ"] == CAR_TYPE]
        df = df.groupby(["ปี พ.ศ.", "ประเภทรถ", "ยี่ห้อ", "รุ่น"], as_index=False)["จำนวน"].sum()
        dfs.append(df)
    df_all = pd.concat(dfs, ignore_index=True)
    df_all["year"] = df_all["ปี พ.ศ."] - 543
    df_all["brand"] = df_all["ยี่ห้อ"].str.strip().str.upper()
    df_all["model"] = df_all["รุ่น"].str.strip().str.upper()
    df_all["is_phev"] = df_all["model"].apply(
        lambda m: any(k in str(m) for k in PHEV_KEYWORDS)
    )
    return df_all


def _parse_fuel_sheet(fpath: Path) -> dict | None:
    """Parse a DLT fuel-type Excel sheet and return fuel counts for รย.1."""
    FUEL_MAP = {
        "ไฟฟ้า": "BEV",
        "เบนซิน-ไฟฟ้า": "HEV",
        "ดีเซล-ไฟฟ้า": "DHEV",
        "เบนซิน-ไฟฟ้าแบบเสียบปลั๊ก": "PHEV",
        "เบนซิน": "Petrol",
        "ดีเซล": "Diesel",
    }
    raw = pd.ExcelFile(fpath).parse("ทั่วประเทศ", header=None)
    header_row = next(
        (i for i, r in raw.iterrows() if "ไฟฟ้า" in " ".join(str(v) for v in r.values)),
        None,
    )
    car_row = next(
        (i for i, r in raw.iterrows()
         if "รย.1" in str(r.values) or "รถยนต์นั่งส่วนบุคคลไม่เกิน 7 คน" in str(r.values)),
        None,
    )
    if header_row is None or car_row is None:
        return None
    headers = raw.iloc[header_row].tolist()
    values  = raw.iloc[car_row].tolist()
    row: dict = {}
    for h, v in zip(headers, values):
        h = str(h).strip()
        if h in FUEL_MAP:
            try:
                row[FUEL_MAP[h]] = int(v)
            except Exception:
                row[FUEL_MAP[h]] = 0
    return row


@st.cache_data
def load_fuel_monthly() -> pd.DataFrame:
    rows = []
    for label, fpath in MONTH_FILES.items():
        if not fpath.exists():
            continue
        parsed = _parse_fuel_sheet(fpath)
        if parsed:
            rows.append({"month": label, **parsed})
    return pd.DataFrame(rows)


@st.cache_data
def load_fuel_annual() -> pd.DataFrame:
    rows = []
    for year, fpath in ANNUAL_FUEL_FILES.items():
        if not fpath.exists():
            continue
        parsed = _parse_fuel_sheet(fpath)
        if parsed:
            rows.append({"year": year, **parsed})
    df = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
    for col in ["Petrol", "Diesel", "BEV", "HEV", "PHEV", "DHEV"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)
    df["ICE"] = df["Petrol"] + df["Diesel"]
    return df


# ── Page ───────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Market Intelligence", layout="wide")
apply_byd_theme()
page_header(
    "Thailand Car Registration Intelligence",
    "DLT new-registration data 2022–2026 · Powertrain trends · Brand rankings · BYD vs competition",
)

df             = load_brand_data()
fuel_df        = load_fuel_monthly()
annual_fuel_df = load_fuel_annual()

# ── KPI strip ──────────────────────────────────────────────────────────────────
yr_totals  = df.groupby("year")["จำนวน"].sum()
byd_totals = df[df["brand"] == "BYD"].groupby("year")["จำนวน"].sum()

rank_2025 = (
    df[df["year"] == 2025]
    .groupby("brand")["จำนวน"].sum()
    .rank(ascending=False)
    .get("BYD", None)
)
growth = (byd_totals.get(2025, 0) - byd_totals.get(2024, 0)) / max(byd_totals.get(2024, 1), 1) * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total new reg. 2025",    f"{int(yr_totals.get(2025, 0)):,}",  "passenger cars")
k2.metric("BYD 2025 registrations", f"{int(byd_totals.get(2025, 0)):,}", f"+{growth:.0f}% vs 2024")
k3.metric("BYD market rank 2025",   f"#{int(rank_2025)}",                "by passenger car volume")
k4.metric("BYD 2022 registrations", f"{int(byd_totals.get(2022, 0)):,}", "market entry")
k5.metric("BYD growth 2022→2025",   f"{int(byd_totals.get(2025, 0) / max(byd_totals.get(2022, 1), 1)):,}×", "111x in 3 years")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ Powertrain Trends",
    "🏁 Brand Race 2022–2026",
    "🔴 BYD Deep Dive",
    "🆚 BYD vs Competitors",
    "🗂️ Model Competitor Map",
    "📊 Trend & Threat Analysis",
])

ALL_YEARS = [2022, 2023, 2024, 2025, 2026]

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — POWERTRAIN TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── Annual 2022–2025 ───────────────────────────────────────────────────────
    st.markdown("#### Annual new registrations by powertrain — passenger cars ≤7 seats (2022–2025)")
    st.caption("Source: DLT Annual Fuel-type Registration · รย.1 vehicle class · full-year totals")

    if annual_fuel_df.empty:
        st.warning("Annual fuel data files not found.")
    else:
        ann_years   = annual_fuel_df["year"].tolist()
        pt_ann_cols = ["ICE", "DHEV", "HEV", "PHEV", "BEV"]

        # Stacked bar — annual volumes
        fig_ann = go.Figure()
        for pt in pt_ann_cols:
            if pt not in annual_fuel_df.columns:
                continue
            fig_ann.add_trace(go.Bar(
                name=pt, x=annual_fuel_df["year"], y=annual_fuel_df[pt],
                marker_color=PT_COLORS.get(pt, "#888"),
                text=[f"{int(v):,}" if v > 5000 else "" for v in annual_fuel_df[pt]],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_ann.update_layout(
            **LAYOUT, barmode="stack",
            title="Annual new registrations by powertrain (passenger cars, 2022–2025)",
            yaxis_title="New registrations", height=440,
            xaxis=dict(tickmode="array", tickvals=ann_years),
        )
        st.plotly_chart(fig_ann, use_container_width=True)

        # % share — annual
        ann_available = [p for p in pt_ann_cols if p in annual_fuel_df.columns]
        total_by_year = annual_fuel_df[ann_available].sum(axis=1)
        fig_ann_pct = go.Figure()
        for pt in pt_ann_cols:
            if pt not in annual_fuel_df.columns:
                continue
            pct = annual_fuel_df[pt] / total_by_year * 100
            fig_ann_pct.add_trace(go.Bar(
                name=pt, x=annual_fuel_df["year"], y=pct,
                marker_color=PT_COLORS.get(pt, "#888"),
                text=[f"{v:.1f}%" if v > 2 else "" for v in pct],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_ann_pct.update_layout(
            **LAYOUT, barmode="stack",
            title="Powertrain share % of annual passenger car registrations (2022–2025)",
            yaxis_title="% share", height=400,
            xaxis=dict(tickmode="array", tickvals=ann_years),
        )
        st.plotly_chart(fig_ann_pct, use_container_width=True)

        # EV adoption trend line
        st.markdown("#### EV adoption trend — BEV · HEV · PHEV share over 2022–2025")
        fig_ev_trend = go.Figure()
        for pt in ["BEV", "HEV", "PHEV"]:
            if pt not in annual_fuel_df.columns:
                continue
            pct = annual_fuel_df[pt] / total_by_year * 100
            fig_ev_trend.add_trace(go.Scatter(
                x=annual_fuel_df["year"], y=pct,
                name=pt, mode="lines+markers+text",
                line=dict(color=PT_COLORS.get(pt, "#888"), width=3),
                marker=dict(size=9),
                text=[f"{v:.1f}%" for v in pct],
                textposition="top center",
            ))
        fig_ev_trend.update_layout(
            **LAYOUT,
            title="BEV / HEV / PHEV share trend (% of annual passenger car registrations)",
            yaxis_title="% share", height=400,
            xaxis=dict(tickmode="array", tickvals=ann_years),
        )
        st.plotly_chart(fig_ev_trend, use_container_width=True)

        # Annual metrics table
        st.markdown("**Annual breakdown (units)**")
        disp_ann = ["year"] + [c for c in ["BEV", "HEV", "PHEV", "DHEV", "ICE"] if c in annual_fuel_df.columns]
        st.dataframe(
            annual_fuel_df[disp_ann].set_index("year").style.format("{:,.0f}"),
            use_container_width=True,
        )

        # Insights
        def _ann(col, yr):
            sub = annual_fuel_df[annual_fuel_df["year"] == yr]
            return int(sub[col].values[0]) if len(sub) and col in sub.columns else 0

        bev_22, bev_25 = _ann("BEV", 2022), _ann("BEV", 2025)
        hev_25  = _ann("HEV", 2025)
        ice_22  = _ann("ICE", 2022)
        ice_25  = _ann("ICE", 2025)

        ia, ib, ic = st.columns(3)
        ia.success(
            f"**BEV exploded: {bev_22:,} (2022) → {bev_25:,} (2025).**\n\n"
            f"{bev_25 / max(bev_22, 1):.0f}× growth in 3 years driven by BYD's aggressive "
            "market entry and Thailand's EV3/EV3.5 incentive schemes."
        )
        ib.info(
            f"**HEV remains strong at {hev_25:,} units in 2025.**\n\n"
            "Toyota and Honda hybrids hold firm as the bridge technology for "
            "consumers not yet ready for full BEV. HEV share actually grew YoY."
        )
        ic.warning(
            f"**ICE contracting sharply: {ice_22:,} (2022) → {ice_25:,} (2025).**\n\n"
            "Petrol + Diesel passenger cars nearly halved in 3 years — "
            "a structural market shift, not a cyclical dip."
        )

    st.divider()

    # ── Monthly 2026 ───────────────────────────────────────────────────────────
    st.markdown("#### Monthly new registrations by powertrain — passenger cars ≤7 seats (2026)")
    st.caption("Source: DLT Fuel-type registration data · รย.1 vehicle class · Jan–May 2026")

    if fuel_df.empty:
        st.warning("Fuel data files not found.")
    else:
        pt_cols = ["ICE", "DHEV", "HEV", "PHEV", "BEV"]
        fuel_df["ICE"] = fuel_df.get("Petrol", pd.Series(dtype=float)).fillna(0) + \
                         fuel_df.get("Diesel", pd.Series(dtype=float)).fillna(0)
        months_order = list(MONTH_FILES.keys())
        fuel_plot = fuel_df.set_index("month").reindex(months_order).reset_index()

        fig_pt = go.Figure()
        for pt in pt_cols:
            if pt not in fuel_plot.columns:
                continue
            fig_pt.add_trace(go.Bar(
                name=pt, x=fuel_plot["month"], y=fuel_plot[pt],
                marker_color=PT_COLORS.get(pt, "#888"),
                text=[f"{int(v):,}" if v > 500 else "" for v in fuel_plot[pt]],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_pt.update_layout(**LAYOUT, barmode="stack",
                             title="Monthly new registrations by powertrain (passenger cars, 2026)",
                             yaxis_title="New registrations", height=420)
        st.plotly_chart(fig_pt, use_container_width=True)

        total_by_month = fuel_plot[[p for p in pt_cols if p in fuel_plot.columns]].sum(axis=1)
        fig_pct = go.Figure()
        for pt in pt_cols:
            if pt not in fuel_plot.columns:
                continue
            pct = fuel_plot[pt] / total_by_month * 100
            fig_pct.add_trace(go.Bar(
                name=pt, x=fuel_plot["month"], y=pct,
                marker_color=PT_COLORS.get(pt, "#888"),
                text=[f"{v:.0f}%" if v > 3 else "" for v in pct],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(color="white", size=10),
            ))
        fig_pct.update_layout(**LAYOUT, barmode="stack",
                              title="Powertrain share % of total monthly registrations",
                              yaxis_title="% share", height=380)
        st.plotly_chart(fig_pct, use_container_width=True)

        st.markdown("**Monthly breakdown (units)**")
        available = [c for c in ["month", "BEV", "HEV", "PHEV", "ICE"] if c in fuel_plot.columns]
        st.dataframe(
            fuel_plot[available].set_index("month").style.format("{:,.0f}"),
            use_container_width=True,
        )

        def _mget(col, month):
            sub = fuel_df[fuel_df["month"] == month]
            return int(sub[col].values[0]) if len(sub) and col in sub.columns else 0

        jan_bev  = _mget("BEV",  "Jan 2026")
        may_bev  = _mget("BEV",  "May 2026")
        may_phev = _mget("PHEV", "May 2026")
        feb_phev = _mget("PHEV", "Feb 2026")

        c1, c2, c3 = st.columns(3)
        c1.info(
            f"**January spike: {jan_bev:,} BEVs registered.**\n\n"
            "January is ~4–8× other months, driven by Motor Show bulk registrations "
            "and BYD promotions. Exclude January for organic trend reading."
        )
        c2.info(
            f"**BEV stabilising at ~10,000–18,000/month** (Mar–May). "
            "BEV now accounts for 30–40% of passenger car registrations — "
            "a structural shift."
        )
        c3.info(
            f"**PHEV growing: {feb_phev:,} → {may_phev:,} (Feb→May 2026).**\n\n"
            "Doubled in 3 months driven by BYD DM-i launches. "
            "Fastest-growing powertrain by growth rate."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BRAND RACE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### New passenger car registrations by brand — all brands, 2022–2026")
    st.caption("2026 = Jan–Feb partial year (CSV data). All passenger cars ≤7 seats.")

    by_brand_year = df.groupby(["year", "brand"])["จำนวน"].sum().reset_index()

    top15_brands = (
        by_brand_year[by_brand_year["year"] == 2025]
        .nlargest(15, "จำนวน")["brand"].tolist()
    )

    pivot_top = (
        by_brand_year[by_brand_year["brand"].isin(top15_brands)]
        .pivot_table(index="brand", columns="year", values="จำนวน", aggfunc="sum", fill_value=0)
    )
    pivot_top = pivot_top.reindex(pivot_top[2025].sort_values(ascending=False).index)

    fig_top = go.Figure()
    year_colors = {2022: "#cbd5e1", 2023: "#94a3b8", 2024: "#475569", 2025: BYD_RED, 2026: GOLD}
    for yr in [2022, 2023, 2024, 2025, 2026]:
        if yr not in pivot_top.columns:
            continue
        fig_top.add_trace(go.Bar(
            name=str(yr), x=pivot_top.index.tolist(), y=pivot_top[yr].values,
            marker_color=year_colors.get(yr, "#888"),
        ))
    fig_top.update_layout(
        **LAYOUT, barmode="group",
        title="Top 15 brands — new passenger car registrations (2022–2026)",
        yaxis_title="New registrations", height=480,
        xaxis_tickangle=-30,
        legend=dict(orientation="h", y=1.08),
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("#### EV & Chinese brand competition")

    ev_brands_in_data = [b for b in EV_BRANDS if b in by_brand_year["brand"].values]
    pivot_ev = (
        by_brand_year[by_brand_year["brand"].isin(ev_brands_in_data)]
        .pivot_table(index="brand", columns="year", values="จำนวน", aggfunc="sum", fill_value=0)
    )
    pivot_ev = pivot_ev.reindex(pivot_ev[2025].sort_values(ascending=False).index)

    fig_ev = go.Figure()
    for yr in [2022, 2023, 2024, 2025, 2026]:
        if yr not in pivot_ev.columns:
            continue
        fig_ev.add_trace(go.Bar(
            name=str(yr), x=pivot_ev.index.tolist(), y=pivot_ev[yr].values,
            marker_color=year_colors.get(yr, "#888"),
        ))
    fig_ev.update_layout(
        **LAYOUT, barmode="group",
        title="EV & Chinese brand registrations (2022–2026)",
        yaxis_title="New registrations", height=440,
        xaxis_tickangle=-15,
        legend=dict(orientation="h", y=1.08),
    )
    st.plotly_chart(fig_ev, use_container_width=True)

    fig_line = go.Figure()
    for brand in ev_brands_in_data:
        sub = by_brand_year[by_brand_year["brand"] == brand].sort_values("year")
        fig_line.add_trace(go.Scatter(
            x=sub["year"], y=sub["จำนวน"],
            name=brand, mode="lines+markers",
            line=dict(color=BRAND_COLORS.get(brand, "#888"), width=3 if brand == "BYD" else 1.5),
            marker=dict(size=8 if brand == "BYD" else 5),
        ))
    fig_line.update_layout(
        **LAYOUT,
        title="EV brand registration trend (line chart)",
        yaxis_title="Annual new registrations", height=440,
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()
    ca, cb, cc = st.columns(3)
    ca.success(
        "**BYD: #3 overall in 2025**, behind only Toyota and Honda. "
        "Grew from 371 units (2022) to 41,180 (2025) — 111× in 3 years."
    )
    cb.warning(
        "**NETA collapse:** 12,777 (2023) → 7,969 (2024) → 3,256 (2025) → 64 in 2026. "
        "Cautionary tale for brand-trust fragility."
    )
    cc.info(
        "**Rising challengers in 2025:** JAECOO (0→8,985), AION (4,127→11,969), DEEPAL (5,603→8,401). "
        "BYD faces intensifying Chinese competition."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BYD DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    byd_df = df[df["brand"] == "BYD"].copy()

    byd_annual = byd_df.groupby("year")["จำนวน"].sum().reset_index()

    fig_byd_total = go.Figure(go.Bar(
        x=byd_annual["year"], y=byd_annual["จำนวน"],
        marker_color=[BYD_RED if y == 2025 else "#f5a0a8" for y in byd_annual["year"]],
        text=[f"{int(v):,}" for v in byd_annual["จำนวน"]],
        textposition="outside",
    ))
    fig_byd_total.update_layout(
        **LAYOUT,
        title="BYD annual new registrations in Thailand (passenger cars)",
        yaxis_title="Units", height=380,
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_byd_total, use_container_width=True)

    st.markdown("#### BYD model breakdown by year")

    byd_df["powertrain"] = byd_df["is_phev"].map({True: "PHEV (DM-i)", False: "BEV"})

    byd_pt = byd_df.groupby(["year", "powertrain"])["จำนวน"].sum().reset_index()
    fig_byd_pt = go.Figure()
    for pt, color in [("BEV", PT_COLORS["BEV"]), ("PHEV (DM-i)", PT_COLORS["PHEV"])]:
        sub = byd_pt[byd_pt["powertrain"] == pt]
        fig_byd_pt.add_trace(go.Bar(
            name=pt, x=sub["year"], y=sub["จำนวน"],
            marker_color=color,
            text=[f"{int(v):,}" for v in sub["จำนวน"]],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=11),
        ))
    fig_byd_pt.update_layout(
        **LAYOUT, barmode="stack",
        title="BYD registrations: BEV vs PHEV (DM-i) by year",
        yaxis_title="Units", height=380,
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_byd_pt, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**2025 model breakdown**")
        byd_2025 = (
            byd_df[byd_df["year"] == 2025]
            .groupby(["model", "powertrain"])["จำนวน"].sum()
            .reset_index().sort_values("จำนวน", ascending=True)
        )
        fig_m25 = go.Figure(go.Bar(
            x=byd_2025["จำนวน"], y=byd_2025["model"],
            orientation="h",
            marker_color=[PT_COLORS["PHEV"] if p == "PHEV (DM-i)" else PT_COLORS["BEV"]
                          for p in byd_2025["powertrain"]],
            text=[f"{int(v):,}" for v in byd_2025["จำนวน"]],
            textposition="outside",
        ))
        fig_m25.update_layout(**LAYOUT, title="2025 by model", height=max(360, 30 * len(byd_2025)))
        st.plotly_chart(fig_m25, use_container_width=True)

    with col_r:
        st.markdown("**2026 (Jan–Feb) model breakdown**")
        byd_2026 = (
            byd_df[byd_df["year"] == 2026]
            .groupby(["model", "powertrain"])["จำนวน"].sum()
            .reset_index().sort_values("จำนวน", ascending=True)
        )
        fig_m26 = go.Figure(go.Bar(
            x=byd_2026["จำนวน"], y=byd_2026["model"],
            orientation="h",
            marker_color=[PT_COLORS["PHEV"] if p == "PHEV (DM-i)" else PT_COLORS["BEV"]
                          for p in byd_2026["powertrain"]],
            text=[f"{int(v):,}" for v in byd_2026["จำนวน"]],
            textposition="outside",
        ))
        fig_m26.update_layout(**LAYOUT, title="2026 Jan–Feb by model", height=max(360, 30 * len(byd_2026)))
        st.plotly_chart(fig_m26, use_container_width=True)

    phev_2025 = int(byd_df[(byd_df["year"] == 2025) & byd_df["is_phev"]]["จำนวน"].sum())
    bev_2025  = int(byd_df[(byd_df["year"] == 2025) & ~byd_df["is_phev"]]["จำนวน"].sum())
    phev_share = phev_2025 / max(phev_2025 + bev_2025, 1) * 100

    st.divider()
    ia, ib, ic = st.columns(3)
    ia.info(
        f"**PHEV launched in 2025:** {phev_2025:,} DM-i units ({phev_share:.0f}% of BYD total). "
        "SEALION 6 DM-i Premium (6,309 units) is the #1 BYD PHEV model in its first year."
    )
    ib.info(
        "**Dolphin dominates BEV:** ~12,300 units in 2025, the most registered single BEV model in Thailand."
    )
    ic.info(
        "**Portfolio shift:** In 2023 the ATTO 3 was 63% of all BYD registrations. "
        "By 2025 BYD has 6+ active models across BEV and PHEV."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BYD vs COMPETITORS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### BYD vs top EV/Chinese brand competitors — registration trend")

    by_brand_year = df.groupby(["year", "brand"])["จำนวน"].sum().reset_index()

    top_ev_2025 = (
        by_brand_year[
            (by_brand_year["year"] == 2025) &
            (by_brand_year["brand"].isin(EV_BRANDS))
        ].nlargest(8, "จำนวน")["brand"].tolist()
    )
    if "BYD" not in top_ev_2025:
        top_ev_2025 = ["BYD"] + top_ev_2025[:7]

    fig_comp = go.Figure()
    for brand in top_ev_2025:
        sub = by_brand_year[by_brand_year["brand"] == brand].sort_values("year")
        is_byd = brand == "BYD"
        fig_comp.add_trace(go.Scatter(
            x=sub["year"], y=sub["จำนวน"],
            name=brand, mode="lines+markers+text",
            line=dict(color=BRAND_COLORS.get(brand, "#888"), width=4 if is_byd else 2,
                      dash="solid" if is_byd else "dot"),
            marker=dict(size=9 if is_byd else 6),
            text=[f"{int(v):,}" if row == sub.iloc[-1].name else ""
                  for row, v in zip(sub.index, sub["จำนวน"])],
            textposition="top center",
        ))
    fig_comp.update_layout(
        **LAYOUT,
        title="BYD vs top EV/Chinese competitors — annual new registrations",
        yaxis_title="Annual registrations", height=500,
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("#### Market share within EV/Chinese brand segment (top 8)")

    ev_total = by_brand_year[by_brand_year["brand"].isin(top_ev_2025)].copy()
    year_totals_ev = ev_total.groupby("year")["จำนวน"].transform("sum")
    ev_total["share_pct"] = ev_total["จำนวน"] / year_totals_ev * 100

    fig_share = go.Figure()
    for brand in top_ev_2025:
        sub = ev_total[ev_total["brand"] == brand].sort_values("year")
        fig_share.add_trace(go.Bar(
            name=brand, x=sub["year"], y=sub["share_pct"],
            marker_color=BRAND_COLORS.get(brand, "#888"),
            text=[f"{v:.0f}%" if v >= 4 else "" for v in sub["share_pct"]],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_share.update_layout(
        **LAYOUT, barmode="stack",
        title="Market share % within EV/Chinese brand segment (top 8)",
        yaxis_title="% share", height=420,
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_share, use_container_width=True)

    st.markdown("#### Registration count comparison table")
    pivot_comp = (
        by_brand_year[by_brand_year["brand"].isin(top_ev_2025)]
        .pivot_table(index="brand", columns="year", values="จำนวน", aggfunc="sum", fill_value=0)
        .astype(int)
    )
    pivot_comp = pivot_comp.reindex(pivot_comp[2025].sort_values(ascending=False).index)
    pivot_comp.columns = [str(c) for c in pivot_comp.columns]
    pivot_comp["Growth 22→25"] = pivot_comp.apply(
        lambda r: f"{r['2025'] / max(r.get('2022', 1), 1):.1f}×", axis=1
    )
    st.dataframe(
        pivot_comp.style.format({c: "{:,}" for c in pivot_comp.columns if c.isdigit()}),
        use_container_width=True,
    )

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.success(
        "**BYD owns the EV segment.** 41,180 units in 2025 — more than AION + DEEPAL + MG combined."
    )
    col2.warning(
        "**MG fading.** Peaked at 29,526 (2022), dropped to 22,665 (2025). "
        "The pioneer advantage has eroded."
    )
    col3.info(
        "**JAECOO is the dark horse.** 0→8,985 in 2025. Budget crossover closest to Atto 3 on price."
    )
    col4.info(
        "**AION accelerating.** 4,127 (2024) → 11,969 (2025) — nearly 3× YoY."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MODEL COMPETITOR MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### BYD top models vs Toyota / Honda / Isuzu competitors")
    st.caption(
        "Segments and competitors based on price overlap and vehicle class. "
        "Prices are approximate Thailand market pricing (2025). "
        "Registration data: DLT 2025 full-year."
    )

    # ── Competitor map cards ───────────────────────────────────────────────────
    # Pre-compute 2025 registration volumes for BYD models and all competitors
    _df25 = df[df["year"] == 2025]

    def _mv(brand: str, kw: str, exclude: str | None = None) -> int:
        mask = (_df25["brand"] == brand) & _df25["model"].str.contains(kw, na=False)
        if exclude:
            mask &= ~_df25["model"].str.contains(exclude, na=False)
        return int(_df25.loc[mask, "จำนวน"].sum())

    # BYD model volumes (special-cased to avoid cross-model contamination)
    BYD_VOL_2025: dict[str, int] = {
        "DOLPHIN":        _mv("BYD", "DOLPHIN"),
        "ATTO 3":         _mv("BYD", "ATTO"),
        "SEALION 6 DM-I": _mv("BYD", "SEALION 6"),
        "SEALION 7":      _mv("BYD", "SEALION 7"),
        "SEAL":           _mv("BYD", "SEAL", exclude="SEALION"),
    }

    PT_BADGE = {
        "BEV":     ("background:#2E86AB;color:white",  "BEV"),
        "PHEV":    ("background:#A23B72;color:white",  "PHEV"),
        "HEV":     ("background:#52B788;color:white",  "HEV"),
        "ICE":     ("background:#BC4749;color:white",  "ICE"),
        "ICE/HEV": ("background:#6A994E;color:white",  "ICE/HEV"),
        "HEV/PHEV":("background:#7c3aed;color:white",  "HEV/PHEV"),
        "Diesel":  ("background:#8B5E3C;color:white",  "Diesel"),
        "REEV":    ("background:#e67e22;color:white",  "REEV"),
    }
    BRAND_BADGE = {
        "TOYOTA": "#CC0000",
        "HONDA":  "#003087",
        "ISUZU":  "#D4A017",
        "MG":     "#FF6B35",
        "AION":   "#00B4D8",
        "JAECOO": "#4361EE",
        "DEEPAL": "#7B2D8B",
    }

    def badge(label: str, style: str) -> str:
        return (f'<span style="font-size:0.7rem;font-weight:700;padding:2px 8px;'
                f'border-radius:4px;{style}">{label}</span>')

    def vol_chip(units: int, color: str = "#111") -> str:
        if units == 0:
            return ""
        return (f'<span style="font-size:0.72rem;font-weight:700;color:{color};'
                f'background:#f3f4f6;border-radius:4px;padding:2px 6px">'
                f'{units:,} units</span>')

    for entry in BYD_COMPETITOR_MAP:
        pt_style, pt_label = PT_BADGE.get(entry["powertrain"], ("background:#888;color:white", entry["powertrain"]))
        byd_vol = BYD_VOL_2025.get(entry["byd_model"], 0)
        byd_vol_txt = f"<strong style='color:#d70c19'>{byd_vol:,}</strong> units (2025)" if byd_vol else ""
        st.markdown(
            f"""
            <div style="border:1px solid #e2ddd6;border-radius:12px;padding:1.25rem 1.5rem;
                        margin-bottom:1rem;background:white;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05)">
              <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem">
                <div style="background:#d70c19;color:white;font-weight:800;font-size:1rem;
                            padding:4px 14px;border-radius:6px;letter-spacing:0.05em">BYD</div>
                <span style="font-size:1.1rem;font-weight:700;color:#111">{entry["byd_model"]}</span>
                {badge(pt_label, pt_style)}
                <span style="font-size:0.8rem;color:#6b7280">{entry["segment"]}</span>
                <span style="margin-left:auto;font-size:0.82rem;color:#555">
                  {entry["price_range"]} &nbsp;·&nbsp; {byd_vol_txt}
                </span>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
            """,
            unsafe_allow_html=True,
        )
        for comp in entry["competitors"]:
            bc = BRAND_BADGE.get(comp["brand"], "#555")
            cpt_style, cpt_label = PT_BADGE.get(comp["powertrain"], ("background:#888;color:white", comp["powertrain"]))
            brand_kw, model_kw = comp["vol_kw"]
            comp_vol = _mv(brand_kw, model_kw)
            st.markdown(
                f'<div style="border:1px solid {bc};border-radius:8px;padding:0.4rem 0.75rem;'
                f'display:inline-flex;align-items:center;gap:0.5rem;background:#fafafa">'
                f'<span style="font-weight:700;font-size:0.78rem;color:{bc}">{comp["brand"]}</span>'
                f'<span style="font-size:0.85rem;color:#111">{comp["model"]}</span>'
                f'{badge(cpt_label, cpt_style)}'
                f'<span style="font-size:0.75rem;color:#6b7280">{comp["price"]}</span>'
                f'{vol_chip(comp_vol, bc)}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.divider()

    # ── Top models from actual registration data ───────────────────────────────
    st.markdown("#### Top-selling models by brand — actual 2025 registration data")
    st.caption("Source: DLT 2025 full-year · passenger cars ≤7 seats")

    def top_models(brand: str, n: int = 6) -> pd.DataFrame:
        return (
            df[(df["brand"] == brand) & (df["year"] == 2025)]
            .groupby("model")["จำนวน"].sum()
            .nlargest(n).reset_index()
            .rename(columns={"model": "Model", "จำนวน": "Units 2025"})
        )

    col_t, col_h, col_i = st.columns(3)

    with col_t:
        st.markdown("##### Toyota — top 6 models (2025)")
        t_df = top_models("TOYOTA", 6)
        fig_t = go.Figure(go.Bar(
            x=t_df["Units 2025"], y=t_df["Model"],
            orientation="h",
            marker_color=BRAND_COLORS["TOYOTA"],
            text=[f"{int(v):,}" for v in t_df["Units 2025"]],
            textposition="outside",
        ))
        fig_t.update_layout(**{**LAYOUT, "margin": dict(l=10, r=60, t=40, b=20)},
                            title="Toyota top models (2025)", height=340)
        st.plotly_chart(fig_t, use_container_width=True)

    with col_h:
        st.markdown("##### Honda — top 6 models (2025)")
        h_df = top_models("HONDA", 6)
        fig_h = go.Figure(go.Bar(
            x=h_df["Units 2025"], y=h_df["Model"],
            orientation="h",
            marker_color=BRAND_COLORS["HONDA"],
            text=[f"{int(v):,}" for v in h_df["Units 2025"]],
            textposition="outside",
        ))
        fig_h.update_layout(**{**LAYOUT, "margin": dict(l=10, r=60, t=40, b=20)},
                            title="Honda top models (2025)", height=340)
        st.plotly_chart(fig_h, use_container_width=True)

    with col_i:
        st.markdown("##### Isuzu — top 4 models (2025)")
        i_df = top_models("ISUZU", 4)
        fig_i = go.Figure(go.Bar(
            x=i_df["Units 2025"], y=i_df["Model"],
            orientation="h",
            marker_color=BRAND_COLORS["ISUZU"],
            text=[f"{int(v):,}" for v in i_df["Units 2025"]],
            textposition="outside",
        ))
        fig_i.update_layout(**{**LAYOUT, "margin": dict(l=10, r=60, t=40, b=20)},
                            title="Isuzu top models (2025)", height=340)
        st.plotly_chart(fig_i, use_container_width=True)

    # Side-by-side registration volume: BYD top models vs competitors
    st.divider()
    st.markdown("#### BYD top models vs key competitor models — 2025 registration volume")

    # Pull actual registration numbers for known models
    MODEL_LOOKUP = {
        "BYD DOLPHIN":        ("BYD",    "DOLPHIN",        None),
        "BYD ATTO 3":         ("BYD",    "ATTO",           None),
        "BYD SEALION 6 DM-I": ("BYD",    "SEALION 6",      None),
        "BYD SEALION 7":      ("BYD",    "SEALION 7",      None),
        "BYD SEAL":           ("BYD",    "SEAL",           "SEALION"),
        "Toyota Yaris Ativ":  ("TOYOTA", "YARIS ATIV",     None),
        "Toyota Yaris Cross": ("TOYOTA", "YARIS CROSS",    None),
        "Toyota Corolla Cross":("TOYOTA","COROLLA CROSS",  None),
        "Toyota Camry":       ("TOYOTA", "CAMRY",          None),
        "Honda City":         ("HONDA",  "CITY",           None),
        "Honda HR-V":         ("HONDA",  "HR-V",           None),
        "Honda CR-V":         ("HONDA",  "CR-V",           None),
        "Honda Accord":       ("HONDA",  "ACCORD",         None),
        "Isuzu D-Max":        ("ISUZU",  "D-MAX",          None),
        "Isuzu MU-X":         ("ISUZU",  "MU-X",           None),
        "MG MG4 Electric":    ("MG",     "MG4",            None),
        "MG S5 EV":           ("MG",     "S5 EV",          None),
        "Aion UT":            ("AION",   "AION UT",        None),
        "Aion Y Plus":        ("AION",   "AION Y",         None),
        "Aion V":             ("AION",   "AION V",         None),
        "Jaecoo 5 EV":        ("JAECOO", "5 EV",           None),
        "Jaecoo 6 EV":        ("JAECOO", "6 EV",           None),
        "Jaecoo 7 SHS":       ("JAECOO", "7 SHS",          None),
        "Deepal S05":         ("DEEPAL", "S05",            "REEV"),
        "Deepal S05 REEV":    ("DEEPAL", "S05 REEV",       None),
        "Deepal S07":         ("DEEPAL", "S07",            None),
    }

    vol_rows = []
    for display_name, (brand, model_kw, excl) in MODEL_LOOKUP.items():
        units = _mv(brand, model_kw, excl)
        if units > 0:
            vol_rows.append({"Model": display_name, "Brand": brand, "Units": units})

    if vol_rows:
        vol_df = pd.DataFrame(vol_rows).sort_values("Units", ascending=True)
        bar_colors = [BRAND_COLORS.get(r, "#888") for r in vol_df["Brand"]]
        fig_vol = go.Figure(go.Bar(
            x=vol_df["Units"], y=vol_df["Model"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:,}" for v in vol_df["Units"]],
            textposition="outside",
        ))
        fig_vol.update_layout(
            **{**LAYOUT, "margin": dict(l=20, r=80, t=50, b=20)},
            title="2025 registrations — BYD top models vs Toyota / Honda / Isuzu competitors",
            height=max(420, 28 * len(vol_df)),
            xaxis_title="New registrations (2025)",
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    st.divider()
    d1, d2, d3 = st.columns(3)
    d1.success(
        "**BYD Dolphin vs Toyota Yaris Ativ:** Dolphin is the #1 BEV model in Thailand. "
        "The Yaris Ativ dominates ICE volume but the gap is closing as BEV incentives hold."
    )
    d2.info(
        "**BYD Atto 3 vs Corolla Cross / HR-V:** The Atto 3 competes directly with Thailand's "
        "best-selling HEV SUVs. Price cuts in 2025 narrowed the gap to ฿629K–849K vs ฿869K–1,069K."
    )
    d3.warning(
        "**BYD Sealion 6 DM-i vs CR-V / Corolla Cross:** The PHEV battleground is emerging. "
        "PHEV registrations doubled Feb→May 2026 — the Sealion 6 DM-i is at the centre of this shift."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TREND & THREAT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    page_header(
        "BYD Trend & Competitive Threat Analysis",
        "Is BYD still #1? Who is catching up? Where is the risk?",
    )

    # ── Pre-compute analytics ──────────────────────────────────────────────────
    by_brand_all = df.groupby(["year", "brand"])["จำนวน"].sum().reset_index()
    total_yr     = df.groupby("year")["จำนวน"].sum()

    # BYD journey: volume + market share + rank
    byd_journey = by_brand_all[by_brand_all["brand"] == "BYD"].copy()
    byd_journey["share_pct"] = byd_journey.apply(
        lambda r: r["จำนวน"] / total_yr.get(r["year"], 1) * 100, axis=1
    )
    byd_journey["rank"] = byd_journey["year"].map(
        lambda yr: int(
            by_brand_all[by_brand_all["year"] == yr]
            .groupby("brand")["จำนวน"].sum()
            .rank(ascending=False)
            .get("BYD", 99)
        )
    )
    # Add 2026 partial row (Jan-Feb from brand data, annualised for trend line)
    by_brand_26   = by_brand_all[by_brand_all["year"] == 2026]
    byd_26_actual = int(by_brand_26[by_brand_26["brand"] == "BYD"]["จำนวน"].sum())
    total_26      = int(by_brand_26["จำนวน"].sum())
    byd_share_26  = byd_26_actual / max(total_26, 1) * 100

    EV_RIVALS = ["JAECOO", "AION", "DEEPAL", "MG", "ORA", "TESLA", "NETA", "XPENG", "ZEEKR"]

    # YoY growth 2024→2025 for EV brands
    def _brand_vol(brand, year):
        sub = by_brand_all[(by_brand_all["brand"] == brand) & (by_brand_all["year"] == year)]
        return int(sub["จำนวน"].sum())

    growth_data = []
    for brand in ["BYD"] + EV_RIVALS:
        v24 = _brand_vol(brand, 2024)
        v25 = _brand_vol(brand, 2025)
        v26 = _brand_vol(brand, 2026)  # Jan–Feb partial
        run_rate = v26 * 6              # annualised
        yoy_25   = (v25 - v24) / max(v24, 1) * 100
        yoy_26   = (run_rate - v25) / max(v25, 1) * 100
        growth_data.append({
            "brand": brand, "v24": v24, "v25": v25,
            "v26_actual": v26, "run_rate_26": run_rate,
            "yoy_25": yoy_25, "yoy_26": yoy_26,
        })
    gdf = pd.DataFrame(growth_data).sort_values("v25", ascending=False)

    # ── Section 1: Verdict banner ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:1.5rem">
        """,
        unsafe_allow_html=True,
    )

    def verdict_card(icon, title, body, color):
        st.markdown(
            f'<div style="background:{color}15;border-left:4px solid {color};'
            f'border-radius:10px;padding:1.1rem 1.25rem">'
            f'<div style="font-size:1.5rem">{icon}</div>'
            f'<div style="font-weight:800;font-size:1rem;color:{color};margin:0.25rem 0">{title}</div>'
            f'<div style="font-size:0.82rem;color:#333;line-height:1.5">{body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    vc1, vc2, vc3 = st.columns(3)
    with vc1:
        verdict_card(
            "✅", "BYD: Still #1 EV brand",
            "BYD held #3 overall in 2025 (behind Toyota & Honda) and jumped to <strong>#2 overall</strong> "
            "in Jan–Feb 2026 with 15.4% market share — the highest single-brand EV share Thailand has recorded. "
            "Within the EV segment, BYD commands over 40% share.",
            "#16a34a",
        )
    with vc2:
        verdict_card(
            "⚠️", "JAECOO: Fastest-growing threat",
            "JAECOO went from 159 units (2024) to 8,985 (2025), then <strong>8,169 in just Jan–Feb 2026</strong>. "
            "Annualised run-rate: ~49,000 — that would make it the #2 Chinese EV brand if the pace holds. "
            "The Jaecoo 5 EV alone accounts for 84% of their volume.",
            "#d97706",
        )
    with vc3:
        verdict_card(
            "📈", "BYD's trend: Accelerating",
            "After a 12% dip in 2024 (ATTO 3 model cycle), BYD rebounded +53% in 2025. "
            "The 2026 annualised run-rate of <strong>~77,000 units</strong> would be +87% vs 2025. "
            "Portfolio diversification (6+ models, BEV + PHEV) is reducing single-model dependency.",
            "#2563eb",
        )

    st.divider()

    # ── Section 2: BYD journey — volume + share + rank ─────────────────────────
    st.markdown("#### BYD's journey: volume, market share & ranking (2022–2026)")
    st.caption("2026 = Jan–Feb partial. Share % based on all passenger car registrations that period.")

    fig_journey = go.Figure()

    # Volume bars
    journey_years = byd_journey["year"].tolist()
    journey_vols  = byd_journey["จำนวน"].tolist()
    bar_colors    = ["#f5a0a8"] * len(journey_years)
    if 2025 in journey_years:
        bar_colors[journey_years.index(2025)] = BYD_RED

    fig_journey.add_trace(go.Bar(
        name="Annual registrations", x=journey_years, y=journey_vols,
        marker_color=bar_colors,
        text=[f"{v:,}" for v in journey_vols],
        textposition="outside",
        yaxis="y1",
    ))
    # Share % line
    fig_journey.add_trace(go.Scatter(
        name="Market share %", x=journey_years, y=byd_journey["share_pct"].tolist(),
        mode="lines+markers+text",
        line=dict(color=GOLD, width=3),
        marker=dict(size=9, color=GOLD),
        text=[f"{v:.1f}%" for v in byd_journey["share_pct"]],
        textposition="top center",
        yaxis="y2",
    ))
    # 2026 partial share annotation
    fig_journey.add_annotation(
        x=2026, y=byd_share_26, text=f"15.4%<br>(Jan–Feb)",
        showarrow=True, arrowhead=2, arrowcolor=GOLD,
        font=dict(color=GOLD, size=11, family="Tahoma"),
        yref="y2", ax=40, ay=-30,
    )

    fig_journey.update_layout(
        **LAYOUT,
        title="BYD annual registrations & passenger-car market share",
        height=420,
        yaxis=dict(title="Registrations", side="left"),
        yaxis2=dict(title="Market share %", side="right", overlaying="y",
                    tickformat=".1f", showgrid=False),
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
        barmode="group",
    )
    st.plotly_chart(fig_journey, use_container_width=True)

    # Rank progression timeline
    rank_html = ""
    rank_labels = {2022: "#22", 2023: "#5", 2024: "#4", 2025: "#3", 2026: "#2*"}
    colors_map  = {2022: "#cbd5e1", 2023: "#94a3b8", 2024: "#f59e0b", 2025: BYD_RED, 2026: "#16a34a"}
    for yr, lbl in rank_labels.items():
        c = colors_map[yr]
        rank_html += (
            f'<div style="text-align:center">'
            f'<div style="font-size:1.6rem;font-weight:900;color:{c}">{lbl}</div>'
            f'<div style="font-size:0.72rem;color:#6b7280">{yr}{"*" if yr==2026 else ""}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="display:flex;justify-content:space-around;align-items:center;'
        f'background:#f8f9fa;border-radius:10px;padding:1rem 1.5rem;margin-bottom:0.5rem">'
        f'<div style="font-size:0.75rem;font-weight:700;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.1em">BYD overall rank</div>'
        f'{rank_html}'
        f'</div>'
        f'<p style="font-size:0.72rem;color:#9ca3af;margin:0">* 2026 = Jan–Feb partial data</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Section 3: 2024→2025 vs 2025→2026 run-rate growth comparison ──────────
    st.markdown("#### Who is growing fastest? YoY growth rate comparison")
    st.caption(
        "Left bars = 2024→2025 actual growth. Right bars = 2025 vs 2026 annualised run-rate (Jan–Feb × 6). "
        "Brands with negative 2026 run-rate are contracting."
    )

    gdf_plot = gdf[gdf["v25"] > 500].copy()   # filter noise

    fig_growth = go.Figure()
    fig_growth.add_trace(go.Bar(
        name="YoY growth 2024→2025",
        x=gdf_plot["brand"],
        y=gdf_plot["yoy_25"].clip(-100, 600),
        marker_color=[BYD_RED if b == "BYD" else BRAND_COLORS.get(b, "#94a3b8")
                      for b in gdf_plot["brand"]],
        text=[f"{v:+.0f}%" for v in gdf_plot["yoy_25"].clip(-100, 600)],
        textposition="outside",
    ))
    fig_growth.add_trace(go.Bar(
        name="Run-rate growth 2025→2026*",
        x=gdf_plot["brand"],
        y=gdf_plot["yoy_26"].clip(-100, 600),
        marker=dict(
            color=[BYD_RED if b == "BYD" else BRAND_COLORS.get(b, "#94a3b8")
                   for b in gdf_plot["brand"]],
            opacity=0.45,
        ),
        text=[f"{v:+.0f}%" for v in gdf_plot["yoy_26"].clip(-100, 600)],
        textposition="outside",
    ))
    fig_growth.update_layout(
        **LAYOUT, barmode="group",
        title="EV brand growth rate: 2024→2025 actual vs 2025→2026 annualised run-rate",
        yaxis_title="YoY growth %", height=460,
        xaxis_tickangle=-20,
        legend=dict(orientation="h", y=1.08),
        yaxis=dict(range=[-120, 650]),
    )
    st.plotly_chart(fig_growth, use_container_width=True)

    st.divider()

    # ── Section 4: Threat matrix — size vs growth ─────────────────────────────
    st.markdown("#### Competitive threat matrix — 2025 volume vs 2026 growth rate")
    st.caption(
        "Bubble size = 2026 annualised run-rate. "
        "Top-right quadrant = large AND fast-growing = highest threat to BYD."
    )

    fig_bubble = go.Figure()
    for _, row in gdf.iterrows():
        brand = row["brand"]
        if row["v25"] < 100 and row["run_rate_26"] < 500:
            continue
        is_byd = brand == "BYD"
        fig_bubble.add_trace(go.Scatter(
            x=[row["v25"]],
            y=[min(row["yoy_26"], 600)],
            mode="markers+text",
            name=brand,
            marker=dict(
                size=max(12, min(70, row["run_rate_26"] / 1000)),
                color=BRAND_COLORS.get(brand, "#888"),
                line=dict(width=3 if is_byd else 1, color="white"),
                opacity=0.85,
            ),
            text=[brand],
            textposition="top center",
            textfont=dict(size=11, color=BRAND_COLORS.get(brand, "#333"),
                          family="Tahoma"),
            showlegend=False,
        ))
    # Quadrant lines
    median_v25 = gdf[gdf["v25"] > 500]["v25"].median()
    fig_bubble.add_vline(x=median_v25, line_dash="dash", line_color="#d1d5db", line_width=1)
    fig_bubble.add_hline(y=0, line_dash="dash", line_color="#d1d5db", line_width=1)
    fig_bubble.add_annotation(x=median_v25 * 1.6, y=550,
        text="<b>⚠ High threat</b><br>Large & fast-growing",
        showarrow=False, font=dict(size=10, color="#d97706"),
        bgcolor="#fef9c3", bordercolor="#d97706", borderwidth=1)
    fig_bubble.add_annotation(x=median_v25 * 0.2, y=550,
        text="<b>Rising challenger</b><br>Small but fast",
        showarrow=False, font=dict(size=10, color="#2563eb"),
        bgcolor="#eff6ff", bordercolor="#2563eb", borderwidth=1)
    fig_bubble.add_annotation(x=median_v25 * 1.6, y=-80,
        text="<b>Fading giant</b><br>Large but shrinking",
        showarrow=False, font=dict(size=10, color="#dc2626"),
        bgcolor="#fef2f2", bordercolor="#dc2626", borderwidth=1)
    fig_bubble.update_layout(
        **LAYOUT,
        title="Threat matrix: 2025 volume (x) vs 2026 run-rate growth % (y) · bubble = 2026 annualised volume",
        xaxis_title="2025 registrations",
        yaxis_title="2026 annualised run-rate growth % vs 2025",
        height=520,
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.divider()

    # ── Section 5: Volume vs run-rate table ────────────────────────────────────
    st.markdown("#### Brand performance table — 2024, 2025, 2026 run-rate")

    tbl = gdf[gdf["v25"] > 200].copy()
    tbl["2026 run-rate"] = tbl["run_rate_26"].astype(int)
    tbl["YoY 24→25"]     = tbl["yoy_25"].map(lambda x: f"{x:+.0f}%")
    tbl["Run-rate vs 25"] = tbl["yoy_26"].map(lambda x: f"{x:+.0f}%")
    tbl_display = tbl[["brand", "v24", "v25", "2026 run-rate", "YoY 24→25", "Run-rate vs 25"]].rename(
        columns={"brand": "Brand", "v24": "2024", "v25": "2025"}
    ).set_index("Brand")

    def highlight_brand(s):
        return ["background-color:#fef2f2;font-weight:bold" if s.name == "BYD" else "" for _ in s]

    def color_growth(val):
        try:
            n = float(val.replace("%", "").replace("+", ""))
            if n > 100:  return "color:#16a34a;font-weight:700"
            if n > 0:    return "color:#15803d"
            return "color:#dc2626;font-weight:700"
        except Exception:
            return ""

    st.dataframe(
        tbl_display.style
            .apply(highlight_brand, axis=1)
            .applymap(color_growth, subset=["YoY 24→25", "Run-rate vs 25"])
            .format({"2024": "{:,}", "2025": "{:,}", "2026 run-rate": "{:,}"}),
        use_container_width=True,
    )
    st.caption("* 2026 run-rate = Jan–Feb 2026 actual × 6. Annualised estimate; does not account for seasonality.")

    st.divider()

    # ── Section 6: JAECOO deep-dive — the biggest near-term threat ─────────────
    st.markdown("#### The JAECOO threat — a closer look")
    col_j1, col_j2 = st.columns([2, 1])

    with col_j1:
        # JAECOO vs BYD trajectory
        compare_brands = ["BYD", "JAECOO", "AION", "DEEPAL"]
        fig_threat = go.Figure()
        for brand in compare_brands:
            sub = by_brand_all[by_brand_all["brand"] == brand].sort_values("year")
            is_byd = brand == "BYD"
            fig_threat.add_trace(go.Scatter(
                x=sub["year"], y=sub["จำนวน"],
                name=brand, mode="lines+markers",
                line=dict(color=BRAND_COLORS.get(brand, "#888"),
                          width=4 if is_byd else 2,
                          dash="solid" if is_byd else "dot"),
                marker=dict(size=9 if is_byd else 6),
            ))
        # Add 2026 partial bars as separate scatter points
        for brand in compare_brands:
            v26 = _brand_vol(brand, 2026)
            if v26 > 0:
                fig_threat.add_trace(go.Scatter(
                    x=[2026], y=[v26],
                    mode="markers+text",
                    name=f"{brand} (2026 partial)",
                    marker=dict(size=12, color=BRAND_COLORS.get(brand, "#888"),
                                symbol="diamond"),
                    text=[f"{v26:,}"],
                    textposition="top center",
                    showlegend=False,
                ))
        fig_threat.update_layout(
            **LAYOUT,
            title="BYD vs fastest-growing rivals — registration trajectory",
            yaxis_title="Annual registrations", height=420,
            legend=dict(orientation="h", y=1.08),
            xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
        )
        st.plotly_chart(fig_threat, use_container_width=True)

    with col_j2:
        st.markdown("##### Why JAECOO is the #1 risk")
        jaecoo_j5_26 = int(df[
            (df["brand"] == "JAECOO") & (df["year"] == 2026) &
            df["model"].str.contains("5 EV", na=False)
        ]["จำนวน"].sum())
        jaecoo_total_26 = _brand_vol("JAECOO", 2026)

        st.markdown(
            f"""
            <div style="background:#fff7ed;border-left:4px solid #d97706;
                        border-radius:8px;padding:1rem 1.1rem;margin-bottom:0.75rem">
              <strong style="color:#d97706">Scale speed</strong><br>
              <span style="font-size:0.82rem">159 units in 2024 → 8,985 in 2025 → 8,169 in <em>just Jan–Feb 2026</em>.
              Annualised to ~49,000 — that puts JAECOO ahead of MG and within striking distance of HONDA in the EV segment.</span>
            </div>
            <div style="background:#fff7ed;border-left:4px solid #d97706;
                        border-radius:8px;padding:1rem 1.1rem;margin-bottom:0.75rem">
              <strong style="color:#d97706">Single-model concentration</strong><br>
              <span style="font-size:0.82rem">Jaecoo 5 EV = {jaecoo_j5_26:,} of {jaecoo_total_26:,} units (Jan–Feb 2026) —
              <strong>{jaecoo_j5_26/max(jaecoo_total_26,1)*100:.0f}%</strong> from one model.
              If JAECOO 5 EV matches BYD Atto 3 head-to-head on price, BYD's compact SUV flank is exposed.</span>
            </div>
            <div style="background:#f0fdf4;border-left:4px solid #16a34a;
                        border-radius:8px;padding:1rem 1.1rem">
              <strong style="color:#16a34a">BYD's defence</strong><br>
              <span style="font-size:0.82rem">BYD Atto 3 price cuts (฿629K vs Jaecoo 5 EV ~฿779K),
              stronger brand trust, wider service network, and the PHEV Sealion 6 DM-i
              give BYD structural moats JAECOO has not yet built.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Section 7: BYD 2023→2024 dip explained ────────────────────────────────
    st.markdown("#### Understanding the 2023→2024 dip: model cycle, not demand collapse")

    byd_model_trend = (
        df[df["brand"] == "BYD"]
        .groupby(["year", "model"])["จำนวน"].sum()
        .reset_index()
    )

    # Classify into model families
    def family(m):
        if "DOLPHIN" in m: return "DOLPHIN family"
        if "ATTO" in m:    return "ATTO 3 family"
        if "SEAL" in m and "SEALION" not in m: return "SEAL family"
        if "SEALION 6" in m: return "SEALION 6 DM-i"
        if "SEALION 7" in m: return "SEALION 7"
        return "Other"

    byd_model_trend["family"] = byd_model_trend["model"].apply(family)
    byd_family = byd_model_trend.groupby(["year", "family"])["จำนวน"].sum().reset_index()

    fig_family = go.Figure()
    family_colors = {
        "ATTO 3 family":  "#E63946",
        "DOLPHIN family": "#2E86AB",
        "SEAL family":    "#A23B72",
        "SEALION 6 DM-i": "#8338EC",
        "SEALION 7":      "#06D6A0",
        "Other":          "#adb5bd",
    }
    for fam, color in family_colors.items():
        sub = byd_family[byd_family["family"] == fam]
        if sub["จำนวน"].sum() == 0:
            continue
        fig_family.add_trace(go.Bar(
            name=fam, x=sub["year"], y=sub["จำนวน"],
            marker_color=color,
            text=[f"{int(v):,}" if v > 300 else "" for v in sub["จำนวน"]],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_family.update_layout(
        **LAYOUT, barmode="stack",
        title="BYD model family contribution — the 2023→2024 portfolio transition",
        yaxis_title="Registrations", height=420,
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_family, use_container_width=True)

    fa, fb, fc = st.columns(3)
    fa.info(
        "**2023 spike:** The original BYD ATTO 3 drove 16,836 units — 55% of all BYD registrations. "
        "Demand was pent-up from BYD's late-2022 entry."
    )
    fb.warning(
        "**2023→2024 dip (–12%):** The old ATTO 3 faded fast (16,836 → 4,353). "
        "New refreshed variants (410KM, 480KM) hadn't ramped. "
        "This was a product cycle gap, not market share loss."
    )
    fc.success(
        "**2025 recovery (+53%):** DOLPHIN, new ATTO 3 variants, SEALION 7, and the new "
        "SEALION 6 DM-i collectively pushed BYD to 41,180 — its highest-ever annual total. "
        "Portfolio breadth now covers every major segment."
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # Section 8: PHEV Market Deep Dive
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### ⚡ PHEV Market Deep Dive — The Emerging Battleground")
    st.caption(
        "PHEV = plug-in hybrids (incl. DM-i, REEV/range-extender, SHS). "
        "Model-level data from DLT brand/model CSVs; total market size from DLT annual fuel-type files."
    )

    # Build PHEV dataset from brand/model CSV (keyword detection)
    PHEV_KW = ["DM-I", "DMI", "PLUG-IN", "PHEV", "SHS", "REEV", "EREV", "PLUG IN"]
    phev_df = df[df["model"].apply(lambda m: any(k in str(m) for k in PHEV_KW))].copy()

    phev_by_year  = phev_df.groupby("year")["จำนวน"].sum()
    phev_by_brand = phev_df.groupby(["year", "brand"])["จำนวน"].sum().reset_index()

    # ── 8a: PHEV total market — annual fuel data vs model keyword detection ────
    col_pa, col_pb = st.columns(2)

    with col_pa:
        # Use annual_fuel_df for accurate total PHEV market (fuel-type source)
        if not annual_fuel_df.empty and "PHEV" in annual_fuel_df.columns:
            fuel_years = annual_fuel_df["year"].tolist()
            fuel_phev  = annual_fuel_df["PHEV"].tolist()

            # Add 2026 monthly sum
            monthly_phev_26 = int(fuel_df["PHEV"].sum()) if not fuel_df.empty and "PHEV" in fuel_df.columns else 0
            chart_years = fuel_years + [2026]
            chart_phev  = fuel_phev  + [monthly_phev_26]

            fig_phev_tot = go.Figure(go.Bar(
                x=chart_years, y=chart_phev,
                marker_color=[PT_COLORS["PHEV"] if y < 2026 else "#c084fc" for y in chart_years],
                text=[f"{int(v):,}" for v in chart_phev],
                textposition="outside",
            ))
            fig_phev_tot.update_layout(
                **LAYOUT,
                title="Total PHEV registrations — passenger cars (fuel-type source)",
                yaxis_title="Units", height=380,
                xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
            )
            fig_phev_tot.add_annotation(
                x=2026, y=monthly_phev_26,
                text="Jan–May<br>2026",
                showarrow=False,
                yshift=28,
                font=dict(size=10, color="#7c3aed"),
            )
            st.plotly_chart(fig_phev_tot, use_container_width=True)

    with col_pb:
        # PHEV share of total passenger car market per year
        if not annual_fuel_df.empty:
            ann_avail = [c for c in ["BEV", "HEV", "PHEV", "DHEV", "ICE"] if c in annual_fuel_df.columns]
            ann_total = annual_fuel_df[ann_avail].sum(axis=1)
            phev_share_ann = (annual_fuel_df["PHEV"] / ann_total * 100).fillna(0)

            fig_phev_share = go.Figure()
            fig_phev_share.add_trace(go.Scatter(
                x=annual_fuel_df["year"], y=phev_share_ann,
                mode="lines+markers+text",
                line=dict(color=PT_COLORS["PHEV"], width=3),
                marker=dict(size=9),
                text=[f"{v:.2f}%" for v in phev_share_ann],
                textposition="top center",
                name="PHEV share %",
            ))
            # Add HEV share for context
            if "HEV" in annual_fuel_df.columns:
                hev_share = (annual_fuel_df["HEV"] / ann_total * 100).fillna(0)
                fig_phev_share.add_trace(go.Scatter(
                    x=annual_fuel_df["year"], y=hev_share,
                    mode="lines+markers+text",
                    line=dict(color=PT_COLORS["HEV"], width=2, dash="dot"),
                    marker=dict(size=7),
                    text=[f"{v:.1f}%" for v in hev_share],
                    textposition="top center",
                    name="HEV share % (context)",
                ))
            fig_phev_share.update_layout(
                **LAYOUT,
                title="PHEV vs HEV share of passenger car market (2022–2025)",
                yaxis_title="% share", height=380,
                legend=dict(orientation="h", y=1.1),
                xaxis=dict(tickmode="array", tickvals=annual_fuel_df["year"].tolist()),
            )
            st.plotly_chart(fig_phev_share, use_container_width=True)

    # ── 8b: PHEV brand race ────────────────────────────────────────────────────
    st.markdown("##### PHEV brand race — who owns this segment?")

    PHEV_BRAND_COLORS = {
        "BYD":        PT_COLORS["PHEV"],
        "HAVAL":      "#8B5E3C",
        "DEEPAL":     BRAND_COLORS["DEEPAL"],
        "MG":         BRAND_COLORS["MG"],
        "JAECOO":     BRAND_COLORS["JAECOO"],
        "GAC":        "#E63946",
        "MITSUBISHI": "#2c2c54",
        "LAND ROVER": "#1B512D",
    }

    phev_brands_pivot = (
        phev_by_brand
        .pivot_table(index="brand", columns="year", values="จำนวน", aggfunc="sum", fill_value=0)
    )
    if 2025 in phev_brands_pivot.columns:
        phev_brands_pivot = phev_brands_pivot.reindex(
            phev_brands_pivot[2025].sort_values(ascending=False).index
        )

    fig_phev_brand = go.Figure()
    yr_palette = {2022: "#e2e8f0", 2023: "#94a3b8", 2024: "#f59e0b",
                  2025: PT_COLORS["PHEV"], 2026: "#c084fc"}
    for yr in [2022, 2023, 2024, 2025, 2026]:
        if yr not in phev_brands_pivot.columns:
            continue
        fig_phev_brand.add_trace(go.Bar(
            name=str(yr),
            x=phev_brands_pivot.index.tolist(),
            y=phev_brands_pivot[yr].values,
            marker_color=yr_palette[yr],
            text=[f"{int(v):,}" if v > 30 else "" for v in phev_brands_pivot[yr].values],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_phev_brand.update_layout(
        **LAYOUT, barmode="group",
        title="PHEV registrations by brand (2022–2026)",
        yaxis_title="Units", height=420,
        legend=dict(orientation="h", y=1.08),
        xaxis_tickangle=-15,
    )
    st.plotly_chart(fig_phev_brand, use_container_width=True)

    # ── 8c: Top PHEV models 2025 and 2026 ─────────────────────────────────────
    col_pm1, col_pm2 = st.columns(2)

    with col_pm1:
        st.markdown("**Top PHEV models — 2025**")
        phev_models_25 = (
            phev_df[phev_df["year"] == 2025]
            .groupby(["brand", "model"])["จำนวน"].sum()
            .reset_index().sort_values("จำนวน", ascending=True)
        )
        bar_c25 = [PHEV_BRAND_COLORS.get(r, "#adb5bd") for r in phev_models_25["brand"]]
        fig_pm25 = go.Figure(go.Bar(
            x=phev_models_25["จำนวน"],
            y=phev_models_25["model"].str.replace("BYD ", "").str.replace(" PLUG-IN HYBRID", " PHEV"),
            orientation="h",
            marker_color=bar_c25,
            text=[f"{int(v):,}" for v in phev_models_25["จำนวน"]],
            textposition="outside",
        ))
        fig_pm25.update_layout(
            **{**LAYOUT, "margin": dict(l=10, r=70, t=40, b=20)},
            title="Top PHEV models (2025)", height=max(340, 30 * len(phev_models_25)),
        )
        st.plotly_chart(fig_pm25, use_container_width=True)

    with col_pm2:
        st.markdown("**Top PHEV models — 2026 (Jan–Feb)**")
        phev_models_26 = (
            phev_df[phev_df["year"] == 2026]
            .groupby(["brand", "model"])["จำนวน"].sum()
            .reset_index().sort_values("จำนวน", ascending=True)
        )
        if not phev_models_26.empty:
            bar_c26 = [PHEV_BRAND_COLORS.get(r, "#adb5bd") for r in phev_models_26["brand"]]
            fig_pm26 = go.Figure(go.Bar(
                x=phev_models_26["จำนวน"],
                y=phev_models_26["model"].str.replace("BYD ", "").str.replace(" PLUG-IN HYBRID", " PHEV"),
                orientation="h",
                marker_color=bar_c26,
                text=[f"{int(v):,}" for v in phev_models_26["จำนวน"]],
                textposition="outside",
            ))
            fig_pm26.update_layout(
                **{**LAYOUT, "margin": dict(l=10, r=70, t=40, b=20)},
                title="Top PHEV models (2026 Jan–Feb)", height=max(300, 30 * len(phev_models_26)),
            )
            st.plotly_chart(fig_pm26, use_container_width=True)
        else:
            st.info("No 2026 PHEV model data available yet.")

    # ── 8d: BYD PHEV share trend ───────────────────────────────────────────────
    st.markdown("##### BYD's grip on the PHEV segment is loosening in 2026")

    phev_share_data = []
    for yr in sorted(phev_df["year"].unique()):
        tot = phev_by_year.get(yr, 0)
        byd = int(phev_df[(phev_df["brand"] == "BYD") & (phev_df["year"] == yr)]["จำนวน"].sum())
        others = {
            b: int(phev_df[(phev_df["brand"] == b) & (phev_df["year"] == yr)]["จำนวน"].sum())
            for b in ["HAVAL", "DEEPAL", "MG", "JAECOO", "GAC", "MITSUBISHI", "LAND ROVER"]
            if int(phev_df[(phev_df["brand"] == b) & (phev_df["year"] == yr)]["จำนวน"].sum()) > 0
        }
        phev_share_data.append({"year": yr, "BYD": byd, **others})

    phev_share_df = pd.DataFrame(phev_share_data).fillna(0).set_index("year")
    phev_share_pct = phev_share_df.div(phev_share_df.sum(axis=1), axis=0) * 100

    fig_phev_share_brand = go.Figure()
    share_brand_colors = {
        "BYD":        PT_COLORS["PHEV"],
        "HAVAL":      "#8B5E3C",
        "DEEPAL":     BRAND_COLORS["DEEPAL"],
        "MG":         BRAND_COLORS["MG"],
        "JAECOO":     BRAND_COLORS["JAECOO"],
        "GAC":        "#E63946",
        "MITSUBISHI": "#2c2c54",
        "LAND ROVER": "#1B512D",
    }
    for brand in phev_share_pct.columns:
        fig_phev_share_brand.add_trace(go.Bar(
            name=brand,
            x=phev_share_pct.index.tolist(),
            y=phev_share_pct[brand].tolist(),
            marker_color=share_brand_colors.get(brand, "#adb5bd"),
            text=[f"{v:.0f}%" if v >= 5 else "" for v in phev_share_pct[brand]],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10),
        ))
    fig_phev_share_brand.update_layout(
        **LAYOUT, barmode="stack",
        title="PHEV market share by brand (% of PHEV segment)",
        yaxis_title="% share", height=380,
        legend=dict(orientation="h", y=1.08),
        xaxis=dict(tickmode="array", tickvals=ALL_YEARS),
    )
    st.plotly_chart(fig_phev_share_brand, use_container_width=True)

    # ── 8e: Insights ──────────────────────────────────────────────────────────
    p1, p2, p3, p4 = st.columns(4)

    byd_phev_25 = int(phev_df[(phev_df["brand"] == "BYD") & (phev_df["year"] == 2025)]["จำนวน"].sum())
    byd_phev_26 = int(phev_df[(phev_df["brand"] == "BYD") & (phev_df["year"] == 2026)]["จำนวน"].sum())
    tot_phev_25 = int(phev_by_year.get(2025, 0))
    tot_phev_26 = int(phev_by_year.get(2026, 0))
    deepal_26   = int(phev_df[(phev_df["brand"] == "DEEPAL") & (phev_df["year"] == 2026)]["จำนวน"].sum())
    jaecoo_26   = int(phev_df[(phev_df["brand"] == "JAECOO") & (phev_df["year"] == 2026)]["จำนวน"].sum())

    p1.success(
        f"**PHEV exploded in 2025.**\n\n"
        f"{tot_phev_25:,} PHEV units registered — a **10×** jump vs 2024 (957 units). "
        "BYD's DM-i launch single-handedly created the modern Thai PHEV market."
    )
    p2.info(
        f"**BYD owns 78.6% of PHEV in 2025.**\n\n"
        "Sealion 6 DM-i Premium (6,309) + DM-i Dynamic (1,465) + Seal 5 DM-i (650) = "
        f"{byd_phev_25:,} of {tot_phev_25:,} total PHEV units."
    )
    p3.warning(
        f"**BYD's PHEV share is under pressure in 2026.**\n\n"
        f"BYD = {byd_phev_26:,} of {tot_phev_26:,} units ({byd_phev_26/max(tot_phev_26,1)*100:.0f}%) Jan–Feb 2026. "
        f"DEEPAL S05 REEV ({deepal_26:,}) and JAECOO 7 SHS ({jaecoo_26:,}) are entering fast — "
        "BYD's PHEV monopoly is eroding."
    )
    p4.warning(
        "**Haval H6 PHEV: the incumbent.**\n\n"
        "Haval had the market to itself in 2022–2024 (peak 1,167 in 2023). "
        "BYD's arrival crushed its share. Haval H6 PHEV still sells ~600/yr — "
        "loyal buyers who want a trusted ICE brand with plug-in capability."
    )
