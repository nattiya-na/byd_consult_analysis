#!/usr/bin/env python3
"""Build survey_analysis_refactored.ipynb from the original notebook."""
import ast, json, uuid

with open("survey_analysis.ipynb") as f:
    nb = json.load(f)
orig = nb["cells"]

def _id():
    return uuid.uuid4().hex[:8]

def code(src):
    return {"cell_type": "code", "execution_count": None, "id": _id(),
            "metadata": {}, "outputs": [], "source": src}

def md_cell(cell):
    """Return a copy of an existing markdown cell with a fresh id."""
    c = dict(cell)
    c["id"] = _id()
    return c

def src(i):
    return "".join(orig[i]["source"])

def strip_func_defs(source, names):
    """Remove named top-level function definitions from source via ast."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    lines = source.splitlines(keepends=True)
    remove = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            end = getattr(node, "end_lineno", None)
            if end is None:
                continue
            for ln in range(node.lineno, end + 1):
                remove.add(ln)
    return "".join(l for i, l in enumerate(lines, 1) if i not in remove)

def strip_import_lines(source, *prefixes):
    lines = source.splitlines(keepends=True)
    return "".join(l for l in lines if not any(l.startswith(p) for p in prefixes))

# ── New cell content ──────────────────────────────────────────────────────────

IMPORTS = """\
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.colors as plc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from scipy.stats import chi2_contingency
except ImportError:
    chi2_contingency = None

try:
    from kmodes.kmodes import KModes
except ImportError:
    KModes = None

from survey_utils import (
    NEW_NAMES, MULTI_COLS, FAMILIARITY_COLS, BASE_AGE_ORDER,
    INCOME_CANONICAL_ORDER, DD_CANONICAL_ORDER,
    HH_PROXY_ORDER, STAGE_ORDER, POWERTRAIN_COLORS, PT_ORDER, FONT_FAMILY,
    load_data, clean_survey,
    thai_layout, barh_counts, count_bar, _hbar_trace,
    heatmap_crosstab, grouped_count_bar,
    short_powertrain_label, split_multiselect, split_brand_segments,
    explode_multiselect, one_hot_multiselect, hh_vehicle_proxy,
)

sns.set_theme(style="white", font_scale=1.05)
"""

DATA_LOAD = """\
_CSV_NAME = "\\u0e41\\u0e1a\\u0e1a\\u0e2a\\u0e2d\\u0e1a\\u0e16\\u0e32\\u0e21\\u0e04\\u0e27\\u0e32\\u0e21\\u0e2a\\u0e19\\u0e43\\u0e08\\u0e43\\u0e19\\u0e01\\u0e32\\u0e23\\u0e0b\\u0e37\\u0e49\\u0e2d\\u0e23\\u0e16\\u0e22\\u0e19\\u0e15\\u0e4c\\u0e44\\u0e1f\\u0e1f\\u0e49\\u0e32\\u0e17\\u0e31\\u0e48\\u0e27\\u0e44\\u0e1b (Responses) - Form Responses 1.csv"
_DATA_FALLBACK = Path("/Users/nattiya.n/miniforge3/envs/personal/action lab") / _CSV_NAME

_NB_DIR = Path.cwd()
DATA_PATH = _NB_DIR / _CSV_NAME
if not DATA_PATH.exists():
    DATA_PATH = _DATA_FALLBACK

MOTOR_SHOW_PATH = _NB_DIR / "motor_show_survey.csv"
if not MOTOR_SHOW_PATH.exists():
    MOTOR_SHOW_PATH = _DATA_FALLBACK.parent / "motor_show_survey.csv"

CHINA_PATH = _NB_DIR / "survey_china.xlsx"
if not CHINA_PATH.exists():
    CHINA_PATH = _DATA_FALLBACK.parent / "survey_china.xlsx"

