#!/usr/bin/env python3
"""Extended Data Figure 1: cohort flow (figures/ed1_cohort_flow.svg).

A single pooled STARD flow, as convention expects of a multicentre diagnostic-accuracy study: one
spine from the registry to the two evaluation cohorts, with the per-site counts annotated at every
node and exclusions branching to the right with their reason and number. The two hospital lines
differ only in where their adjudication is stored and how their records were assembled, which is a
matter of data provenance and belongs in Methods, not in the skeleton of the diagram.

Counts from Multimodal-Diagnosis-Model/docs/FRONTEND.md, docs/COHORT_VALIDATION.json and
docs/VALIDATION.md (2026-09-18). The 35-patient ICU series comes from the 2026-01-17 talk; its
overlap with the evaluation cohorts is unconfirmed.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG  # noqa: E402

OUT = HERE.parent / "figures" / "ed1_cohort_flow.svg"
W, H = 1000, 596
INK, INK2, MUTED = "#1f2937", "#4b5563", "#6b7280"
BLUE_E, BLUE_F = "#93c5fd", "#eff6ff"
GRAY_E, GRAY_F = "#cbd5e1", "#f8fafc"
AMBER_E, AMBER_F = "#fcd34d", "#fffbeb"
FS = 13

SPINE_X, SPINE_W = 250, 410          # the pooled flow
EXCL_X, EXCL_W = 706, 258            # exclusions branch right

# title, n, per-site line, note (None for no note)
NODES = [
    ("Three-hospital mNGS registry", "105 specimens",
     "KMUH 51  ·  TVGH 35  ·  TSGH 19", None, BLUE_E, GRAY_F),
    ("Standardized record assembled", "81 patients",
     "KMUH 33  ·  TVGH + TSGH 48", None, BLUE_E, GRAY_F),
    ("Delivery cohort", "55 patients",
     "KMUH 30  ·  TVGH + TSGH 25", "primary analysis (Fig. 2a,b)", BLUE_E, BLUE_F),
    ("Direct-prompting comparison", "41 patients",
     "KMUH 30  ·  TVGH + TSGH 11", "model comparison (Fig. 3)", BLUE_E, BLUE_F),
]
# (n, reasons) aligned to the gap below node i
EXCLUSIONS = [
    ("24 specimens", ["KMUH 18: no saved standardized record",
                      "TVGH + TSGH 6: criteria not documented"]),
    ("26 patients", ["KMUH 3: no frozen decision record",
                     "TVGH + TSGH 23: outside the delivered subsets"]),
    ("14 patients", ["TVGH + TSGH: below input-quality grade A"]),
]


def node(svg, x, y, w, h, title, count, sites, note, edge, fill):
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.4, rx=7)
    svg.text(x + 18, y + 24, title, size=FS, fill=INK, weight="bold")
    svg.text(x + w - 18, y + 25, count, size=FS + 4, fill=INK, weight="bold", anchor="end")
    svg.text(x + 18, y + 44, sites, size=FS - 2, fill=INK2)
    if note:
        svg.text(x + w - 18, y + 44, note, size=FS - 2, fill=MUTED, anchor="end")


def excluded(svg, y, count, reasons):
    h = 30 + len(reasons) * 15
    svg.rect(EXCL_X, y, EXCL_W, h, AMBER_F, stroke=AMBER_E, sw=1.2, rx=6)
    svg.text(EXCL_X + 14, y + 20, "Excluded  " + count, size=FS - 1, fill="#92400e", weight="bold")
    for i, r in enumerate(reasons):
        svg.text(EXCL_X + 14, y + 36 + i * 15, r, size=FS - 2, fill=INK2)
    return h


def main() -> None:
    svg = SVG(W, H)
    node_h, gap = 62, 74
    y = 34
    centres = []
    for i, (title, count, sites, note, edge, fill) in enumerate(NODES):
        node(svg, SPINE_X, y, SPINE_W, node_h, title, count, sites, note, edge, fill)
        centres.append(y)
        if i < len(NODES) - 1:
            ymid = y + node_h + gap / 2
            svg.line(SPINE_X + SPINE_W / 2, y + node_h, SPINE_X + SPINE_W / 2, y + node_h + gap - 8,
                     stroke=INK2, sw=1.4)
            svg.add(f'<path d="M{SPINE_X + SPINE_W / 2 - 4.5},{y + node_h + gap - 9} '
                    f'L{SPINE_X + SPINE_W / 2},{y + node_h + gap - 1} '
                    f'L{SPINE_X + SPINE_W / 2 + 4.5},{y + node_h + gap - 9} Z" fill="{INK2}"/>')
            n, reasons = EXCLUSIONS[i]
            bh = excluded(svg, ymid - (30 + len(reasons) * 15) / 2, n, reasons)
            svg.line(SPINE_X + SPINE_W / 2, ymid, EXCL_X - 9, ymid, stroke=INK2, sw=1.2)
            svg.add(f'<path d="M{EXCL_X - 10},{ymid - 4.5} L{EXCL_X - 1},{ymid} '
                    f'L{EXCL_X - 10},{ymid + 4.5} Z" fill="{INK2}"/>')
        y += node_h + gap
    y -= gap - 26

    # the earlier series is not part of this flow: shown detached, to the left of the delivery node
    sy = centres[1] + 4
    svg.rect(30, sy, 190, 76, GRAY_F, stroke=GRAY_E, sw=1.2, rx=6, extra='stroke-dasharray="5 4"')
    svg.text(44, sy + 22, "Earlier ICU series", size=FS - 1, fill=INK, weight="bold")
    svg.text(44, sy + 40, "35 patients, KMUH", size=FS - 2, fill=INK2)
    svg.text(44, sy + 56, "organism burden (Fig. 2c,d)", size=FS - 2, fill=MUTED)
    svg.text(44, sy + 70, "overlap with the 55 unconfirmed", size=FS - 3, fill=MUTED)

    fy = y + 4
    for line in (
        "Reference standard: causative pathogens adjudicated by the treating infectious-diseases physicians, with versioned revisions.",
        "The scoring rules were developed with these labels visible, so neither evaluation cohort is an untouched external test set.",
        "Both cohorts required at least one adjudicated pathogen; patients whose final diagnosis was not pulmonary infection were not evaluated.",
    ):
        svg.text(30, fy, line, size=FS - 2, fill=INK2)
        fy += 17
    svg.text(30, fy + 6, "Counts: docs/FRONTEND.md, docs/COHORT_VALIDATION.json, docs/VALIDATION.md "
             "(Multimodal-Diagnosis-Model, 2026-09-18).", size=FS - 3, fill=MUTED)
    svg.save(OUT)


if __name__ == "__main__":
    main()
