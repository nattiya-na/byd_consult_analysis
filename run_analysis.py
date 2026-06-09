"""Main entry point — runs all survey analysis phases end to end.

Usage:
    python run_analysis.py                    # save all charts to output/
    python run_analysis.py --phases 2,3,4     # run specific phases only
    python run_analysis.py --skip 10          # skip phase 10 (k-modes clustering)
    python run_analysis.py --no-export        # skip CSV export
    python run_analysis.py --no-charts        # text output only, no files written
"""
import argparse
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before other matplotlib imports

from pathlib import Path

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns

from survey_utils import load_data, clean_survey
from phase2_customer_profile import run_phase2
from phase3_powertrain_prefs import run_phase3
from phase4_purchase_factors import run_phase4, run_phase4b, run_phase4c
from phase5_motor_show import run_phase5
from phase6_feature_engineering import run_phase6
from phase8_barriers_motivation import run_phase8
from phase9_brand_positioning import run_phase9, run_phase9b
from phase10_clustering import run_phase10
from phase11_awareness import run_phase11

_CSV_NAME = (
    "แบบสอบถามความสนใจในการซื้อรถยนต์ไฟฟ้าทั่วไป (Responses) - Form Responses 1.csv"
)
_DIR = Path(__file__).parent
DATA_PATH = _DIR / _CSV_NAME
MOTOR_SHOW_PATH = _DIR / "motor_show.csv"
CHINA_PATH = _DIR / "survey_china.xlsx"
OUTPUT_DIR = _DIR / "output"


class _ChartSaver:
    """Intercept every fig.show() / plt.show() call and write to output/.

    Plotly figures  → phase{N}_{counter:02d}.html
    Matplotlib figs → phase{N}_{counter:02d}.png
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self._phase = 0
        self._phase_counter = 0
        self.saved: list[Path] = []
        self._orig_fig_show = None
        self._orig_plt_show = None

    def set_phase(self, n: int):
        self._phase = n
        self._phase_counter = 0

    def _next(self, ext: str) -> Path:
        self._phase_counter += 1
        return self.output_dir / f"phase{self._phase:02d}_{self._phase_counter:02d}.{ext}"

    def install(self):
        saver = self
        self._orig_fig_show = go.Figure.show
        self._orig_plt_show = plt.show

        def _plotly_save(fig_self, *_a, **_kw):
            path = saver._next("html")
            fig_self.write_html(str(path))
            saver.saved.append(path)
            print(f"  → {path.name}")

        def _mpl_save(*_a, **_kw):
            path = saver._next("png")
            plt.savefig(str(path), bbox_inches="tight", dpi=150)
            plt.close()
            saver.saved.append(path)
            print(f"  → {path.name}")

        go.Figure.show = _plotly_save
        plt.show = _mpl_save

    def uninstall(self):
        if self._orig_fig_show is not None:
            go.Figure.show = self._orig_fig_show
        if self._orig_plt_show is not None:
            plt.show = self._orig_plt_show


def _parse_args():
    parser = argparse.ArgumentParser(description="BYD EV survey analysis")
    parser.add_argument(
        "--phases",
        default=None,
        help="Comma-separated list of phases to run (e.g. 2,3,4). Runs all by default.",
    )
    parser.add_argument(
        "--skip",
        default=None,
        help="Comma-separated list of phases to skip (e.g. 10).",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip CSV export at the end.",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Suppress all chart rendering (text output only, no files written).",
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    wanted = set(range(2, 12)) - {7}  # phase 7 is empty in the notebook
    if args.phases:
        wanted = {int(p.strip()) for p in args.phases.split(",")}
    if args.skip:
        wanted -= {int(p.strip()) for p in args.skip.split(",")}

    try:
        sns.set_theme(style="white", font_scale=1.05)
    except AttributeError:
        sns.set_style("white")

    saver = _ChartSaver(OUTPUT_DIR)
    if not args.no_charts:
        saver.install()
        print(f"Charts will be saved to: {OUTPUT_DIR}/")

    try:
        print("\n=== Phase 1: Loading and cleaning data ===")
        df = load_data(DATA_PATH, MOTOR_SHOW_PATH, CHINA_PATH)
        print(f"Loaded {len(df)} rows: {df['data_source'].value_counts().to_dict()}")

        df_clean, AGE_ORDER, INCOME_ORDER, DD_ORDER = clean_survey(df)
        df_plot = df_clean.copy()
        print(f"Cleaned: {len(df_clean)} rows × {df_clean.shape[1]} columns.")

        def run(phase_num, fn, *a, **kw):
            if phase_num not in wanted:
                return
            saver.set_phase(phase_num)
            print(f"\n{'=' * 60}\n=== Phase {phase_num} ===\n{'=' * 60}")
            fn(*a, **kw)

        run(2, run_phase2, df_plot, AGE_ORDER, INCOME_ORDER, DD_ORDER)
        run(3, run_phase3, df_plot, AGE_ORDER, INCOME_ORDER)
        run(4, run_phase4, df_plot)
        run(4, run_phase4b, df_plot)
        run(4, run_phase4c, df_plot, AGE_ORDER)
        run(5, run_phase5, df_plot, AGE_ORDER, INCOME_ORDER)

        if 6 in wanted:
            saver.set_phase(6)
            print(f"\n{'=' * 60}\n=== Phase 6 ===\n{'=' * 60}")
            df_plot = run_phase6(df_plot)

        run(8, run_phase8, df_plot, AGE_ORDER, INCOME_ORDER)
        run(9, run_phase9, df_plot, AGE_ORDER)
        run(9, run_phase9b, df_plot)
        run(10, run_phase10, df_plot)
        run(11, run_phase11, df_plot, AGE_ORDER)

    finally:
        saver.uninstall()

    if not args.no_export:
        print("\n=== Exporting results ===")
        df_clean.to_csv("clean_survey_data.csv", index=False, encoding="utf-8-sig")
        print("Exported clean_survey_data.csv")

    if saver.saved:
        print(f"\n{len(saver.saved)} chart(s) saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
