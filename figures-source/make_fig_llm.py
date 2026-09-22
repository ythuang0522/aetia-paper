#!/usr/bin/env python3
"""Figure 4: AETIA against four frontier language models prompted directly on identical raw data.

a, precision-recall plane with iso-F1 curves (41 patients); b, precision, recall and F1 per system;
c, F1 difference of each model from AETIA. Reads figures-source/metrics.csv (direct_raw_41).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, AXIS, GRID, INK, INK2, MUTED, read_csv  # noqa: E402
from charts import FS, grouped_bars, marker, pr_plane  # noqa: E402

OUT = HERE.parent / "figures" / "fig3_llm_comparison.svg"
W, H = 1000, 420
BLUE = "#1d4ed8"; GREY = "#6b7280"
P_COL, R_COL, F_COL = "#2a78d6", "#eb6834", "#1baf7a"
ORDER = ["AETIA", "GPT-5.6 Sol", "GPT-5.6 Luna", "GPT-5.6 Terra", "GPT-6 Astra"]
SHAPES = {"AETIA": "circle", "GPT-5.6 Sol": "square", "GPT-5.6 Luna": "triangle", "GPT-5.6 Terra": "diamond", "GPT-6 Astra": "circle"}


def main() -> None:
    rows = {r["method"]: r for r in read_csv(HERE / "metrics.csv") if r["experiment"] == "direct_raw_41"}
    n = rows["AETIA"]["n_patients"]
    svg = SVG(W, H)
    # a
    svg.text(14, 30, "a", size=22, weight="bold")
    pts = []
    for m in ORDER:
        r = rows[m]
        pts.append(dict(label="AETIA" if m == "AETIA" else "", recall=float(r["recall"]), precision=float(r["precision"]),
                        shape=SHAPES[m], color=BLUE if m == "AETIA" else GREY, dx=-12, dy=-12, anchor="end", bold=True, r=8 if m == "AETIA" else 6.5))
    pr_plane(svg, 70, 50, 300, 270, pts)
    # in-panel legend for the clustered direct-prompting models (marker shapes carry identity)
    lx, ly = 90, 240
    svg.text(lx, ly, "Direct prompting", size=FS - 2, fill=INK2, weight="bold")
    for j, m in enumerate(ORDER[1:]):
        yy = ly + 16 + j * 15
        marker(svg, lx + 6, yy - 4, SHAPES[m], GREY, r=4.5)
        svg.text(lx + 18, yy, m, size=FS - 3, fill=INK2)
    svg.text(70 + 150, 50 + 270 + 52, f"Patients, n = {n}; identical de-identified inputs", size=FS - 2, fill=MUTED, anchor="middle")
    # b
    svg.text(440, 30, "b", size=22, weight="bold")
    groups = [(m if m != "AETIA" else "AETIA", rows[m]) for m in ORDER]
    grouped_bars(svg, 500, 50, 480, 270, groups, [("Precision", "precision", P_COL), ("Recall", "recall", R_COL), ("F1", "f1", F_COL)],
                 bar_w=20, sub_labels=[None, "direct prompting", "direct prompting", "direct prompting", "direct prompting"])
    svg.legend(506, 36, [("Precision", P_COL), ("Recall", R_COL), ("F1", F_COL)], size=FS - 1, swatch=13, gap=24)
    svg.save(OUT)


if __name__ == "__main__":
    main()
