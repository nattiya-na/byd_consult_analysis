"""Shared helpers for the BYD EV survey analysis notebook."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Column-layout constants ────────────────────────────────────────────────────

NEW_NAMES = [
    "timestamp", "location", "age_range", "gender", "occupation",
    "monthly_income", "purchase_decision_role", "household_size",
    "cars_owned_count", "current_powertrains_owned", "daily_driving_distance",
    "charging_convenience", "familiarity_ice", "familiarity_hev",
    "familiarity_phev", "familiarity_reev", "familiarity_bev",
    "powertrain_considering", "powertrain_choose_today", "budget_range",
    "brands_considering", "byd_considering_reason", "byd_not_considering_reason",
    "purchase_factors_top3", "purchase_factor_most_important", "byd_view_factor",
    "likelihood_switch_ev_3y", "ev_adoption_barriers", "info_sources",
]

MULTI_COLS = [
    "current_powertrains_owned", "powertrain_considering",
    "purchase_factors_top3", "ev_adoption_barriers", "info_sources",
]

FAMILIARITY_COLS = [
    "familiarity_ice", "familiarity_hev", "familiarity_phev",
    "familiarity_reev", "familiarity_bev",
]

SKIP_ENGLISH = {"age_range"}

# Motor show column mapping: position in motor_show_survey.csv → NEW_NAMES slot
MS_COL_INDICES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    19, 44, 20, 21, 45, 46, 41, 43, 17, 38, 39, 40,
]

# survey_china.xlsx column mapping (0-based) for NEW_NAMES[2:]
CHINA_COL_REST = [
    13, 14, 16, 17, 18, 20, 21, 22, 23, 24, 25, 28, 29, 27, 26,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
]

BASE_AGE_ORDER = ["18–24", "25–34", "35–44", "45–54", "55+"]

INCOME_CANONICAL_ORDER = [
    "Below 15,000 THB",
    "15,001 – 30,000 THB",
    "30,001 – 60,000 THB",
    "60,001 – 100,000 THB",
    "100,001 – 150,000 THB",
    "150,001 – 200,000 THB",
    "Above 200,000 THB",
]

_INCOME_RANGE_TO_LABEL: dict[tuple[int, int], str] = {
    (15001, 30000): "15,001 – 30,000 THB",
    (30001, 60000): "30,001 – 60,000 THB",
    (60001, 100000): "60,001 – 100,000 THB",
    (100001, 150000): "100,001 – 150,000 THB",
    (150001, 200000): "150,001 – 200,000 THB",
}

DD_CANONICAL_ORDER = [
    "Less than 10 km", "10 – 20 km", "21 – 50 km",
    "51 – 100 km", "More than 100 km",
]

HH_PROXY_ORDER = [
    "No car",
    "≥1 car, fewer cars than people",
    "≥1 car, as many cars as number of people",
    "≥1 car, more cars than people",
]

STAGE_ORDER = [
    "Ready to book / buy now",
    "Planning to buy within 6 months",
    "Planning to buy within 7–12 months",
    "Researching options for future purchase",
    "Not planning to buy; just browsing / accompanying someone",
]

POWERTRAIN_COLORS = {
    "BEV": "#2E86AB", "PHEV": "#A23B72", "REEV": "#F18F01",
    "HEV": "#6A994E", "ICE": "#BC4749", "Not sure": "#95A3A6", "Other": "#C9C9C9",
}

PT_ORDER = ["BEV", "PHEV", "REEV", "HEV", "ICE", "Not sure", "Other"]

FONT_FAMILY = "Noto Sans Thai, Thonburi, Tahoma, DejaVu Sans, sans-serif"

# ── Text / NLP helpers ─────────────────────────────────────────────────────────

_PAREN_EN = re.compile(r"\(([^)]*)\)")


def extract_english(text) -> str | float:
    """Return the best English fragment from a bilingual Thai/English string."""
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return np.nan
    s = str(text).strip()
    if not s:
        return np.nan

    def latin_score(fragment: str) -> int:
        return len(re.findall(r"[A-Za-z]", fragment))

    candidates = _PAREN_EN.findall(s)
    best, best_score = None, 0
    for frag in candidates:
        sc = latin_score(frag)
        if sc >= 3 and sc >= best_score:
            best, best_score = frag, sc
    if best is not None:
        out = best.strip()
    elif " - " in s:
        out = s.rsplit(" - ", 1)[-1].strip()
    elif " / " in s:
        out = s.rsplit(" / ", 1)[-1].strip()
    else:
        out = s

    out = re.sub(r"\s+", " ", out).strip()
    if not out:
        return np.nan
    out_no_thai = re.sub(r"[฀-๿]+", " ", out).strip()
    out_no_thai = re.sub(r"\s+", " ", out_no_thai)
    if latin_score(out_no_thai) >= 2:
        out = out_no_thai
    elif latin_score(out) < 2:
        fallback = re.sub(r"[฀-๿]+", " ", s).strip()
        fallback = re.sub(r"\s+", " ", fallback)
        return fallback if latin_score(fallback) >= 1 else np.nan
    return out


def clean_multiselect(val) -> str | float:
    """Extract English from each comma-separated part and rejoin with '; '."""
    if pd.isna(val):
        return val
    parts = [p.strip() for p in str(val).split(",") if p.strip()]
    cleaned = [extract_english(p) for p in parts]
    cleaned = [c for c in cleaned if pd.notna(c) and str(c).strip()]
    return "; ".join(cleaned) if cleaned else np.nan


def split_brand_segments(val) -> list[str]:
    """Split a brand string on comma or semicolon (ASCII and fullwidth CJK)."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    s = str(val).strip()
    if not s:
        return []
    parts = re.split(r"\s*[,;，；]\s*", s)
    return [p.strip() for p in parts if p.strip()]


