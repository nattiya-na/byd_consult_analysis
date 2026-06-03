# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data analysis project studying Thai consumer interest in BYD EVs, combining three survey datasets with qualitative interview analysis. The output is a set of interactive Plotly charts (HTML) and a standalone IMC strategy dashboard.

## Running the Analysis

```bash
# Run all analysis phases (saves charts to output/)
python run_analysis.py

# Run specific phases only
python run_analysis.py --phases 2,3,4

# Skip a phase (phase 10 requires kmodes, may be slow)
python run_analysis.py --skip 10

# Text output only, no files written
python run_analysis.py --no-charts

# Generate the IMC dashboard (produces output/dashboard.html)
python dashboard.py
```

## Web Crawler (byd_web_crawler/)

A separate sub-project with its own dependencies and CLI:

```bash
cd byd_web_crawler
pip install -r requirements.txt
playwright install chromium  # for Facebook crawler

python main.py crawl pantip
python main.py crawl youtube
python main.py crawl all
python main.py analyze fast
python main.py analyze viz
```

## Interview Extraction

```bash
# Reads all .docx files from interviews/ and interviews_2/, writes all_interviews_raw.txt
python extract_interviews.py

# Extracts PHEV-related quotes from all_interviews_raw.txt into phev_quotes_raw.txt
python extract_phev.py
```

## Architecture

### Data Flow

`survey_utils.py` is the shared foundation. All phase modules import from it.

1. **`survey_utils.load_data()`** — merges three sources into one raw DataFrame:
   - `*Form Responses 1.csv` — general online survey (Thai/English bilingual)
   - `motor_show.csv` — motor show booth survey (different column layout, mapped via `MS_COL_INDICES`)
   - `survey_china.xlsx` — China-administered survey (different column layout, mapped via `CHINA_COL_REST`)
   
2. **`survey_utils.clean_survey()`** — normalises all text to English (via `extract_english()`), canonicalises ordinal categories (age, income, driving distance), and returns ordered Categoricals plus the three order lists.

3. **Phase modules** (`phase2_*.py` → `phase11_*.py`) — each exports a `run_phaseN()` function that takes the cleaned DataFrame and calls `fig.show()` / `plt.show()`. `run_analysis.py` monkey-patches these to intercept and save to `output/phaseNN_NN.{html,png}` instead of rendering interactively.

### Key Constants in `survey_utils.py`

- `NEW_NAMES` — canonical 29-column schema all three sources are aligned to
- `MULTI_COLS` — columns where values are comma-separated multi-selects
- `POWERTRAIN_COLORS` / `PT_ORDER` — consistent colours across all charts
- `FONT_FAMILY` — Thai-compatible font stack used everywhere

### Phase Modules

| Phase | File | Content |
|-------|------|---------|
| 2 | `phase2_customer_profile.py` | Demographics, household analysis |
| 3 | `phase3_powertrain_prefs.py` | Powertrain preference breakdowns |
| 4 | `phase4_purchase_factors.py` | Top-3 purchase factors, importance ranking |
| 5 | `phase5_motor_show.py` | Motor show cohort comparison, purchase stage |
| 6 | `phase6_feature_engineering.py` | Derived features (EV readiness index, HH vehicle proxy); **mutates and returns df_plot** |
| 8 | `phase8_barriers_motivation.py` | EV adoption barriers by segment |
| 9 | `phase9_brand_positioning.py` | Brand consideration maps, BYD vs competitors |
| 10 | `phase10_clustering.py` | K-Modes persona clustering (requires `pip install kmodes`) |
| 11 | `phase11_awareness.py` | Brand awareness by age |

Phase 6 is special: it returns an augmented DataFrame that all later phases depend on (adds `powertrain_short`, `ev_readiness_index`, `hh_vehicle_proxy`, one-hot multiselect columns).

### dashboard.py

Standalone script that re-loads and re-cleans data internally, then builds a single multi-section HTML file at `output/dashboard.html`. Targets IMC strategy segmentation: Gen Z (18–24) BEV vs. Middle Age (35–54) PHEV/REEV personas.

### byd_web_crawler/

Independent sub-project. Uses SQLAlchemy + SQLite (`byd_perception.db`), Playwright for Facebook, YouTube Data API v3, Twitter API v2, and BERTopic + XLM-RoBERTa for Thai NLP sentiment/topic modeling. Config via `.env` (not committed).

## Notes

- The main survey CSV has a long Thai filename — always reference it via `DATA_PATH` in `run_analysis.py` or the `_CSV` constant in `dashboard.py`.
- Phase 7 does not exist (left empty in original notebook).
- Charts render to `output/` by default; the directory is created automatically.
- `survey_china.xlsx` replaces `survey_china_old.xlsx` — the old file is kept for reference only.
