#!/usr/bin/env python3
"""Figure 2: performance benchmark and direct-prompting comparison.

a, primary-cohort precision-recall plane (55 patients); b, precision, recall and F1
for the primary assay benchmark; c, direct-prompting precision-recall plane (41
patients); d, precision, recall and F1 for AETIA and the directly prompted models.
All plotted values are read from figures-source/metrics.csv. Canvas 1000 units =
180 mm.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, INK2, MUTED, read_csv  # noqa: E402
from charts import FS, grouped_bars, marker, pr_plane  # noqa: E402

OUT = HERE.parent / "figures" / "fig2_benchmark.svg"
W, H = 1000, 760
BLUE = "#1d4ed8"; GREY = "#6b7280"
P_COL, R_COL, F_COL = "#2a78d6", "#eb6834", "#1baf7a"
PRIMARY_ORDER = ["AETIA", "mNGS report", "FilmArray/GM", "Culture"]
PRIMARY_SHAPES = {"AETIA": "circle", "mNGS report": "triangle", "FilmArray/GM": "square", "Culture": "diamond"}
PRIMARY_LABELS = {"AETIA": "AETIA", "mNGS report": "mNGS report", "FilmArray/GM": "FilmArray / GM", "Culture": "Culture"}
DIRECT_ORDER = ["AETIA", "GPT-5.6 Sol", "GPT-5.6 Luna", "GPT-5.6 Terra", "GPT-6 Astra"]
DIRECT_SHAPES = {"AETIA": "circle", "GPT-5.6 Sol": "square", "GPT-5.6 Luna": "triangle", "GPT-5.6 Terra": "diamond", "GPT-6 Astra": "circle"}


def points_for(rows, order, shapes, labels=True):
    """Build chart points while keeping AETIA visually emphasized."""
    points = []
    for method in order:
        row = rows[method]
        is_aetia = method == "AETIA"
        # Keep the primary-method labels on the assay panel. Direct-prompting
        # methods are identified by the in-panel marker legend to avoid a
        # cluster of overlapping labels around recall 55-61%.
        label = (labels and PRIMARY_LABELS.get(method, method)) or ("AETIA" if is_aetia else "")
        points.append(
            dict(
                label=label,
                recall=float(row["recall"]),
                precision=float(row["precision"]),
                shape=shapes[method],
                color=BLUE if is_aetia else GREY,
                dx=-12,
                dy=-12,
                anchor="end",
                bold=is_aetia,
                r=8 if is_aetia else (7 if labels else 6.5),
            )
        )
    return points


def direct_legend(svg, x, y):
    """Legend for the four direct-prompting systems in panel c."""
    svg.text(x, y, "Direct prompting", size=FS - 2, fill=INK2, weight="bold")
    for j, method in enumerate(DIRECT_ORDER[1:]):
        yy = y + 16 + j * 15
        marker(svg, x + 6, yy - 4, DIRECT_SHAPES[method], GREY, r=4.5)
        svg.text(x + 18, yy, method, size=FS - 3, fill=INK2)


def main() -> None:
    metrics = read_csv(HERE / "metrics.csv")
    primary = {r["method"]: r for r in metrics if r["experiment"] == "r5_55"}
    direct = {r["method"]: r for r in metrics if r["experiment"] == "direct_raw_41"}
    n55 = primary["AETIA"]["n_patients"]
    n41 = direct["AETIA"]["n_patients"]
    svg = SVG(W, H)

    # a: primary-cohort PR plane
    svg.text(14, 30, "a", size=22, weight="bold")
    pr_plane(svg, 70, 52, 390, 230, points_for(primary, PRIMARY_ORDER, PRIMARY_SHAPES))
    svg.text(265, 343, f"Primary cohort, n = {n55}; dashed curves, iso-F1", size=FS - 2, fill=MUTED, anchor="middle")

    # b: primary-cohort grouped bars
    svg.text(500, 30, "b", size=22, weight="bold")
    primary_groups = [(PRIMARY_LABELS[method], primary[method]) for method in PRIMARY_ORDER]
    grouped_bars(
        svg,
        540,
        52,
        430,
        230,
        primary_groups,
        [("Precision", "precision", P_COL), ("Recall", "recall", R_COL), ("F1", "f1", F_COL)],
    )
    svg.legend(548, 38, [("Precision", P_COL), ("Recall", R_COL), ("F1", F_COL)], size=FS - 1, swatch=13, gap=24)

    # c: direct-prompting PR plane
    svg.text(14, 386, "c", size=22, weight="bold")
    pr_plane(svg, 70, 408, 390, 230, points_for(direct, DIRECT_ORDER, DIRECT_SHAPES, labels=False))
    direct_legend(svg, 96, 508)
    svg.text(265, 699, f"Direct prompting, n = {n41}; identical inputs; dashed curves, iso-F1", size=FS - 2, fill=MUTED, anchor="middle")

    # d: direct-prompting grouped bars
    svg.text(500, 386, "d", size=22, weight="bold")
    direct_groups = [(method, direct[method]) for method in DIRECT_ORDER]
    grouped_bars(
        svg,
        540,
        408,
        430,
        230,
        direct_groups,
        [("Precision", "precision", P_COL), ("Recall", "recall", R_COL), ("F1", "f1", F_COL)],
        bar_w=17,
        gap=2,
        sub_labels=[None, "direct prompting", "direct prompting", "direct prompting", "direct prompting"],
    )
    svg.legend(548, 394, [("Precision", P_COL), ("Recall", R_COL), ("F1", F_COL)], size=FS - 1, swatch=13, gap=24)
    svg.text(755, 744, f"Direct prompting, n = {n41}", size=FS - 2, fill=MUTED, anchor="middle")
    svg.save(OUT)


if __name__ == "__main__":
    main()