def clean_brands(val) -> str | float:
    """Extract English from each brand segment and rejoin with '; '."""
    if pd.isna(val):
        return val
    parts = split_brand_segments(val)
    out = []
    for p in parts:
        if not p.strip():
            continue
        e = extract_english(p)
        if pd.notna(e) and str(e).strip():
            out.append(str(e).strip())
        else:
            t = re.sub(r"[฀-๿]+", " ", p)
            t = re.sub(r"\s+", " ", t).strip()
            if t:
                out.append(t)
    return "; ".join(out) if out else np.nan


# ── Normalization ──────────────────────────────────────────────────────────────

def parse_count_from_english(s, *, cars: bool = False) -> int:
    if pd.isna(s):
        return np.nan
    t = str(s).lower()
    if cars and ("do not own" in t or t.strip() == "0"):
        return 0
    if "or more" in t:
        m = re.search(r"(\d+)", t)
        return int(m.group(1)) if m else np.nan
    m = re.search(r"\b(\d+)\b", t)
    return int(m.group(1)) if m else np.nan


def normalize_age_range(val) -> str:
    """Map raw age labels (including numeric ages from survey_china) to BASE_AGE_ORDER."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if not s:
        return np.nan
    num = pd.to_numeric(s, errors="coerce")
    if pd.notna(num):
        a = int(round(float(num)))
        if a < 18:
            return np.nan
        if a <= 24: return "18–24"
        if a <= 34: return "25–34"
        if a <= 44: return "35–44"
        if a <= 54: return "45–54"
        return "55+"
    t = s.replace("–", "-").replace("—", "-")
    t = re.sub(r"\s*-\s*", "-", t)
    ascii_to_canon = {
        "18-24": "18–24", "25-34": "25–34", "35-44": "35–44",
        "45-54": "45–54", "55+": "55+",
    }
    if t in ascii_to_canon:
        return ascii_to_canon[t]
    if s in BASE_AGE_ORDER:
        return s
    return s


def normalize_monthly_income(val) -> str:
    """Map income options (incl. survey_china spacing / duplicated text) to canonical labels."""
    if pd.isna(val):
        return np.nan
    raw = str(val).strip()
    if not raw:
        return np.nan
    if raw in INCOME_CANONICAL_ORDER:
        return raw
    s_clean = raw.replace("\xa0", " ").replace(" ", " ")
    s_clean = re.sub(r"\s+", " ", s_clean).strip()
    s_low = s_clean.lower()
    if "below" in s_low:
        return "Below 15,000 THB"
    if "above" in s_low:
        return "Above 200,000 THB"
    if "ต่ำกว่า" in raw:
        return "Below 15,000 THB"
    if "มากกว่า" in raw:
        return "Above 200,000 THB"
    m = re.search(
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*[––\-]\s*(\d{1,3}(?:,\d{3})+|\d+)",
        s_clean,
    )
    if not m:
        return np.nan
    lo = int(m.group(1).replace(",", ""))
    hi = int(m.group(2).replace(",", ""))
    return _INCOME_RANGE_TO_LABEL.get((lo, hi), np.nan)


def _income_sort_key(label):
    s = str(label).lower()
    if "below" in s:
        m = re.search(r"([\d,]+)", str(label))
        return (0, float(m.group(1).replace(",", "")) if m else 0.0)
    if "above" in s:
        m = re.search(r"([\d,]+)", str(label))
        return (2, float(m.group(1).replace(",", "")) if m else 1e9)
    m = re.search(r"([\d,]+)\s*[–\-]\s*([\d,]+)", str(label))
    if m:
        return (1, float(m.group(1).replace(",", "")))
    return (1, 0.0)


def normalize_daily_driving_distance(val) -> str:
    """Map daily distance labels (Thai/English, Forms variants) to DD_CANONICAL_ORDER."""
    if pd.isna(val):
        return np.nan
    raw = str(val).strip()
    if not raw:
        return np.nan
    if raw in DD_CANONICAL_ORDER:
        return raw
    s = raw.replace("\xa0", " ").replace(" ", " ")
    s = re.sub(r"\s+", " ", s).strip()
    no_thai = re.sub(r"[฀-๿]+", " ", s)
    no_thai = re.sub(r"\s+", " ", no_thai).strip()
    sl = no_thai.lower()
    if re.search(r"less\s+than\s*10\b", sl) or sl.startswith("less than 10"):
        return "Less than 10 km"
    if re.search(r"more\s+than\s*100\b", sl):
        return "More than 100 km"
    if "น้อยกว่า" in raw:
        return "Less than 10 km"
    if "มากกว่า" in raw:
        return "More than 100 km"
    for a, b in re.findall(r"(\d+)\s*[––\-]\s*(\d+)", s):
        a, b = int(a), int(b)
        if (a, b) == (10, 20): return "10 – 20 km"
        if (a, b) == (21, 50): return "21 – 50 km"
        if (a, b) == (51, 100): return "51 – 100 km"
    return np.nan


# ── Data loading ───────────────────────────────────────────────────────────────

def _china_location(raw: pd.DataFrame) -> pd.Series:
    """Combine region (col 6) with the first non-empty province cell (cols 7–12)."""
    region = raw.iloc[:, 6]
    detail = raw.iloc[:, 7:13]
    finest = detail.apply(
        lambda row: next((v for v in row if pd.notna(v) and str(v).strip()), np.nan),
        axis=1,
    )
    out = []
    for r, f in zip(region, finest):
        if pd.notna(f) and pd.notna(r):
            out.append(f"{r} — {f}")
        elif pd.notna(f):
            out.append(str(f))
        elif pd.notna(r):
            out.append(str(r))
        else:
            out.append(np.nan)
    return pd.Series(out, index=raw.index, dtype=object)


def load_data(
    data_path: Path | str,
    motor_show_path: Path | str,
    china_path: Path | str,
) -> pd.DataFrame:
    """Load and combine all three survey sources into a single raw DataFrame."""
    data_path = Path(data_path)
    motor_show_path = Path(motor_show_path)
    china_path = Path(china_path)

    # General online CSV
    df_raw = pd.read_csv(data_path)
    df_raw.columns = df_raw.columns.str.strip()
    if len(df_raw.columns) != len(NEW_NAMES):
        raise ValueError(
            f"Expected {len(NEW_NAMES)} columns, got {len(df_raw.columns)}. "
            "Update NEW_NAMES to match the export."
        )
    df_general = df_raw.copy()
    df_general.columns = NEW_NAMES
    df_general["data_source"] = "general"
    df_general["purchase_stage"] = np.nan

    frames = [df_general]

    # Motor show CSV (optional)
    if motor_show_path.exists():
        motor_show_raw = pd.read_csv(motor_show_path)
        motor_show_raw.columns = motor_show_raw.columns.str.strip()
        if len(MS_COL_INDICES) != len(NEW_NAMES):
            raise ValueError("MS_COL_INDICES must match NEW_NAMES length.")
        if motor_show_raw.shape[1] < max(MS_COL_INDICES) + 1 or motor_show_raw.shape[1] < 19:
            raise ValueError(
                f"Unexpected motor show shape {motor_show_raw.shape}; check MS_COL_INDICES / export."
            )
        ms_aligned = pd.DataFrame(
            {name: motor_show_raw.iloc[:, idx].values for name, idx in zip(NEW_NAMES, MS_COL_INDICES)}
        )
        ms_aligned["data_source"] = "motor_show"
        ms_aligned["purchase_stage"] = motor_show_raw.iloc[:, 18].values
        frames.append(ms_aligned)
    else:
        print(f"[load_data] motor_show file not found, skipping: {motor_show_path}")

    # Survey China XLSX (optional)
    if china_path.exists():
        china_raw = pd.read_excel(china_path)
        china_raw.columns = china_raw.columns.str.strip()
        if china_raw.shape[1] < 42:
            raise ValueError(
                f"Unexpected survey_china shape {china_raw.shape}; expected >= 42 columns."
            )
        _rest_names = NEW_NAMES[2:]
        if len(CHINA_COL_REST) != len(_rest_names):
            raise ValueError(
                f"CHINA_COL_REST length {len(CHINA_COL_REST)} vs NEW_NAMES[2:] ({len(_rest_names)})."
            )
        china_aligned = pd.DataFrame(index=china_raw.index)
        _ts = china_raw.iloc[:, 2]
        if pd.api.types.is_datetime64_any_dtype(_ts):
            china_aligned["timestamp"] = pd.to_datetime(_ts, errors="coerce").dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            china_aligned["timestamp"] = _ts
        china_aligned["location"] = _china_location(china_raw)
        for name, idx in zip(_rest_names, CHINA_COL_REST):
            china_aligned[name] = china_raw.iloc[:, idx].values
        china_aligned["data_source"] = "survey_china"
        china_aligned["purchase_stage"] = china_raw.iloc[:, 19].values
        frames.append(china_aligned)
    else:
        print(f"[load_data] China survey file not found, skipping: {china_path}")

    return pd.concat(frames, ignore_index=True)


def clean_survey(df: pd.DataFrame) -> tuple[pd.DataFrame, list, list, list]:
    """Apply all text normalisation and categorisation to the combined raw frame.

    Returns ``(df_clean, age_order, income_order, dd_order)``.
    """
    df_clean = df.copy()

    for col in df_clean.columns:
        if col in SKIP_ENGLISH or col in {"timestamp", "data_source"}:
            continue
        if col in FAMILIARITY_COLS:
            continue
        if col == "brands_considering":
            df_clean[col] = df_clean[col].map(clean_brands)
            continue
        if col in MULTI_COLS:
            df_clean[col] = df_clean[col].map(clean_multiselect)
        else:
            df_clean[col] = df_clean[col].map(extract_english)

    for col in FAMILIARITY_COLS:
        df_clean[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df_clean["household_size_n"] = df_clean["household_size"].map(
        lambda x: parse_count_from_english(x, cars=False)
    )
    df_clean["cars_owned_count_n"] = df_clean["cars_owned_count"].map(
        lambda x: parse_count_from_english(x, cars=True)
    )

    df_clean["age_range"] = df_clean["age_range"].map(normalize_age_range)
    _seen_age = df_clean["age_range"].dropna().unique().tolist()
    age_order = [a for a in BASE_AGE_ORDER if a in _seen_age] + sorted(
        [x for x in _seen_age if x not in BASE_AGE_ORDER]
    )
    df_clean["age_range"] = pd.Categorical(
        df_clean["age_range"], categories=age_order, ordered=True
    )

    df_clean["monthly_income"] = df_clean["monthly_income"].map(normalize_monthly_income)
    _seen_inc = df_clean["monthly_income"].dropna().unique().tolist()
    income_order = [x for x in INCOME_CANONICAL_ORDER if x in _seen_inc] + sorted(
        [x for x in _seen_inc if x not in INCOME_CANONICAL_ORDER],
        key=_income_sort_key,
    )
    df_clean["monthly_income"] = pd.Categorical(
        df_clean["monthly_income"], categories=income_order, ordered=True
    )

    df_clean["daily_driving_distance"] = df_clean["daily_driving_distance"].map(
        normalize_daily_driving_distance
    )
    _seen_dd = df_clean["daily_driving_distance"].dropna().unique().tolist()
    dd_order = [d for d in DD_CANONICAL_ORDER if d in _seen_dd] + sorted(
        [x for x in _seen_dd if x not in DD_CANONICAL_ORDER],
        key=lambda x: str(x).lower(),
    )
    df_clean["daily_driving_distance"] = pd.Categorical(
        df_clean["daily_driving_distance"], categories=dd_order, ordered=True
    )

    return df_clean, age_order, income_order, dd_order


# ── Plot layout helpers ────────────────────────────────────────────────────────

def thai_layout(fig, height=None, width=None):
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=11),
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=40),
    )
    if height is not None:
        fig.update_layout(height=height)
    if width is not None:
        fig.update_layout(width=width)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def _hbar_trace(vc, colorscale_name="Blues"):
    y = [str(i) for i in vc.index]
    x = vc.values
    n = len(x)
    scale = [i / max(1, n - 1) for i in range(n)]
    cols = plc.sample_colorscale(colorscale_name, scale)
    return go.Bar(x=x, y=y, orientation="h", marker=dict(color=cols), showlegend=False)


def barh_counts(series, title, figsize=(10, 5)):
    _w, _ = figsize
    vc = series.dropna().astype(str).value_counts()
    height = max(360, min(1200, 80 + 22 * max(1, len(vc))))
    if vc.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(title=title)
        thai_layout(fig, height=height, width=int(_w * 80))
        fig.show()
        return
    y = [str(i) for i in vc.index[::-1]]
    x = vc.values[::-1]
    n = len(x)
    scale = [i / max(1, n - 1) for i in range(n)]
    colors = plc.sample_colorscale("Viridis", scale)
    fig = go.Figure(go.Bar(x=x, y=y, orientation="h", marker=dict(color=colors), showlegend=False))
    fig.update_layout(title=title, xaxis_title="Count", yaxis_title="")
    thai_layout(fig, height=height, width=int(_w * 80))
    fig.show()


def count_bar(series, title, order=None, figsize=(10, 5)):
    _w, _ = figsize
    vc = series.dropna().value_counts()
    if order is not None:
        order = [o for o in order if o in vc.index]
        vc = vc.reindex(order).fillna(0).astype(int)
    else:
        vc = vc.sort_values(ascending=True)
    height = max(360, min(1200, 80 + 22 * max(1, len(vc))))
    y = [str(i) for i in vc.index]
    x = vc.values
    n = len(x)
    scale = [i / max(1, n - 1) for i in range(n)]
    colors = plc.sample_colorscale("Blues", scale)
    fig = go.Figure(go.Bar(x=x, y=y, orientation="h", marker=dict(color=colors), showlegend=False))
    fig.update_layout(title=title, xaxis_title="Count", yaxis_title="")
    thai_layout(fig, height=height, width=int(_w * 80))
    fig.show()


def heatmap_crosstab(frame: pd.DataFrame, row: str, col: str, title: str, colorscale: str = "Blues"):
    """Row-normalised heatmap of two categorical columns in *frame*."""
    sub = frame[[row, col]].dropna()
    if sub.empty:
        return
    ct = pd.crosstab(sub[row], sub[col], normalize="index")
    z = ct.values.astype(float)
    text = [[f"{v * 100:.0f}%" if np.isfinite(v) else "" for v in r] for r in z]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[str(c) for c in ct.columns],
            y=[str(i) for i in ct.index],
            text=text,
            texttemplate="%{text}",
            colorscale=colorscale,
            colorbar=dict(title="Share"),
            hovertemplate="row=%{y}<br>col=%{x}<br>share=%{z:.0%}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=col.replace("_", " ").title(),
        yaxis_title=row.replace("_", " ").title(),
    )
    fig.update_xaxes(tickangle=-45)
    thai_layout(fig, height=520, width=1100)
    fig.show()


def grouped_count_bar(df_plot: pd.DataFrame, column: str, title: str, cat_order=None):
    """Side-by-side bar chart comparing a column across the three survey cohorts."""
    fig = go.Figure()
    for src, lab in [
        ("general", "General online"),
        ("motor_show", "Motor show"),
        ("survey_china", "Survey China (Forms)"),
    ]:
        sub = df_plot[df_plot["data_source"] == src]
        vc = sub[column].value_counts()
        if cat_order is not None:
            co = [c for c in cat_order if c in vc.index]
            vc = vc.reindex(co).fillna(0).astype(int)
        else:
            vc = vc.sort_index()
        fig.add_trace(go.Bar(name=lab, x=[str(i) for i in vc.index], y=vc.values))
    fig.update_layout(
        title=title,
        barmode="group",
        xaxis_title=column.replace("_", " ").title(),
        yaxis_title="Count",
        legend_title_text="Cohort",
    )
    fig.update_xaxes(tickangle=-35)
    thai_layout(fig, height=480, width=1000)
    fig.show()


# ── Feature engineering ────────────────────────────────────────────────────────

def short_powertrain_label(val) -> str | float:
    if pd.isna(val):
        return np.nan
    s = str(val).lower()
    if "not sure" in s:
        return "Not sure"
    if "battery electric" in s or re.search(r"\bbev\b", s):
        return "BEV"
    if "plug-in" in s or "phev" in s:
        return "PHEV"
    if "range-extended" in s or "reev" in s:
        return "REEV"
    if "internal combustion" in s or re.search(r"\bice\b", s):
        return "ICE"
    if "hybrid" in s and "plug" not in s:
        return "HEV"
    if "hev" in s:
        return "HEV"
    return "Other"


def split_multiselect(val) -> list[str]:
    if pd.isna(val):
        return []
    parts = re.split(r"[,;，；]\s*", str(val).strip())
    return [p.strip() for p in parts if p and str(p).strip()]


def explode_multiselect(df: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for idx, val in df[col].items():
        for token in split_multiselect(val):
            rows.append({"row": idx, "value": token})
    return pd.DataFrame(rows)


def one_hot_multiselect(df: pd.DataFrame, col: str, prefix: str, min_frequency: int = 1) -> pd.DataFrame:
    long = explode_multiselect(df, col)
    if long.empty:
        return pd.DataFrame(index=df.index)
    vc = long["value"].value_counts()
    keep = vc[vc >= min_frequency].index
    long = long[long["value"].isin(keep)]
    wide = long.assign(x=1).pivot_table(
        index="row", columns="value", values="x", aggfunc="max", fill_value=0
    )
    wide = wide.reindex(df.index, fill_value=0).fillna(0).astype(int)
    safe = {c: prefix + re.sub(r"[^0-9A-Za-z]+", "_", str(c))[:80] for c in wide.columns}
    return wide.rename(columns=safe)


def hh_vehicle_proxy(row) -> str:
    c = int(row["cars_owned_count_n"])
    h = int(row["household_size_n"])
    if c == 0:
        return "No car"
    if c < h:
        return "≥1 car, fewer cars than people"
    if c == h:
        return "≥1 car, as many cars as number of people"
    return "≥1 car, more cars than people"