df = load_data(DATA_PATH, MOTOR_SHOW_PATH, CHINA_PATH)
print(f"Loaded {len(df)} rows: {df['data_source'].value_counts().to_dict()}")
"""

CLEAN = """\
df_clean, AGE_ORDER, INCOME_ORDER, DD_ORDER = clean_survey(df)
df_plot = df_clean.copy()
AGE_ORDER_PLOT = AGE_ORDER
INCOME_ORDER_PLOT = INCOME_ORDER
DD_ORDER_PLOT = DD_ORDER
print(f"Cleaned: {len(df_clean)} rows \\u00d7 {df_clean.shape[1]} columns.")
"""

# ── Phase 2: demographics — strip function defs, keep chart calls ─────────────
# Original cell 8 contains function defs + chart calls. Keep only chart calls.
_src8 = src(8)
# The chart calls start after the last function definition ends.
# All defs: thai_layout, barh_counts, count_bar, _hbar_trace
_s8 = strip_func_defs(_src8, {"thai_layout", "barh_counts", "count_bar", "_hbar_trace"})
# Remove FONT_FAMILY constant (imported from utils) and collapse excess blank lines
import re as _re
_s8 = _re.sub(r"^FONT_FAMILY\s*=.*\n", "", _s8, flags=_re.MULTILINE)
_s8 = _re.sub(r"\n{3,}", "\n\n", _s8)
DEMO_CHARTS = _s8.lstrip("\n")

# Cell 9: household/cars subplot — unchanged
HH_CARS = src(9)

# Cell 11: hh vehicle proxy — strip the function def, remove HH_PROXY_ORDER redefinition
_src11 = src(11)
_s11 = strip_func_defs(_src11, {"_hh_vehicle_proxy"})
# Remove HH_PROXY_ORDER block (it's imported from utils)
_lines11 = _s11.splitlines(keepends=True)
start_hh = next((i for i, l in enumerate(_lines11) if l.startswith("HH_PROXY_ORDER")), None)
if start_hh is not None:
    end_hh = start_hh
    while end_hh < len(_lines11) and (not _lines11[end_hh].startswith("]") or end_hh == start_hh):
        end_hh += 1
    end_hh += 1  # include the ']' line
    # skip one blank line after
    if end_hh < len(_lines11) and _lines11[end_hh].strip() == "":
        end_hh += 1
    _lines11 = _lines11[:start_hh] + _lines11[end_hh:]
HH_PROXY = "".join(_lines11).lstrip("\n").replace("_hh_vehicle_proxy", "hh_vehicle_proxy")

# Cells 12 + 13: daily driving
DAILY = src(12) + "\n" + src(13)

# Cell 17: powertrain considering
POWERTRAIN_CONS = src(17)

# Cell 18: strip heatmap_crosstab def + import lines; update calls
_src18 = src(18)
_s18 = strip_func_defs(_src18, {"heatmap_crosstab"})
_s18 = strip_import_lines(_s18, "from IPython.display import display", "from plotly.subplots import make_subplots")
_s18 = _s18.lstrip("\n")
_s18 = _s18.replace(
    'heatmap_crosstab(\n    "age_range",\n    "powertrain_choose_today",',
    'heatmap_crosstab(\n    df_plot, "age_range", "powertrain_choose_today",',
).replace(
    'heatmap_crosstab(\n    "monthly_income",\n    "powertrain_choose_today",',
    'heatmap_crosstab(\n    df_plot, "monthly_income", "powertrain_choose_today",',
)
PHASE3_HEATMAPS = _s18

# Cell 22: update heatmap_crosstab calls
_src22 = src(22)
PHASE3_MORE = _src22.replace(
    'heatmap_crosstab(\n    "age_range",\n    "purchase_factor_most_important",',
    'heatmap_crosstab(\n    df_plot, "age_range", "purchase_factor_most_important",',
)

# Cell 27: purchase factors — unchanged
PURCHASE_FACTORS = src(27)

# Cell 31: remove split_multiselect guard block
_src31 = src(31)
GUARD_START = 'if "split_multiselect" not in globals():\n'
gpos = _src31.find(GUARD_START)
if gpos != -1:
    # find end of the if-block (next non-indented, non-blank line)
    tail = _src31[gpos + len(GUARD_START):]
    end_rel = 0
    for line in tail.splitlines(keepends=True):
        if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
            break
        end_rel += len(line)
    _src31 = _src31[:gpos] + _src31[gpos + len(GUARD_START) + end_rel:]
SELF_EXPLICATED = _src31.lstrip("\n")

# Cells 32, 33, 37 — unchanged
BARRIERS = src(32)
BYD_REASONS = src(33)
INFO_SOURCES = src(37)

# Cell 40 (motor show): strip heatmap_crosstab_df def, rename to heatmap_crosstab
_src40 = src(40)
_s40 = strip_func_defs(_src40, {"heatmap_crosstab_df"})
_s40 = strip_import_lines(_s40, "from IPython.display import display")
_s40 = _s40.replace("heatmap_crosstab_df(", "heatmap_crosstab(")
MOTOR_SHOW = _s40.lstrip("\n")

# Cell 41 (motor show demo): strip grouped_count_bar def, update calls with df_plot
_src41 = src(41)
_s41 = strip_func_defs(_src41, {"grouped_count_bar"})
# Remove the comment line that preceded the def
_s41 = _s41.replace("# --- Side-by-side demographics by cohort ---\n", "")
_s41 = _s41.replace(
    'grouped_count_bar("age_range"', 'grouped_count_bar(df_plot, "age_range"'
).replace(
    'grouped_count_bar("gender"', 'grouped_count_bar(df_plot, "gender"'
).replace(
    'grouped_count_bar("location"', 'grouped_count_bar(df_plot, "location"'
).replace(
    'grouped_count_bar("monthly_income"', 'grouped_count_bar(df_plot, "monthly_income"'
).replace(
    'grouped_count_bar(\n    "likelihood_switch_ev_3y"',
    'grouped_count_bar(\n    df_plot, "likelihood_switch_ev_3y"'
)
MOTOR_SHOW_DEMO = _s41.lstrip("\n")

# Cell 43 (Phase 6): strip function defs + boilerplate that now live in utils
_src43 = src(43)
_s43 = strip_func_defs(
    _src43,
    {"short_powertrain_label", "split_multiselect", "explode_multiselect", "one_hot_multiselect"},
)
# Remove single-line imports and sns.set_theme already at the notebook top
_s43 = _re.sub(r"^import matplotlib\.pyplot as plt\n", "", _s43, flags=_re.MULTILINE)
_s43 = _re.sub(r"^import seaborn as sns\n", "", _s43, flags=_re.MULTILINE)
_s43 = _s43.replace('sns.set_theme(style="white", font_scale=1.05)\n', "")
# Remove try/except blocks for sklearn, scipy, kmodes
for _block in [
    "try:\n    import sklearn  # scikit-learn (used with K-Modes / workflows)\nexcept ImportError:\n    sklearn = None  # optional; install scikit-learn if needed for K-Modes / workflows\n",
    "try:\n    from scipy.stats import chi2_contingency\nexcept ImportError:\n    chi2_contingency = None\n",
    "try:\n    from kmodes.kmodes import KModes\nexcept ImportError:\n    KModes = None\n",
]:
    _s43 = _s43.replace(_block, "")
# strip POWERTRAIN_COLORS / PT_ORDER redefinitions (imported from utils)
pc_start = _s43.find("POWERTRAIN_COLORS = {")
pc_end   = _s43.find("}\nPT_ORDER")
if pc_start != -1 and pc_end != -1:
    pt_end = _s43.find("\n", pc_end + len("}\nPT_ORDER")) + 1
    _s43 = _s43[:pc_start] + _s43[pt_end:]
# collapse excess blank lines and strip edges
_s43 = _re.sub(r"\n{3,}", "\n\n", _s43)
PHASE6 = _s43.strip("\n")

# Cell 45 (Phase 7): remove redundant import + guard block
_src45 = src(45)
_s45 = strip_import_lines(_s45 := src(45), "from IPython.display import display", "import re  # daily")
GUARD_45 = '_missing = [\n'
g45 = _s45.find(GUARD_45)
if g45 != -1:
    tail45 = _s45[g45:]
    end45 = 0
    found_runtime = False
    for line in tail45.splitlines(keepends=True):
        end45 += len(line)
        if 'raise RuntimeError' in line and 'powertrain_short' in line:
            found_runtime = True
        if found_runtime and line.strip().endswith("'"):
            end45 += 1  # skip blank after closing quote
            break
    # skip one more blank
    if g45 + end45 < len(_s45) and _s45[g45 + end45:].startswith("\n"):
        end45 += 1
    _s45 = _s45[:g45] + _s45[g45 + end45:]
PHASE7 = _s45.lstrip("\n")

# Cell 47 (Phase 9b): remove guard, clean up import duplication
_src47 = src(47)
_s47 = strip_import_lines(
    _src47,
    "# --- Phase 9b: powertrain_considering",
    "import matplotlib.pyplot as plt",
    "import plotly.graph_objects as go",
)
GUARD_47 = 'if "short_powertrain_label" not in globals()'
g47 = _s47.find(GUARD_47)
if g47 != -1:
    end47 = _s47.find("\n\n", g47)
    if end47 != -1:
        _s47 = _s47[:g47] + _s47[end47 + 2:]
_s47 = "# --- Phase 9b: powertrain_considering × BYD in brands ---\n" + _s47.lstrip("\n")
PHASE9B = _s47

# Cell 49, 51, 54, 56 — unchanged
PHASE8 = src(49)
PHASE9 = src(51)
PHASE10 = src(54)
PHASE11 = src(56)

EXPORTS = """\
df_clean.to_csv('clean_survey_data.csv', index=False, encoding='utf-8-sig')
if 'mention_totals' in dir():
    mention_totals.to_csv('mention_totals.csv', encoding='utf-8-sig')
