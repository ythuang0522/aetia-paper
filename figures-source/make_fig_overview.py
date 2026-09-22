#!/usr/bin/env python3
"""Figure 1: overview of AETIA (figures/fig1_overview.svg). Edit this script, not the SVG.

Pictorial schematic in four rows, concept-level labels only (no tier codes or rule counts;
those live in Methods and the Supplementary tables):
  a, one patient's record -> one language-model agent per read-out -> structured evidence;
  b, rule-based selection: funnel of four filters, colonizer guardrails, picked organisms,
     language-model safety review that can flag but not pick;
  c, evidence tracing for every candidate (literature and case-fit, sequencing strength,
     direct evidence, colonization check);
  d, the final rule as a clinical algorithm: three selection criteria (passed every filter and
     guardrail in b; the same species from a sterile site; published cases matching this patient
     with site and sequencing support), any one sufficient, joined by a brace and drawn with the
     pictures of the panels they come from -> the list frozen with the criterion that selected
     each organism -> the delivered record, one entry per organism with the findings for and
     against, in the chip idiom of Fig. 4.
A running example carries the same organism glyphs through all rows: a bacterium and a virus
are picked by the rules, a mould flagged by the review is rescued by traced evidence, a yeast
is held back by a guardrail. Two visual codes mark the division of labour: violet chip =
language model (extracts, judges, explains; never decides); blue cog = deterministic rule.
Canvas 1000 units = 180 mm (Nature double column); 13 units ~ 6.6 pt; nothing below 11.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG  # noqa: E402
import icons as I  # noqa: E402

OUT = HERE.parent / "figures" / "fig1_overview.svg"
W, H = 1000, 930
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"; HAIR = "#cbd5e1"
BLUE = "#1d4ed8"; BLUE_T = "#dbeafe"; BLUE_E = "#93c5fd"
VIOL = "#6d28d9"; VIOL_T = "#ede9fe"; VIOL_E = "#c4b5fd"
GREEN = "#15803d"; GREEN_T = "#dcfce7"; GREEN_E = "#86efac"
AMBER = "#d97706"; AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"
ORANGE = "#f97316"; ORANGE_T = "#fdba74"
FS = 13          # body labels
FS2 = 12         # secondary lines (never below 11)
GHOST = "#9ca3af"   # organisms that are set aside


def text(svg, x, y, s, size=FS, fill=INK, anchor="start", weight="normal", style="normal"):
    svg.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight, style=style)


def card(svg, x, y, w, h, fill=GRAY_T, edge=GRAY_E, rx=8):
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.2, rx=rx)


def title(svg, x, y, s, icon=None, size=FS + 1):
    """Card title with an optional 24-unit marker icon at its left."""
    if icon:
        icon(svg, x, y - 17, 24)
        text(svg, x + 30, y, s, size=size, weight="bold")
    else:
        text(svg, x, y, s, size=size, weight="bold")


def pill(svg, cx, cy, label, fill, edge, size=FS, icon=None, w=None, h=26):
    tw = len(label) * size * 0.52 + 24 + (28 if icon else 0)
    w = w or tw
    svg.rect(cx - w / 2, cy - h / 2, w, h, fill, stroke=edge, sw=1.2, rx=h / 2)
    if icon:
        icon(svg, cx - w / 2 + 8, cy - 11, 22)
        text(svg, cx - w / 2 + 34, cy + size * 0.36, label, size=size)
    else:
        text(svg, cx, cy + size * 0.36, label, size=size, anchor="middle")


def arrow(svg, x1, y1, x2, y2, color=INK2, sw=1.4):
    svg.arrow(x1, y1, x2, y2, stroke=color, sw=sw, head=6)


def heading(svg, x, y, letter, s):
    svg.text(x, y, letter, size=22, weight="bold", fill=INK)
    text(svg, x + 26, y, s, size=15, fill=INK2)


def ghost(glyph):
    """Grey version of an organism glyph (set aside)."""
    return lambda svg, cx, cy, s: glyph(svg, cx, cy, s, ink=GHOST, fill="#f3f4f6")


def main() -> None:
    svg = SVG(W, H)

    # ---------------------------------------------------------------- key --------------------
    kx = 566; ky = 10
    svg.rect(kx, ky, W - 16 - kx, 46, "#ffffff", stroke=GRAY_E, sw=1, rx=6)
    I.brain_chip(svg, kx + 8, ky + 2, 20)
    text(svg, kx + 34, ky + 17, "Language model", size=FS2, weight="bold")
    text(svg, kx + 150, ky + 17, "extracts, judges, explains; never decides", size=FS2, fill=INK2)
    I.cog(svg, kx + 8, ky + 24, 20)
    text(svg, kx + 34, ky + 39, "Deterministic rule", size=FS2, weight="bold")
    text(svg, kx + 150, ky + 39, "decides; versioned and traceable", size=FS2, fill=INK2)

    # ================================================================ a ==========================
    heading(svg, 14, 30, "a", "Evidence extraction from one patient's record")
    mods = [
        ("Chest imaging", "report text", I.xray, [I.bacterium, I.fungus]),
        ("Diagnoses", "comorbidities", I.clipboard, [I.person]),
        ("Blood counts", "CRP, other labs", I.blood_tube, [I.person]),
        ("Galactomannan", "antigen", I.well_plate, [I.fungus]),
        ("Multiplex PCR", "respiratory panel", I.pcr_box, [I.virus, I.bacterium]),
        ("Cultures", "blood, sputum, BAL", I.petri, [I.bacterium, I.yeast]),
        ("mNGS report", "reads per organism", I.sequencer, [I.bacterium, I.fungus, I.virus]),
    ]
    colw = 138; x0 = 16; ytop = 70
    cxs = [x0 + i * colw + colw / 2 for i in range(7)]
    for i, ((l1, l2, icon, glyphs), cx) in enumerate(zip(mods, cxs)):
        icon(svg, cx - 29, ytop, 58)
        text(svg, cx, ytop + 76, l1, size=FS, anchor="middle", weight="bold")
        text(svg, cx, ytop + 91, l2, size=FS2, fill=MUTED, anchor="middle")
        arrow(svg, cx, ytop + 98, cx, ytop + 112)
    # agents: one language-model agent per read-out (host agent spans two, antigen/panel agent two)
    ya = ytop + 128
    agents = [(0, 0, "Imaging agent"), (1, 2, "Host agent"), (3, 4, "Antigen and panel agent"), (5, 5, "Culture agent")]
    for a, b, lab in agents:
        cx = (cxs[a] + cxs[b]) / 2
        w = (cxs[b] - cxs[a]) + 122
        pill(svg, cx, ya, lab, VIOL_T, VIOL_E, icon=I.brain_chip, w=w)
    pill(svg, cxs[6], ya, "Specimen and site", GRAY_T, GRAY_E, w=122)
    # organisms or host context each agent can report
    for (l1, l2, icon, glyphs), cx in zip(mods, cxs):
        n = len(glyphs); gap = 30
        for j, g in enumerate(glyphs):
            g(svg, cx + (j - (n - 1) / 2) * gap, ya + 40, 26)
    # bus into the structured evidence
    ybus = ya + 68
    for cx in cxs:
        svg.line(cx, ya + 58, cx, ybus, stroke=INK2, sw=1.2)
    svg.line(cxs[0], ybus, cxs[6], ybus, stroke=INK2, sw=1.2)
    xc = (cxs[0] + cxs[6]) / 2
    arrow(svg, xc, ybus, xc, ybus + 16)
    ex, ey, ew, eh = 130, ybus + 18, 740, 52
    card(svg, ex, ey, ew, eh)
    I.document(svg, ex + 10, ey + 6, 40)
    text(svg, ex + 56, ey + 22, "Structured evidence", size=FS + 1, weight="bold")
    text(svg, ex + 56, ey + 40, "organism support by modality  ·  host immune status  ·  specimen, site and timing", size=FS2, fill=INK2)
    text(svg, ex + ew - 12, ey + 22, "each agent sees only its own read-out", size=FS2, fill=MUTED, anchor="end")
    text(svg, ex + ew - 12, ey + 40, "no reference labels", size=FS2, fill=MUTED, anchor="end")

    # ================================================================ b ==========================
    yb = ey + eh + 44
    heading(svg, 14, yb, "b", "Rule-based selection of causative organisms")
    # mNGS report: organisms with read bars
    lx = 16; ly = yb + 24
    text(svg, lx, ly, "mNGS report", size=FS, weight="bold")
    text(svg, lx, ly + 15, "organisms and reads", size=FS2, fill=MUTED)
    cands = [(I.bacterium, 96), (I.virus, 70), (I.yeast, 62), (I.bacterium, 40),
             (I.fungus, 30), (I.bacterium, 18), (I.virus, 10), (I.bacterium, 5)]
    for j, (g, reads) in enumerate(cands):
        yy = ly + 36 + j * 21
        g(svg, lx + 14, yy, 20)
        svg.rect(lx + 32, yy - 4, reads, 8, ORANGE if j == 0 else ORANGE_T, rx=2)
    # funnel with four filters
    fx0, fx1 = 196, 650; fy = ly + 8; fh0, fh1 = 152, 96
    fmid = fy + fh0 / 2
    svg.path(f"M{fx0},{fy} L{fx1},{fmid - fh1 / 2} L{fx1},{fmid + fh1 / 2} L{fx0},{fy + fh0} Z",
             stroke=HAIR, sw=1.2, fill="#ffffff")
    arrow(svg, lx + 150, fmid, fx0, fmid)
    filters = ["Read burden", "Dominance in the specimen", "Background control", "Site and hospital support"]
    sw_ = 20; sgap = (fx1 - fx0 - 4 * sw_) / 5
    I.cog(svg, fx0 + 4, fy + 2, 22)
    for i, t1 in enumerate(filters):
        sx = fx0 + sgap + i * (sw_ + sgap)
        t = (sx + sw_ / 2 - fx0) / (fx1 - fx0)
        hh = fh0 + (fh1 - fh0) * t
        top = fmid - hh / 2 + 6
        svg.rect(sx, top, sw_, hh - 12, GRAY_T, stroke=GRAY_E, sw=1.2, rx=4)
        for yy in range(int(top + 8), int(top + hh - 16), 8):
            svg.line(sx + 4, yy, sx + sw_ - 4, yy, stroke=HAIR, sw=0.8)
        svg.circle(sx + sw_ / 2, top + hh - 12 - 4, 9, INK)
        text(svg, sx + sw_ / 2, top + hh - 12, str(i + 1), size=FS2, fill="#ffffff", anchor="middle", weight="bold")
        # organisms still in play after this filter
        keep = [I.bacterium, I.virus, I.yeast, I.fungus, I.bacterium, I.virus][: 6 - i]
        gx = sx + sw_ + sgap / 2
        for j, g in enumerate(keep):
            g(svg, gx, fmid - (len(keep) - 1) * 11 + j * 22, 18)
    # filter names keyed by number, two per row under the funnel
    for i, t1 in enumerate(filters):
        xx = fx0 + (i % 2) * 214; yy = fy + fh0 + 20 + (i // 2) * 19
        svg.circle(xx + 8, yy - 4, 8, INK)
        text(svg, xx + 8, yy, str(i + 1), size=11, fill="#ffffff", anchor="middle", weight="bold")
        text(svg, xx + 21, yy, t1, size=FS, weight="bold")
    # guardrail band: colonizers deflected before picking
    gy = fy + fh0 + 52; gh = 62
    svg.rect(fx0, gy, fx1 - fx0, gh, AMBER_T, stroke=AMBER_E, sw=1.2, rx=8)
    text(svg, fx0 + 12, gy + 21, "Colonizer guardrails", size=FS, weight="bold")
    text(svg, fx0 + 12, gy + 38, "oral flora  ·  skin and water organisms", size=FS2, fill=INK2)
    text(svg, fx0 + 12, gy + 53, "respiratory Candida  ·  latent herpesviruses", size=FS2, fill=INK2)
    text(svg, fx1 - 12, gy + 38, "hold back organisms", size=FS2, fill=INK2, anchor="end")
    text(svg, fx1 - 12, gy + 53, "the filters would pass", size=FS2, fill=INK2, anchor="end")
    for j, g in enumerate([I.yeast, I.bacterium, I.virus]):
        gx = fx1 - 20 - (2 - j) * 34
        ghost(g)(svg, gx, gy + 20, 18); I.cross(svg, gx + 9, gy + 9, 12)
    # picked
    px = fx1 + 26; pw = 150; py = fy; ph = fh0
    card(svg, px, py, pw, ph, BLUE_T, BLUE_E)
    title(svg, px + 12, py + 24, "Picked", icon=I.cog)
    for j, (g, lab) in enumerate([(I.bacterium, "primary"), (I.virus, "secondary")]):
        yy = py + 58 + j * 32
        g(svg, px + 30, yy, 22); I.check(svg, px + 54, yy, 15)
        text(svg, px + 68, yy + 4, lab, size=FS2, fill=INK2)
    text(svg, px + 12, py + ph - 26, "order fixed; no later", size=FS2, fill=INK2)
    text(svg, px + 12, py + ph - 12, "stage may change it", size=FS2, fill=INK2)
    arrow(svg, fx1, fmid, px, fmid)
    # safety review: language model reads only the unpicked organisms
    rx = px + pw + 18; rw = W - 16 - rx
    card(svg, rx, py, rw, ph, VIOL_T, VIOL_E)
    title(svg, rx + 12, py + 24, "Safety review", icon=I.brain_chip)
    text(svg, rx + 12, py + 44, "reads only the unpicked;", size=FS2, fill=INK2)
    text(svg, rx + 12, py + 58, "may flag, cannot pick", size=FS2, fill=INK2)
    for j, (g, lab, carried) in enumerate([(I.fungus, "flagged", True), (I.bacterium, "flagged", True),
                                            (I.yeast, "audit only", False), (I.virus, "audit only", False)]):
        yy = py + 80 + j * 19
        (g if carried else ghost(g))(svg, rx + 24, yy, 17)
        if carried:
            I.flag(svg, rx + 42, yy, 13)
        text(svg, rx + 56, yy + 4, lab, size=FS2, fill=INK2 if carried else MUTED)
    # unpicked organisms flow from the funnel floor, under the picked card, into the review
    yflow = py + ph + 34
    svg.path(f"M{fx1 - 24},{fmid + fh1 / 2 + 3} C{fx1 - 24},{yflow} {fx1 + 10},{yflow} {px + 40},{yflow} "
             f"L{rx + 60},{yflow} C{rx + rw / 2},{yflow} {rx + rw / 2},{yflow} {rx + rw / 2},{py + ph + 3}",
             stroke=VIOL, sw=1.2)
    svg.add(f'<path d="M{rx + rw / 2 - 4},{py + ph + 9} L{rx + rw / 2},{py + ph + 1} L{rx + rw / 2 + 4},{py + ph + 9} Z" fill="{VIOL}"/>')
    text(svg, px + pw / 2, yflow - 6, "unpicked organisms", size=FS2, fill=VIOL, anchor="middle")
    # candidates carried forward
    cy_ = yflow + 26
    svg.line(px, cy_, W - 16, cy_, stroke=INK2, sw=1.2)
    svg.line(px, cy_ - 6, px, cy_, stroke=INK2, sw=1.2); svg.line(W - 16, cy_ - 6, W - 16, cy_, stroke=INK2, sw=1.2)
    text(svg, (px + W - 16) / 2, cy_ + 17, "Candidates for evidence tracing:", size=FS, anchor="middle", weight="bold")
    text(svg, (px + W - 16) / 2, cy_ + 32, "picked and flagged organisms", size=FS, anchor="middle", weight="bold")

    # ================================================================ c ==========================
    # Evidence matrix: one row per carried candidate, one column per evidence source. Column
    # headers draw how each source is produced (PubMed articles read by a language model against
    # the label-blind case card; sequencing strength, direct tests and the colonization check
    # graded by rules); cells are glyphs (verdict dots per article, strength bars, specimen
    # ladder, colonization dot). The matrix is the evidence profile that the final rule (d) reads.
    yc = max(gy + gh, cy_ + 32) + 44
    heading(svg, 14, yc, "c", "Evidence tracing for every candidate")
    ccy = yc + 16
    hdr_h = 126; row_h = 30; nrow = 4
    cols = {"lit": (146, 322), "seq": (478, 140), "dir": (628, 184), "col": (822, 130)}
    rows_y0 = ccy + hdr_h + 10
    ch = hdr_h + 10 + nrow * row_h
    # ---- column headers
    # literature: PubMed -> language model reads each article against the case card -> verdict
    x, w = cols["lit"]
    card(svg, x, ccy, w, hdr_h, VIOL_T, VIOL_E)
    title(svg, x + 10, ccy + 20, "Literature, read by a language model", icon=I.brain_chip, size=FS)
    for k in range(3):
        I.document(svg, x + 14 + k * 8, ccy + 30 + k * 4, 30)
    I.magnifier(svg, x + 42, ccy + 54, 20)
    text(svg, x + 10, ccy + 96, "PubMed", size=11, fill=INK2)
    text(svg, x + 10, ccy + 108, "up to 10 articles", size=11, fill=INK2)
    arrow(svg, x + 84, ccy + 54, x + 98, ccy + 54, color=VIOL)
    I.brain_chip(svg, x + 104, ccy + 36, 36)
    text(svg, x + 146, ccy + 58, "vs", size=FS2, fill=VIOL, weight="bold")
    I.clipboard(svg, x + 162, ccy + 34, 38)
    text(svg, x + 102, ccy + 84, "reads each article against", size=11, fill=INK2)
    text(svg, x + 102, ccy + 96, "the label-blind case card:", size=11, fill=INK2)
    text(svg, x + 102, ccy + 108, "site · syndrome · host ·", size=11, fill=INK2)
    text(svg, x + 102, ccy + 120, "phenotype · timing", size=11, fill=INK2)
    arrow(svg, x + 240, ccy + 54, x + 254, ccy + 54, color=VIOL)
    I.cog(svg, x + 258, ccy + 30, 24)
    text(svg, x + 284, ccy + 47, "verdict", size=11, fill=INK2)
    for k, (col, lab) in enumerate([(GREEN, "strong"), (AMBER, "partial"), ("#d1d5db", "neither")]):
        yy = ccy + 70 + k * 13
        svg.circle(x + 266, yy - 4, 4.5, col); text(svg, x + 275, yy, lab, size=11, fill=INK2)
    text(svg, x + 260, ccy + 120, "per article", size=11, fill=MUTED)
    # sequencing strength
    x, w = cols["seq"]
    card(svg, x, ccy, w, hdr_h, GRAY_T, GRAY_E)
    title(svg, x + 10, ccy + 20, "Sequencing", icon=I.cog, size=FS)
    I.sequencer(svg, x + 6, ccy + 36, 32)
    for k, hgt in enumerate((10, 16, 24, 32)):
        svg.rect(x + 46 + k * 9, ccy + 74 - hgt, 7, hgt, ORANGE_T if k < 2 else ORANGE, rx=1.5)
    svg.rect(x + 100, ccy + 42, 8, 32, ORANGE, rx=1.5); svg.rect(x + 110, ccy + 66, 8, 8, ORANGE_T, rx=1.5)
    text(svg, x + 62, ccy + 88, "burden", size=11, fill=INK2, anchor="middle")
    text(svg, x + 110, ccy + 88, "dominance", size=11, fill=INK2, anchor="middle")
    text(svg, x + 10, ccy + 108, "reads per organism;", size=11, fill=MUTED)
    text(svg, x + 10, ccy + 120, "with site alignment", size=11, fill=MUTED)
    # direct evidence
    x, w = cols["dir"]
    card(svg, x, ccy, w, hdr_h, GRAY_T, GRAY_E)
    title(svg, x + 10, ccy + 20, "Direct tests", icon=I.cog, size=FS)
    I.petri(svg, x + 8, ccy + 26, 28); I.pcr_box(svg, x + 36, ccy + 26, 28); I.well_plate(svg, x + 64, ccy + 26, 28)
    text(svg, x + 100, ccy + 40, "same organism", size=11, fill=INK2)
    text(svg, x + 100, ccy + 52, "by culture, PCR", size=11, fill=INK2)
    text(svg, x + 100, ccy + 64, "or antigen", size=11, fill=INK2)
    for k, (hgt, col, l1, l2) in enumerate([(12, "#bfdbfe", "context", "only"), (22, "#60a5fa", "target", "site"), (32, BLUE, "sterile", "site")]):
        xx = x + 12 + k * 37
        svg.rect(xx, ccy + 94 - hgt, 20, hgt, col, rx=2)
        text(svg, xx + 10, ccy + 108, l1, size=11, fill=INK2, anchor="middle")
        text(svg, xx + 10, ccy + 120, l2, size=11, fill=INK2, anchor="middle")
    text(svg, x + 124, ccy + 100, "graded by", size=11, fill=MUTED)
    text(svg, x + 124, ccy + 112, "specimen", size=11, fill=MUTED)
    # colonization check
    x, w = cols["col"]
    card(svg, x, ccy, w, hdr_h, GRAY_T, GRAY_E)
    title(svg, x + 10, ccy + 20, "Colonization", icon=I.cog, size=FS)
    I.sieve(svg, x + 10, ccy + 36, w - 20, 14)
    for k, (col, lab) in enumerate([(GREEN, "fits the site"), (AMBER, "guarded"), ("#b91c1c", "colonizer")]):
        yy = ccy + 70 + k * 13
        svg.circle(x + 16, yy - 4, 4.5, col); text(svg, x + 25, yy, lab, size=11, fill=INK2)
    text(svg, x + 10, ccy + 120, "reported, not a gate", size=11, fill=MUTED)
    # ---- rows: the carried candidates
    text(svg, 16, ccy + 20, "Candidates", size=FS, weight="bold")
    text(svg, 16, ccy + 36, "picked and flagged", size=11, fill=MUTED)
    text(svg, 16, ccy + 48, "organisms from b", size=11, fill=MUTED)
    example = [
        # glyph, picked?, article verdicts, burden(h, pos), dominance(h, pos), direct(assay, level), colonization
        (I.bacterium, True,  [GREEN, GREEN, GREEN, AMBER, "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db"], (22, True), (20, True), (I.petri, 2), GREEN),
        (I.virus,     True,  [GREEN, AMBER, AMBER, "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db"], (14, True), (5, False), (I.pcr_box, 2), GREEN),
        (I.fungus,    False, [GREEN, GREEN, AMBER, AMBER, AMBER, "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db"], (11, False), (6, False), (None, 0), GREEN),
        (I.bacterium, False, [AMBER, "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db", "#d1d5db"], (8, False), (4, False), (None, 0), AMBER),
    ]
    for r, (g, picked, verd, burden, dom, direct, colz) in enumerate(example):
        ry = rows_y0 + r * row_h; ym = ry + row_h / 2
        if r:
            svg.line(16, ry, cols["col"][0] + cols["col"][1] + 6, ry, stroke=GRAY_E, sw=0.8)
        g(svg, 36, ym, 20)
        (I.check if picked else I.flag)(svg, 58, ym, 13)
        text(svg, 70, ym + 4, "picked" if picked else "flagged", size=11, fill=INK2)
        # literature: one dot per article, then the counts the rule reads
        x, w = cols["lit"]
        for k, col in enumerate(verd):
            svg.circle(x + 14 + k * 15, ym, 5, col)
        ns = sum(c == GREEN for c in verd); npart = sum(c == AMBER for c in verd)
        text(svg, x + 176, ym + 4, f"strong {ns} · partial {npart}", size=11, fill=INK2)
        # sequencing: burden and dominance bars (full colour when the axis is positive)
        x, w = cols["seq"]
        for k, (hgt, pos) in enumerate((burden, dom)):
            svg.rect(x + 62 + k * 44, ym + 12 - hgt, 10, hgt, ORANGE if pos else ORANGE_T, rx=1.5)
        # direct tests: assay icon and the specimen ladder filled to the achieved level
        x, w = cols["dir"]
        assay, level = direct
        if assay:
            assay(svg, x + 62, ym - 11, 22)
        for k, hgt in enumerate((8, 14, 20)):
            xx = x + 104 + k * 22
            reached = k < level
            svg.rect(xx, ym + 10 - hgt, 16, hgt, [BLUE, "#60a5fa", BLUE][k] if reached else "#ffffff",
                     stroke=BLUE if reached else "#cbd5e1", sw=0.8, rx=1.5)
        if not assay:
            text(svg, x + 62, ym + 4, "none", size=11, fill=MUTED)
        # colonization
        x, w = cols["col"]
        svg.circle(x + 16 + 4, ym, 5.5, colz)
    # matrix -> final rule
    mx1 = cols["col"][0] + cols["col"][1]
    svg.rect(16, rows_y0 - 6, mx1 + 6 - 16, nrow * row_h + 12, "none", stroke=INK2, sw=1, rx=6)
    ymid = rows_y0 + nrow * row_h / 2
    arrow(svg, mx1 + 6, ymid, mx1 + 15, ymid)
    svg.text(W - 20, ymid, "read by the final rule (d)", size=11, fill=INK2, anchor="middle", rotate=-90)

    # ================================================================ d ==========================
    # The final rule as a clinical algorithm: three selection criteria, any one of which is
    # sufficient, joined by a brace (no logic-gate symbol). Each criterion is drawn with the
    # picture of the panel it comes from (b's funnel, c's specimen ladder, c's verdict dots, read
    # bars and site marker) and the example organisms ride the criterion that selected them.
    # Criteria 1-3 are the rule_path values the code records (picked / C3_direct / A1_site_B,
    # OBER_patient_delivery/generate_r5_final_decisions.py:17-21,98-116). The delivered record is
    # drawn in the chip idiom of Fig. 4: one line per finding, with what it does to the call.
    yd = ccy + ch + 44
    heading(svg, 14, yd, "d", "Final selection and the delivered record")
    dy = yd + 20
    LH = (46, 46, 70); LGAP = 10
    dh = sum(LH) + 2 * LGAP
    lx, lw = 16, 384
    lane_y = (dy, dy + LH[0] + LGAP, dy + LH[0] + LH[1] + 2 * LGAP)
    lane_mid = tuple(ly + h / 2 for ly, h in zip(lane_y, LH))
    CRIT_C = (BLUE, INK2, GREEN)

    def badge(cx, cy, n, color, r=9, lit=True):
        svg.circle(cx, cy, r, color if lit else "#ffffff", stroke="none" if lit else HAIR, sw=1.2)
        text(svg, cx, cy + 4, str(n), size=FS2, fill="#ffffff" if lit else "#9ca3af",
             anchor="middle", weight="bold")

    # ---- criterion 1: the organisms the filters and guardrails of b already selected
    y = lane_y[0]
    svg.rect(lx, y, lw, LH[0], BLUE_T, stroke=BLUE_E, sw=1.2, rx=8)
    badge(lx + 18, y + 23, 1, BLUE)
    fa, fb = lx + 34, lx + 74                      # b's funnel in miniature
    svg.path(f"M{fa},{y + 9} L{fb},{y + 17} L{fb},{y + 29} L{fa},{y + 37} Z", stroke=BLUE, sw=1.3, fill="#ffffff")
    for dyy in (-8, 0, 8):
        svg.circle(fa + 11, y + 23 + dyy, 2.6, BLUE_E)
    svg.circle(fb - 7, y + 19, 2.6, BLUE); svg.circle(fb - 7, y + 27, 2.6, BLUE)
    text(svg, lx + 86, y + 20, "Passed every filter and guardrail", size=FS2, weight="bold")
    text(svg, lx + 86, y + 35, "the organisms selected in b", size=FS2, fill=INK2)
    I.bacterium(svg, lx + 328, y + 23, 22); I.virus(svg, lx + 362, y + 23, 22)

    # ---- criterion 2: the same species grown or amplified from a sterile site
    y = lane_y[1]
    svg.rect(lx, y, lw, LH[1], GRAY_T, stroke=GRAY_E, sw=1.2, rx=8)
    badge(lx + 18, y + 23, 2, INK2)
    I.bottle(svg, lx + 32, y + 11, 24, growth=True)
    I.petri(svg, lx + 56, y + 11, 24); I.pcr_box(svg, lx + 80, y + 11, 24)
    for k2, hgt in enumerate((8, 13, 20)):         # c's specimen ladder, sterile-site rung reached
        xx = lx + 110 + k2 * 14
        top = k2 == 2
        svg.rect(xx, y + 33 - hgt, 11, hgt, BLUE if top else "#ffffff",
                 stroke=BLUE if top else HAIR, sw=0.9, rx=1.5)
    svg.line(lx + 108, y + 34, lx + 153, y + 34, stroke=HAIR, sw=1)
    text(svg, lx + 164, y + 20, "Same species from a sterile site", size=FS2, weight="bold")
    text(svg, lx + 164, y + 35, "by culture, PCR or antigen", size=FS2, fill=INK2)
    svg.add(f'<circle cx="{lx + 364}" cy="{y + 16}" r="10" fill="#ffffff" stroke="{HAIR}" '
            f'stroke-width="1.2" stroke-dasharray="3 3"/>')
    text(svg, lx + 364, y + 40, "none", size=11, fill=MUTED, anchor="middle")

    # ---- criterion 3: published cases that match this patient, with site and sequencing support
    y = lane_y[2]
    svg.rect(lx, y, lw, LH[2], GREEN_T, stroke=GREEN_E, sw=1.2, rx=8)
    badge(lx + 18, y + 35, 3, GREEN)
    text(svg, lx + 34, y + 18, "Published cases match this patient", size=FS2, weight="bold")
    text(svg, lx + 254, y + 18, "all three required", size=11, fill=INK2)
    cw3 = 92
    for k2, (l1, l2) in enumerate((("matching", "published cases"), ("specimen site", "matches"),
                                   ("high or dominant", "read count"))):
        cx3 = lx + 34 + k2 * (cw3 + 14)
        svg.rect(cx3, y + 24, cw3, 40, "#ffffff", stroke=GREEN_E, sw=1.1, rx=6)
        mid = cx3 + cw3 / 2
        if k2 == 0:
            for j, col in enumerate((GREEN, GREEN, AMBER)):
                svg.circle(mid + (j - 1) * 14, y + 35, 4.6, col)
        elif k2 == 1:
            I.site_pin(svg, mid - 19, y + 25, 20); I.check(svg, mid + 11, y + 35, 13)
        else:
            svg.rect(mid - 11, y + 28, 9, 14, ORANGE, rx=1.5)
            svg.rect(mid + 2, y + 33, 9, 9, ORANGE, rx=1.5)
        text(svg, mid, y + 51, l1, size=11, fill=INK2, anchor="middle")
        text(svg, mid, y + 61, l2, size=11, fill=INK2, anchor="middle")
        if k2 < 2:
            text(svg, cx3 + cw3 + 7, y + 48, "+", size=FS + 3, fill=GREEN, anchor="middle", weight="bold")
    svg.add(f'<circle cx="{lx + 364}" cy="{y + 38}" r="10" fill="#ffffff" stroke="{HAIR}" '
            f'stroke-width="1.2" stroke-dasharray="3 3"/>')
    text(svg, lx + 364, y + 62, "none", size=11, fill=MUTED, anchor="middle")

    # ---- the criteria are joined by a brace: any one of them selects
    bx = lx + lw + 20; gmid = dy + dh / 2
    y0, y1 = dy + 4, dy + dh - 4
    svg.path(f"M{bx},{y0} Q{bx + 10},{y0} {bx + 10},{(y0 + gmid) / 2} Q{bx + 10},{gmid} {bx + 20},{gmid} "
             f"Q{bx + 10},{gmid} {bx + 10},{(gmid + y1) / 2} Q{bx + 10},{y1} {bx},{y1}",
             stroke=INK, sw=1.6)
    for i, cy_ in enumerate(lane_mid):
        svg.line(lx + lw, cy_, bx + 2, cy_, stroke=CRIT_C[i], sw=1.6, dash="" if i == 0 else "4 3")
    I.cog(svg, bx + 26, gmid - 12, 24)
    arrow(svg, bx + 54, gmid, bx + 92, gmid)
    text(svg, bx + 36, dy + dh + 16, "any one", size=FS2, fill=MUTED, anchor="middle")

    # ---- the list, frozen before any text is written; its first organism is expanded at right
    fx = bx + 96; fw = 136
    card(svg, fx, dy, fw, dh, BLUE_T, BLUE_E)
    title(svg, fx + 10, dy + 24, "Final list", icon=I.lock)
    text(svg, fx + 10, dy + 42, "frozen before any", size=11, fill=INK2)
    text(svg, fx + 10, dy + 55, "text is written", size=11, fill=INK2)
    row1 = dy + 78
    svg.rect(fx + 8, row1 - 13, fw - 16, 26, "#ffffff", stroke=BLUE, sw=1.4, rx=8)
    for j, (g, sel, lab) in enumerate([(I.bacterium, True, "selected"), (I.virus, True, "selected"),
                                       (I.fungus, False, "not selected"), (I.bacterium, False, "not selected")]):
        yy = row1 + j * 30
        (g if sel else ghost(g))(svg, fx + 24, yy, 21)
        text(svg, fx + 42, yy + 4, lab, size=11, fill=INK2 if sel else MUTED)

    # ---- what the clinician receives for one selected organism: the findings that implicate it,
    # in this patient's own context (the worked entry of Fig. 4c, Case 1; prototype vignette).
    cx0 = fx + fw + 18; cw = W - 16 - cx0
    card(svg, cx0, dy, cw, dh)
    title(svg, cx0 + 12, dy + 22, "Delivered record", icon=I.table_icon)
    text(svg, cx0 + 12, dy + 40, "the explanation written for this organism", size=11, fill=MUTED)
    svg.line(cx0 + 10, dy + 54, cx0 + cw - 10, dy + 54, stroke=GRAY_E, sw=1)
    # the leader starts at the highlighted row, not at the card, so the entry belongs to that organism
    svg.arrow(fx + fw - 6, row1, cx0 + 16, row1, stroke=BLUE, sw=1.4, head=6)
    I.bacterium(svg, cx0 + 32, row1, 22)
    svg.rich(cx0 + 48, row1 + 4, [("Klebsiella pneumoniae", {"font-style": "italic", "font-weight": "bold"})],
             size=FS2, fill=INK)
    pw = 88
    svg.rect(cx0 + cw - 12 - pw, row1 - 10, pw, 21, GREEN_T, stroke=GREEN_E, sw=1.1, rx=10.5)
    text(svg, cx0 + cw - 12 - pw / 2, row1 + 4, "SELECTED", size=FS2, fill=GREEN, anchor="middle", weight="bold")
    text(svg, cx0 + 32, row1 + 22, "ventilated patient  ·  lavage specimen", size=11, fill=MUTED)
    for k2, (icon, lab) in enumerate([(I.sequencer, "dominant, highest read count"),
                                      (I.xray, "bilateral consolidation"),
                                      (I.blood_tube, "CRP peak with hypoxaemia"),
                                      (I.document, "published cases match site and host")]):
        ly = row1 + 40 + k2 * 19
        icon(svg, cx0 + 30, ly - 9, 18)
        text(svg, cx0 + 54, ly + 4, lab, size=FS2, fill=INK2)

    svg.height = dy + dh + 26
    svg.save(OUT)


if __name__ == "__main__":
    main()
