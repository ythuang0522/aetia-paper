#!/usr/bin/env python3
"""Extended Data Figure 2: what the registry's 105 mNGS reports contain (figures/ed2_registry.svg).

a, organisms per report.  Each row is a dumbbell between the two levels of one contrast.  The gap
   between patient strata closes once the specimen compartment is held fixed (grey, all specimens;
   blue, bronchoalveolar lavage alone), whereas the gap between compartments is the contrast itself.
b, agreement between the mNGS report and culture, from the registry's own organism-by-organism
   comparison, with the two corroboration rates underneath.

Every number is read from figures-source/impact_summary.json (written by tables/make_impact.py from
the registry workbook, which stays outside this repository); none is typed here.
Canvas 1000 units = 180 mm.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, INK, INK2, MUTED, GRID, AXIS, BLUE  # noqa: E402

OUT = HERE.parent / "figures" / "ed2_registry.svg"
SRC = HERE / "impact_summary.json"
W, H = 1000, 392
FS = 13
GREY_D = "#6b7280"      # the reading over all specimens
ORANGE = "#eb6834"      # the compartment contrast

STRATA = [                                     # label, low key, low name, high key, high name
    ("Ward", "ward:general ward", "general ward", "ward:ICU", "intensive care"),
    ("Corticosteroids", "steroid:no", "no", "steroid:yes", "yes"),
    ("ARDS", "ards:no", "no", "ards:yes", "yes"),
    ("Pneumonia", "pneumonia:CAP", "community", "pneumonia:HAP/VAP", "hospital/ventilator"),
]
# the workbook does not define "partial match" or "mismatch", so its category names are used unchanged
CLASSES = [("bacterium", "#4a6fa5"), ("virus", "#8a5fbf"), ("fungus", "#eda100"), ("mycobacterium", "#b9b7ae")]
CLASS_NAMES = ["bacteria", "viruses", "fungi", "mycobacteria"]
CONCORD = [("NGS+ Cx-", "mNGS only", BLUE), ("Partial match", "partial match", "#7fb0e8"),
           ("Mismatch", "mismatch", ORANGE), ("Matched", "exact match", "#1baf7a"),
           ("NGS- Cx +", "culture only", "#b9b7ae"), ("NGS- Cx-", "neither", "#e1e0d9")]


def dumbbell(svg, x_of, y, lo, hi, color, value_labels=True):
    xlo, xhi = x_of(lo), x_of(hi)
    if abs(xhi - xlo) < 1.5:                   # the two levels coincide: one dot, one value
        svg.circle(xlo, y, 5.0, color)
        if value_labels:
            svg.text(xlo + 11, y + 4, f"{lo:g}", size=FS - 2, fill=color, weight="bold")
        return
    svg.line(min(xlo, xhi), y, max(xlo, xhi), y, stroke=color, sw=3.0, cap="round")
    svg.circle(xlo, y, 5.0, "#ffffff", stroke=color, sw=2.0)
    svg.circle(xhi, y, 5.0, color)
    if value_labels:
        svg.text(xlo - 9, y + 4, f"{lo:g}", size=FS - 3, fill=MUTED, anchor="end")
        svg.text(xhi + 9, y + 4, f"{hi:g}", size=FS - 2, fill=color, weight="bold")


def panel_a(svg, d, gx, x0, y0, w, h):
    allsp, balf = d["burden_strata_all_specimens"], d["burden_strata_BALF_only"]
    xmax = 8.0
    x_of = lambda v: x0 + (v / xmax) * w        # noqa: E731
    for t in range(0, int(xmax) + 1, 2):
        svg.line(x_of(t), y0 - 8, x_of(t), y0 + h, stroke=GRID, sw=1.0)
        svg.text(x_of(t), y0 + h + 17, str(t), size=FS - 2, fill=MUTED, anchor="middle")
    svg.line(x0, y0 + h, x_of(xmax), y0 + h, stroke=AXIS, sw=1.0)
    svg.text(x0 + w / 2, y0 + h + 35, "Organisms per mNGS report (median)", size=FS - 1,
             fill=INK2, anchor="middle")

    y = y0 + 16
    air, ster = d["burden_airway"], d["burden_sterile"]
    svg.text(gx, y - 2, "Specimen compartment", size=FS - 1, fill=INK, anchor="end", weight="bold")
    svg.text(gx, y + 13, f"sterile site (n={ster['n']}) → airway (n={air['n']})",
             size=FS - 3, fill=MUTED, anchor="end")
    dumbbell(svg, x_of, y, ster["median"], air["median"], ORANGE)

    y += 46
    svg.line(gx - 218, y - 10, x_of(xmax), y - 10, stroke=GRID, sw=1.0)
    y += 10
    for label, klo, lo_name, khi, hi_name in STRATA:
        a_lo, a_hi = allsp[klo], allsp[khi]
        b_lo, b_hi = balf.get(klo), balf.get(khi)
        svg.text(gx, y - 1, label, size=FS - 1, fill=INK, anchor="end")
        svg.text(gx, y + 14, f"{lo_name} (n={a_lo['n']}) → {hi_name} (n={a_hi['n']})",
                 size=FS - 3, fill=MUTED, anchor="end")
        dumbbell(svg, x_of, y, a_lo["median"], a_hi["median"], GREY_D)
        if b_lo and b_hi:
            dumbbell(svg, x_of, y + 16, b_lo["median"], b_hi["median"], BLUE)
        y += 52

    svg.legend(gx - 218, y0 + h + 58, [("compartment, all 105 specimens", ORANGE),
                                       ("patient stratum, all specimens", GREY_D)],
               size=FS - 2, swatch=9, gap=16)
    svg.legend(gx - 218, y0 + h + 76, [("patient stratum, lavage fluid only", BLUE)],
               size=FS - 2, swatch=9, gap=16)


def panel_b(svg, d, x0, y0, w):
    c = d["workbook_concordance"]
    svg.text(x0, y0 - 12, f"mNGS report against culture, organism by organism (n = {c['comparisons']})",
             size=FS - 1, fill=INK2)
    bar_h = 34
    x = x0
    for key, _name, color in CONCORD:
        seg = c[key]["pct"] / 100.0 * w
        svg.rect(x, y0, seg, bar_h, color, stroke="#ffffff", sw=1.0)
        x += seg
    # every category named in a two-column key, so no leader lines are needed
    ky = y0 + bar_h + 22
    for i, (key, name, color) in enumerate(CONCORD):
        cx = x0 + (i % 2) * (w / 2)
        cy = ky + (i // 2) * 17
        svg.rect(cx, cy - 8, 9, 9, color, rx=2, stroke="#d8d7d1", sw=0.6)
        svg.text(cx + 14, cy, f"{name} {c[key]['pct']:g}%", size=FS - 2, fill=INK2, baseline="middle")

    co = d["concordance"]
    y = ky + 3 * 17 + 26
    for name, num, den, pct, color in [
            ("mNGS organisms with a same-species culture", co["culture_confirmed"],
             co["mngs_organisms"], co["culture_confirmed_pct"], BLUE),
            ("cultured organisms absent from the mNGS report", co["culture_absent_from_report"],
             co["culture_organisms"], co["culture_absent_pct"], ORANGE)]:
        svg.text(x0, y - 8, f"{name} ({num}/{den})", size=FS - 2, fill=INK2)
        svg.rect(x0, y, w, 13, "#f1f0ec", rx=2)
        svg.rect(x0, y, w * pct / 100.0, 13, color, rx=2)
        svg.text(x0 + w * pct / 100.0 + 8, y + 11, f"{pct:g}%", size=FS - 2, fill=INK, weight="bold")
        y += 46

    cc = d["class_composition"]
    svg.text(x0, y - 8, "Organism class, reported against adjudicated causative", size=FS - 1, fill=INK2)
    y += 4
    for scope, key, total in (("reported", "reported", cc["reported_total"]),
                              ("adjudicated", "adjudicated", cc["adjudicated_total"])):
        svg.text(x0, y + 12, f"{scope} ({total})", size=FS - 2, fill=MUTED)
        bx = x0 + 96
        bw = w - 96
        for cls, color in CLASSES:
            entry = cc[key].get(cls)
            if not entry:
                continue
            seg = entry["pct"] / 100.0 * bw
            svg.rect(bx, y, seg, 15, color, stroke="#ffffff", sw=1.0)
            if seg >= 46:
                svg.text(bx + seg / 2, y + 11, f"{entry['pct']:g}%", size=FS - 2,
                         fill="#ffffff" if cls in ("bacterium", "virus") else INK, anchor="middle")
            bx += seg
        y += 24
    svg.legend(x0 + 96, y + 10, [(n, c) for (k, c), n in zip(CLASSES, CLASS_NAMES)],
               size=FS - 2, swatch=9, gap=12)
    svg.text(x0, y + 32, f"{cc['herpesviruses']} of the {cc['reported']['virus']['n']} reported viruses "
             f"({cc['herpesvirus_pct_of_viruses']:g}%) are herpesviruses", size=FS - 2, fill=MUTED)


def main() -> None:
    d = json.loads(SRC.read_text())
    svg = SVG(W, H)
    svg.text(14, 30, "a", size=22, weight="bold")
    panel_a(svg, d, 246, 262, 46, 210, 250)
    svg.text(546, 30, "b", size=22, weight="bold")
    panel_b(svg, d, 580, 60, 390)
    svg.save(OUT)


if __name__ == "__main__":
    main()
