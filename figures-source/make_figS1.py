#!/usr/bin/env python3
"""Supplementary Figure 1: cohort flow (figures/supp/figS1_cohort_flow.svg), CONSORT-style.

Numbers from Multimodal-Diagnosis-Model/docs/FRONTEND.md and docs/COHORT_VALIDATION.json (2026-09-18).
The 35-patient ICU series comes from the 2026-01-17 talk; its overlap with the 55/41 sets is unconfirmed.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG  # noqa: E402

OUT = HERE.parent / "figures" / "supp" / "figS1_cohort_flow.svg"
W, H = 1000, 600
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"
BLUE_T = "#dbeafe"; BLUE_E = "#93c5fd"; GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"; AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
FS = 13


def box(svg, x, y, w, h, title, lines, fill="#ffffff", edge=GRAY_E, tfill=GRAY_T, dashed=False):
    extra = 'stroke-dasharray="5 4"' if dashed else ""
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.2, rx=6, extra=extra)
    svg.rect(x, y, w, 24, tfill, stroke="none", rx=6)
    svg.rect(x, y + 12, w, 12, tfill, stroke="none")
    svg.text(x + 10, y + 16, title, size=FS, weight="bold", fill=INK)
    for i, ln in enumerate(lines):
        svg.text(x + 10, y + 42 + i * 15, ln, size=FS - 2, fill=INK2)


def arrow(svg, x1, y1, x2, y2):
    svg.arrow(x1, y1, x2, y2, stroke=INK2, sw=1.3, head=6)


def main() -> None:
    svg = SVG(W, H)
    # registry
    box(svg, 300, 16, 400, 78, "Three-hospital mNGS registry: 105 specimens",
        ["KMUH 51 · TVGH 35 · TSGH 19 (master index K53 / T19 / V35 = 107 specimen-cases)",
         "shared master workbook, case slide decks, laboratory grouped mNGS, clinical pathogen diagnoses"])
    arrow(svg, 420, 94, 250, 130); arrow(svg, 580, 94, 750, 130)
    # two lines
    box(svg, 40, 132, 420, 96, "KMUH line: 33 patients with saved standardized inputs",
        ["8 clinical sections + 1 mNGS section per patient; 297 / 297 sections identical",
         "to the frozen upstream inputs; IDs kmuh_case_code (Pn ↔ Knnn) + specimen code",
         "workbook label found for 24 of 33; 9 without a same-label workbook candidate"])
    box(svg, 540, 132, 420, 96, "TVGH + TSGH line: 48 of 54 registry candidates",
        ["9 clinical sections + 1 grouped mNGS per patient; 480 / 480 identical;",
         "6 patients with empty grouped mNGS (identity only); IDs legacy_global",
         "54 → 48 exclusion recipe not fully documented"])
    # main flow: elbows from each line into the 55 box; exclusions branch outward (CONSORT style)
    for xc, xend in ((250, 332), (750, 668)):
        svg.line(xc, 228, xc, 300, stroke=INK2, sw=1.3)
        arrow(svg, xc, 300, xend, 300)
    svg.text(258, 292, "30", size=FS - 2, fill=INK2, weight="bold"); svg.text(742, 292, "25", size=FS - 2, fill=INK2, weight="bold", anchor="end")
    arrow(svg, 250, 262, 202, 262); arrow(svg, 750, 262, 798, 262)
    box(svg, 40, 232, 160, 62, "Not delivered: 3", ["KMUH cases without a", "frozen R5 decision record"], dashed=True, tfill=AMBER_T, edge=AMBER_E)
    box(svg, 800, 232, 160, 62, "Not delivered: 23", ["outside the rich/moderate (20)", "and full-root (5) subsets"], dashed=True, tfill=AMBER_T, edge=AMBER_E)
    # 55
    box(svg, 332, 258, 336, 100, "R5 delivery cohort: 55 patients (Fig. 2a,b)",
        ["KMUH 30 + TVGH/TSGH 25", "518 candidates → 114 upstream picks + 9 R5 rescues = 123 selected",
         "all 55 decisions replayed byte-identical from frozen intermediates", "reference: physician-adjudicated pathogens, versioned revisions"],
        tfill=BLUE_T, edge=BLUE_E)
    # 41
    svg.line(500, 358, 500, 398, stroke=INK2, sw=1.3)
    svg.add(f'<path d="M496,392 L500,398 L504,392 Z" fill="{INK2}"/>')
    arrow(svg, 500, 378, 798, 378)
    box(svg, 800, 348, 160, 62, "Not compared: 14", ["two-hospital cases below", "input-quality grade A"], dashed=True, tfill=AMBER_T, edge=AMBER_E)
    box(svg, 332, 398, 336, 86, "Direct-prompting comparison: 41 patients (Fig. 3)",
        ["KMUH 30 answer-positive + TVGH/TSGH 11 quality-A", "identity-fixed payloads; 4 models × 41 = 164 frozen predictions",
         "AETIA on the same 41: TP 69 · FP 33 · FN 7"], tfill=BLUE_T, edge=BLUE_E)
    # ICU series
    box(svg, 40, 400, 250, 86, "Earlier ICU series: 35 patients (Fig. 2c,d)",
        ["KMUH, first pipeline version (Jan 2026 talk)", "positive rate and organisms per patient", "overlap with the 55 / 41 sets unconfirmed"],
        dashed=True, tfill=GRAY_T)
    # footnotes
    svg.text(40, 520, "Reference standard: causative pathogens adjudicated by the treating infectious-diseases physicians, with versioned revisions", size=FS - 2, fill=INK2)
    svg.text(40, 537, "(KMUH answer overrides 2026-09-14; direct-prompting gold corrections 2026-09-12). Rule development inspected these labels:", size=FS - 2, fill=INK2)
    svg.text(40, 554, "neither evaluation cohort is an untouched external test set. Amber boxes mark exclusion steps whose criteria are incompletely documented.", size=FS - 2, fill=INK2)
    svg.text(40, 580, "Counts: docs/FRONTEND.md, docs/COHORT_VALIDATION.json, docs/VALIDATION.md (Multimodal-Diagnosis-Model, 2026-09-18).", size=FS - 3, fill=MUTED)
    svg.save(OUT)


if __name__ == "__main__":
    main()
