#!/usr/bin/env python3
"""Extended Data Figure 3: the course after the report (figures/ed3_trajectory.svg).

a, one row per admission: the fever state of each window after the mNGS specimen, and how long the
   admission ran. The temperature block empties from left to right in both outcome groups.
b, the same data as proportions, survivors against decedents, with n at every point.
c, counted per decedent rather than per window: did the marker improve by day 3-7, and did it hold?

Every number is read from figures-source/trajectory_summary.json (written by tables/make_trajectory.py
from sources that stay outside this repository); none is typed here. Canvas 1000 units = 180 mm.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, INK, INK2, MUTED, GRID, AXIS, BLUE  # noqa: E402

OUT = HERE.parent / "figures" / "ed3_trajectory.svg"
SRC = HERE / "trajectory_summary.json"
W, H = 1000, 566
FS = 13

SURV, DIED = "#2a78d6", "#eb6834"
FEVER_C = {"fever": "#c9401f", "raised": "#f0a488", "normal": "#dfe6ef", "na": "#ffffff"}
FEVER_N = [("fever", "≥ 38 °C"), ("raised", "37–38 °C"), ("normal", "< 37 °C"), ("na", "not recorded")]
HELD, REVERSED, NEVER = "#1baf7a", "#eda100", "#c9c7bf"
WINDOWS = [("pre", "−14 to −1"), ("d0-2", "0–2"), ("d3-7", "3–7"), ("d8-14", "8–14"), ("d15-30", "15–30")]
ROW_H, ROW_GAP, CELL_W = 7.4, 1.6, 34


def panel_a(svg, d, x0, y0):
    rows = d["patient_rows"]
    grid_w = len(WINDOWS) * CELL_W
    bar_x = x0 + grid_w + 26
    bar_w = 170
    longest = max(r["days_to_end"] or 0 for r in rows) or 1

    for i, (_k, lab) in enumerate(WINDOWS):
        svg.text(x0 + i * CELL_W + CELL_W / 2, y0 - 8, lab, size=FS - 3, fill=MUTED, anchor="middle")
    svg.text(x0 + grid_w / 2, y0 - 24, "Days relative to the mNGS specimen", size=FS - 2, fill=INK2, anchor="middle")
    svg.text(bar_x, y0 - 24, "Days of admission after the specimen", size=FS - 2, fill=INK2)
    for t in (0, 30, 60):
        svg.text(bar_x + t / longest * bar_w, y0 - 8, str(t), size=FS - 3, fill=MUTED, anchor="middle")

    y = y0
    for group, color, label in (("died", DIED, "died in hospital"), ("survived", SURV, "survived to discharge")):
        block = [r for r in rows if r["outcome"] == group]
        top = y
        for r in block:
            for i, state in enumerate(r["windows"]):
                svg.rect(x0 + i * CELL_W + 0.6, y, CELL_W - 1.2, ROW_H, FEVER_C[state],
                         stroke="#d9d8d2" if state == "na" else "none", sw=0.5, rx=1)
            if r["days_to_end"] is not None:
                svg.rect(bar_x, y + 1.4, max(r["days_to_end"] / longest * bar_w, 1.2), ROW_H - 2.8, color, rx=1)
            y += ROW_H + ROW_GAP
        svg.line(x0 - 10, top, x0 - 10, y - ROW_GAP, stroke=color, sw=2.6, cap="round")
        svg.text(x0 - 16, (top + y - ROW_GAP) / 2 - 4, label.split()[0], size=FS - 2, fill=color,
                 anchor="end", weight="bold")
        svg.text(x0 - 16, (top + y - ROW_GAP) / 2 + 9, "n = %d" % len(block), size=FS - 3, fill=MUTED, anchor="end")
        y += 12
    lx = x0
    for k, n in FEVER_N:
        svg.rect(lx, y + 3, 9, 9, FEVER_C[k], stroke="#c3c2b7", sw=0.7, rx=2)
        svg.text(lx + 13, y + 11, n, size=FS - 3, fill=INK2)
        lx += 13 + len(n) * (FS - 3) * 0.55 + 16
    return y + 8


def panel_b(svg, d, x0, y0, w, h):
    f = d["fever"]
    pts = {g: [(i, f[g]["by_window"][k]["pct"], f[g]["by_window"][k]["n"])
               for i, (k, _l) in enumerate(WINDOWS) if k in f[g]["by_window"]]
           for g in ("survived", "died")}
    hi = max(v for p in pts.values() for _i, v, _n in p) * 1.18
    y_of = lambda v: y0 + h - v / hi * h                            # noqa: E731
    x_of = lambda i: x0 + 18 + i * (w - 36) / (len(WINDOWS) - 1)    # noqa: E731
    for v in (0, 20, 40):
        svg.line(x0, y_of(v), x0 + w, y_of(v), stroke=GRID, sw=1.0)
        svg.text(x0 - 6, y_of(v) + 4, str(v), size=FS - 3, fill=MUTED, anchor="end")
    svg.text(x0 - 6, y0 - 10, "Patients with a maximum ≥ 38 °C (%)", size=FS - 2, fill=INK2, weight="bold")
    for i, (_k, lab) in enumerate(WINDOWS):
        svg.text(x_of(i), y0 + h + 15, lab, size=FS - 3, fill=MUTED, anchor="middle")
    for row, (group, color) in enumerate((("survived", SURV), ("died", DIED))):
        p = pts[group]
        svg.path("M " + " L ".join(f"{x_of(i):.1f} {y_of(v):.1f}" for i, v, _n in p), stroke=color, sw=2.4)
        for i, v, n in p:
            svg.circle(x_of(i), y_of(v), 4.0, color, stroke="#ffffff", sw=1.2)
            svg.text(x_of(i), y0 + h + 30 + row * 13, str(n), size=FS - 3, fill=color, anchor="middle")
    svg.text(x0 - 6, y0 + h + 30, "n", size=FS - 3, fill=SURV, anchor="end")
    svg.text(x0 - 6, y0 + h + 43, "n", size=FS - 3, fill=DIED, anchor="end")


def panel_c(svg, d, x0, y0, w):
    svg.text(x0, y0 - 27, "Among the patients who died", size=FS - 2, fill=INK, weight="bold")
    svg.text(x0, y0 - 12, "did the marker improve by day 3–7, and did the improvement hold?",
             size=FS - 2, fill=MUTED)
    y = y0 + 4
    for label, marker in (("Temperature", "temperature"), ("Arterial pO₂", "pO2"), ("Platelets", "platelets")):
        r = d["markers"][marker]["response"]
        total = r["decedents_assessable"]
        segs = [(r["improved"] - r["improved_then_worsened"], HELD),
                (r["improved_then_worsened"], REVERSED), (r["worsened"], NEVER)]
        svg.text(x0, y + 13, label, size=FS - 2, fill=INK)
        svg.text(x0, y + 27, "n = %d" % total, size=FS - 3, fill=MUTED)
        bx, bw = x0 + 96, w - 96
        for n, color in segs:
            seg = n / total * bw
            if seg <= 0:
                continue
            svg.rect(bx, y, seg, 24, color, stroke="#ffffff", sw=1.0)
            if seg >= 24:
                svg.text(bx + seg / 2, y + 17, str(n), size=FS - 3,
                         fill=INK if color == NEVER else "#ffffff", anchor="middle", weight="bold")
            bx += seg
        y += 38
    svg.legend(x0 + 96, y + 6, [("improved, held", HELD), ("improved, then reversed", REVERSED)],
               size=FS - 3, swatch=9, gap=16)
    svg.legend(x0 + 96, y + 24, [("never improved", NEVER)], size=FS - 3, swatch=9, gap=16)


def main() -> None:
    d = json.loads(SRC.read_text())
    svg = SVG(W, H)
    svg.text(16, 30, "a", size=22, weight="bold")
    panel_a(svg, d, 150, 66)
    svg.text(560, 30, "b", size=22, weight="bold")
    panel_b(svg, d, 646, 82, 318, 132)
    svg.text(560, 320, "c", size=22, weight="bold")
    panel_c(svg, d, 606, 382, 360)
    svg.save(OUT)


if __name__ == "__main__":
    main()