if 'reason_neg' in dir():
    reason_neg.value_counts().to_csv('reasonbyd_neg.csv', encoding='utf-8-sig')
print("Exports written.")
"""

# ── Assemble ───────────────────────────────────────────────────────────────────

new_cells = [
    md_cell(orig[0]),   # Title
    md_cell(orig[1]),   # Answer text note
    code(IMPORTS),
    md_cell(orig[3]),   # ## Phase 1
    code(DATA_LOAD),
    code(CLEAN),
    md_cell(orig[7]),   # ## Phase 2
    code(DEMO_CHARTS),
    code(HH_CARS),
    md_cell(orig[10]),  # ### Inferred vehicle sharing
    code(HH_PROXY),
    code(DAILY),
    md_cell(orig[15]),  # Persona summary
    md_cell(orig[16]),  # ## Phase 3
    code(POWERTRAIN_CONS),
    code(PHASE3_HEATMAPS),
    md_cell(orig[21]),  # ### Age group × single purchase factor
    code(PHASE3_MORE),
    md_cell(orig[23]),  # ### Interpretation
    md_cell(orig[26]),  # ## Phase 4
    code(PURCHASE_FACTORS),
    md_cell(orig[30]),  # ## Phase 4b
    code(SELF_EXPLICATED),
    code(BARRIERS),
    code(BYD_REASONS),
    code(INFO_SOURCES),
    md_cell(orig[38]),  # Key takeaways
    md_cell(orig[39]),  # ## Phase 5
    code(MOTOR_SHOW),
    code(MOTOR_SHOW_DEMO),
    md_cell(orig[42]),  # ## Phase 6
    code(PHASE6),
    md_cell(orig[44]),  # ## Phase 7
    code(PHASE7),
    md_cell(orig[46]),  # Powertrain × BYD
    code(PHASE9B),
    md_cell(orig[48]),  # ## Phase 8
    code(PHASE8),
    md_cell(orig[50]),  # ## Phase 9
    code(PHASE9),
    md_cell(orig[52]),  # ## Phase 10
    code(PHASE10),
    md_cell(orig[55]),  # ## Phase 11
    code(PHASE11),
    md_cell(orig[57]),  # Powertrain awareness report
    md_cell(orig[58]),  # Executive Summary
    code(EXPORTS),
]

nb_new = {
    "cells": new_cells,
    "metadata": nb["metadata"],
    "nbformat": nb["nbformat"],
    "nbformat_minor": nb.get("nbformat_minor", 5),
}

with open("survey_analysis_refactored.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb_new, f, ensure_ascii=False, indent=1)

print(f"Done: {len(new_cells)} cells (was {len(orig)}).")
