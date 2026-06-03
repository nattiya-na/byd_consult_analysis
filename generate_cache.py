"""
Run this locally ONCE (or after any raw-data update) to produce the
deployable data cache used by the Streamlit app.

Usage:
    python generate_cache.py

Outputs:
    data_cache/survey_processed.parquet   — cleaned, feature-engineered DataFrame
    data_cache/meta.json                  — ordered category lists for sidebar filters
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from survey_utils import load_data, clean_survey
from utils.data_loader import _add_features

_CSV = "แบบสอบถามความสนใจในการซื้อรถยนต์ไฟฟ้าทั่วไป (Responses) - Form Responses 1.csv"
DATA_PATH = ROOT / _CSV
MOTOR_SHOW_PATH = ROOT / "motor_show.csv"
CHINA_PATH = ROOT / "survey_china.xlsx"
OUT = ROOT / "data_cache"


def main() -> None:
    print("Loading raw survey files…")
    df_raw = load_data(DATA_PATH, MOTOR_SHOW_PATH, CHINA_PATH)
    print(f"  raw rows: {len(df_raw)}")

    print("Cleaning…")
    df_clean, age_order, income_order, dd_order = clean_survey(df_raw)

    print("Feature engineering…")
    df = _add_features(df_clean)

    # Drop timestamp — not needed by any chart and mildly identifying
    df = df.drop(columns=["timestamp"], errors="ignore")

    OUT.mkdir(exist_ok=True)

    parquet_path = OUT / "survey_processed.parquet"
    df.to_parquet(parquet_path, index=False, engine="pyarrow")
    print(f"  saved {len(df)} rows × {len(df.columns)} cols → {parquet_path.relative_to(ROOT)}")

    meta = {
        "age_order": age_order,
        "income_order": income_order,
        "dd_order": dd_order,
    }
    meta_path = OUT / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"  saved metadata → {meta_path.relative_to(ROOT)}")
    print("Done.")


if __name__ == "__main__":
    main()
