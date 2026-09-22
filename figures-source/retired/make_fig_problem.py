#!/usr/bin/env python3
"""RETIRED 2026-09-21 (PI: the registry motivation is stated in the Introduction and Supplementary Note 6, not drawn).
Kept for reference; not built by the Makefile.  Former Figure 1 (figures/fig1_problem.svg).

Registry evidence that the mNGS report alone does not identify the pathogen: read counts of
adjudicated-causative and non-causative detections overlap across five decades, a third of
adjudicated pathogens are absent from the report of the sequenced specimen, and ten species are
causative in one patient and not in another. Numbers come from figures-source/discordance.csv,
written by tables/make_discordance.py from the registry workbook (PHI, outside this repository).
Edit this script, not the SVG.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, read_csv  # noqa: E402

OUT = HERE.parent / "figures" / "fig1_problem.svg"
W, H = 1000, 316
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"; HAIR = "#cbd5e1"
BLUE = "#1d4ed8"
GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"
AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
FS = 13


def text(svg, x, y, s, size=FS, fill=INK, anchor="start", weight="normal", style="normal"):
    svg.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight, style=style)


def heading(svg, x, y, letter, title):
    svg.text(x, y, letter, size=22, weight="bold", fill=INK)
    text(svg, x + 26, y, title, size=15, fill=INK2)


def panel_a(svg) -> None:
    """Registry evidence that the sequencing report alone does not identify the pathogen."""
    import math
    rows = [r for r in read_csv(HERE / "discordance.csv") if r["reads"] not in ("", None)]
    heading(svg, 14, 30, "a", "Read count does not separate pathogens from colonizers")
    text(svg, 40, 48, "Three-hospital registry, the 33 cases whose adjudicated pathogen list is recorded in the shared workbook: "
                      "104 organisms reported by mNGS, 55 adjudicated pathogens", size=FS - 2, fill=MUTED)
    px0, px1 = 130, 600
    ytopbox, yboxh = 60, 112
    ycau, ynon = 92, 140

    def xof(reads):
        return px0 + (math.log10(max(int(reads), 1) + 1) / 6.0) * (px1 - px0)

    svg.rect(px0 - 8, ytopbox, px1 - px0 + 16, yboxh, "#fbfbfa", stroke=HAIR, sw=1, rx=6)
    ticks = ["1", "10", "100", "1k", "10k", "100k", "1M"]
    for d, lab in enumerate(ticks):
        x = px0 + (d / 6.0) * (px1 - px0)
        svg.line(x, ytopbox + 6, x, ytopbox + yboxh - 6, stroke="#e5e7eb", sw=0.8)
        text(svg, x, ytopbox + yboxh + 14, lab, size=FS - 4, fill=MUTED, anchor="middle")
    text(svg, (px0 + px1) / 2, ytopbox + yboxh + 30, "reads reported for the organism (log scale)", size=FS - 3, fill=INK2, anchor="middle")
    for row_y, want, color, lab in ((ycau, "1", BLUE, "adjudicated"), (ynon, "0", "#9ca3af", "not causative")):
        vals = sorted(int(r["reads"]) for r in rows if r["causative"] == want)
        text(svg, px0 - 16, row_y - 2, lab, size=FS - 3, fill=INK2, anchor="end")
        if want == "1":
            text(svg, px0 - 16, row_y + 11, "causative", size=FS - 3, fill=INK2, anchor="end")
        denom = 38 if want == "1" else 66
        text(svg, px0 - 16, row_y + (24 if want == "1" else 11), f"n = {len(vals)} of {denom}", size=FS - 4, fill=MUTED, anchor="end")
        for k, v in enumerate(vals):
            svg.circle(xof(v), row_y + ((k % 3) - 1) * 7, 3.6, color, stroke="#ffffff", sw=0.8)
    # callouts in the clear band between the two rows
    x_lo = xof(7)
    svg.line(x_lo, ycau + 9, x_lo, 118, stroke=MUTED, sw=0.8, dash="2 2")
    text(svg, x_lo + 6, 116, "7 reads, adjudicated causative: P. jirovecii in BALF, confirmed by BALF PCR", size=FS - 4, fill=INK2)
    x_hi = xof(189467)
    svg.line(x_hi, ynon - 9, x_hi, 122, stroke=MUTED, sw=0.8, dash="2 2")
    text(svg, x_hi - 6, 130, "189,467 reads and grew in culture, adjudicated colonization (BALF)", size=FS - 4, fill=INK2, anchor="end")
    # the quantitative statement, under the axis
    text(svg, px0 - 8, ytopbox + yboxh + 44, "Read count alone ranks a pathogen above a non-pathogen in 61% of pairs (AUC 0.61; 0.73 in BALF and sputum,", size=FS - 3, fill=INK)
    text(svg, px0 - 8, ytopbox + yboxh + 57, "0.56 in blood, CSF and tissue). The two distributions overlap across five orders of magnitude.", size=FS - 3, fill=INK)
    # right column: three registry facts
    heading(svg, 620, 30, "b", "Where the discriminating evidence is")
    sx = 630; sw = W - 16 - sx
    facts = [("63%", "of the organisms mNGS reported were", "not the pathogen (66 of 104 detections)"),
             ("31%", "of adjudicated pathogens were absent from", "the report; 88% of those were found by"),
             ("47%", "of causative detections had same-organism", "support from another test, against 18% of")]
    tails = ["", "culture or a targeted test", "non-causative detections"]
    for j, (big, line1, line2) in enumerate(facts):
        yy = 60 + j * 50
        svg.rect(sx, yy, sw, 46, GRAY_T, stroke=GRAY_E, sw=1, rx=6)
        text(svg, sx + 12, yy + 20, big, size=FS + 3, weight="bold", fill=BLUE)
        text(svg, sx + 88, yy + 15, line1, size=FS - 3, fill=INK)
        text(svg, sx + 88, yy + 28, line2, size=FS - 4, fill=MUTED)
    for j, tail in enumerate(tails):
        if tail:
            text(svg, sx + 88, 60 + j * 50 + 41, tail, size=FS - 4, fill=MUTED)
    # the clincher band
    heading(svg, 14, 248, "c", "The same species, opposite calls")
    by = 258
    svg.rect(16, by, W - 32, 48, AMBER_T, stroke=AMBER_E, sw=1.2, rx=8)
    text(svg, 28, by + 17, "Ten species were the pathogen in one patient and a colonizer, contaminant or bystander in another — neither identity nor read count settles it:",
         size=FS - 1, weight="bold")
    text(svg, 28, by + 33, "cytomegalovirus  ·  Epstein–Barr virus  ·  herpes simplex virus 1  ·  Pneumocystis jirovecii  ·  Klebsiella pneumoniae",
         size=FS - 3, fill=INK2)
    text(svg, 28, by + 45, "Pseudomonas aeruginosa  ·  Acinetobacter nosocomialis  ·  Burkholderia cenocepacia  ·  Candida albicans  ·  Candida tropicalis",
         size=FS - 3, fill=INK2)


def main() -> None:
    svg = SVG(W, H)
    panel_a(svg)
    svg.save(OUT)


if __name__ == "__main__":
    main()
