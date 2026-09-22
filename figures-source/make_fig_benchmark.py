#!/usr/bin/env python3
"""Figure 3: AETIA against conventional read-outs.

a, precision-recall plane with iso-F1 curves (55 patients); b, precision, recall and F1 per method;
c, fraction of patients with >= 1 reported organism and d, organisms per patient (ICU series, n = 35).
Reads figures-source/metrics.csv (r5_55) and burden.csv. Canvas 1000 units = 180 mm.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, INK, INK2, MUTED, read_csv  # noqa: E402
from charts import FS, grouped_bars, pr_plane, single_bars  # noqa: E402

OUT = HERE.parent / "figures" / "fig2_benchmark.svg"
W, H = 1000, 745
BLUE = "#1d4ed8"; GREY = "#6b7280"
P_COL, R_COL, F_COL = "#2a78d6", "#eb6834", "#1baf7a"
SHAPES = {"AETIA": "circle", "mNGS report": "triangle", "FilmArray/GM": "square", "Culture": "diamond"}
LABELS = {"AETIA": "AETIA", "mNGS report": "mNGS report", "FilmArray/GM": "FilmArray / GM", "Culture": "Culture"}
ORDER = ["AETIA", "mNGS report", "FilmArray/GM", "Culture"]


def main() -> None:
    rows = {r["method"]: r for r in read_csv(HERE / "metrics.csv") if r["experiment"] == "r5_55"}
    burden = read_csv(HERE / "burden.csv")
    n55 = rows["AETIA"]["n_patients"]; n35 = burden[0]["n_patients"]
    svg = SVG(W, H)

    # a: PR plane
    svg.text(14, 30, "a", size=22, weight="bold")
    pts = []
    offs = {"AETIA": (-12, -12, "end"), "mNGS report": (-12, -12, "end"), "FilmArray/GM": (12, 4, "start"), "Culture": (12, 4, "start")}
    for m in ORDER:
        r = rows[m]
        dx, dy, anc = offs[m]
        pts.append(dict(label=LABELS[m], recall=float(r["recall"]), precision=float(r["precision"]),
                        shape=SHAPES[m], color=BLUE if m == "AETIA" else GREY, dx=dx, dy=dy, anchor=anc, bold=(m == "AETIA"), r=8 if m == "AETIA" else 7))
    pr_plane(svg, 70, 50, 340, 300, pts)
    svg.text(70 + 170, 50 + 300 + 52, f"Patients, n = {n55}; (patient, organism) pairs; dashed, iso-F1", size=FS - 2, fill=MUTED, anchor="middle")

    # b: grouped bars
    svg.text(490, 30, "b", size=22, weight="bold")
    groups = [(LABELS[m], rows[m]) for m in ORDER]
    grouped_bars(svg, 560, 50, 420, 300, groups, [("Precision", "precision", P_COL), ("Recall", "recall", R_COL), ("F1", "f1", F_COL)])
    svg.legend(566, 36, [("Precision", P_COL), ("Recall", R_COL), ("F1", F_COL)], size=FS - 1, swatch=13, gap=24)

    # c, d: burden (single series, AETIA highlighted)
    names = {"Culture": "Culture", "FilmArray": "FilmArray", "mNGS report": "mNGS", "AETIA": "AETIA"}
    items_pos = [(names[r["method"]], float(r["positive_rate"])) for r in burden]
    items_n = [(names[r["method"]], float(r["mean_species"])) for r in burden]
    svg.text(14, 440, "c", size=22, weight="bold")
    single_bars(svg, 70, 460, 300, 190, items_pos, 100, (0, 25, 50, 75, 100), "Patients with ≥ 1 organism (%)", hi_color=BLUE)
    svg.text(490, 440, "d", size=22, weight="bold")
    single_bars(svg, 560, 460, 300, 190, items_n, 7, (0, 2, 4, 6), "Organisms per patient (mean)", value_fmt="{:.2f}", hi_color=BLUE)
    svg.text(70 + 150, 728, f"ICU patients, n = {n35}", size=FS - 2, fill=MUTED, anchor="middle")
    svg.text(560 + 150, 728, f"ICU patients, n = {n35}", size=FS - 2, fill=MUTED, anchor="middle")
    svg.save(OUT)


if __name__ == "__main__":
    main()
