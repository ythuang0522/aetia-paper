#!/usr/bin/env python3
"""Figure 1: overview of AETIA (figures/fig1_overview.svg). Edit this script, not the SVG.

Pictorial schematic in four rows, concept-level labels only (no tier codes, rule counts or
thresholds; those live in Methods and the Supplementary tables):
  a, the patient's record -> seven modality-specific language-model agents -> structured
     evidence per organism;
  b, candidate assembly and rule-based selection: mNGS and conventional-test lanes, candidate
     pool, colonizer guardrails, Picked organisms, language-model safety review that can flag
     but not pick;
  c, one evidence profile per Picked or Flagged organism (literature match, sequencing strength
     and dominance, conventional tests by specimen class, site relevance);
  d, the final rule: Picked organisms are kept; a Flagged organism is added (the rescue rule)
     when the same organism is isolated from a sterile site or tissue, or when literature, site
     and sequencing all agree -> the frozen list -> a clinical rationale written by a language model.
No between-panel connectors (PI, 2026-09-24): panel order, stage headings and the same seven
organisms carried through every panel convey the workflow.
A schematic example carries seven detections through the figure: a bacterium and a virus are
picked; a mould and a mycobacterium are flagged; three are held back by guardrails. In c the
flagged mycobacterium has a pleural-fluid culture, so in d it is rescued through the sterile-site
route; the flagged mould lacks sequencing and site support and is not selected.
Colour semantics (one meaning each, all panels): violet = language model; blue = selected;
orange = mNGS reads; amber = caution / held back / flagged; green = supporting evidence;
red = evidence against; grey = neutral. Key: violet chip = language model, cog = rule.
Panel a keeps seven separate agents on the PI's instruction (2026-09-24); the code's agent specs
(upstream/tools/analyze_llm_agent.py:56-111) group them into five, flagged in Methods. Route labels in d follow the rule_path values in
OBER_patient_delivery/generate_r5_final_decisions.py:17-21,98-116.
Canvas 1000 units = 180 mm (Nature double column); 13 units ~ 6.6 pt; no text below 13.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG  # noqa: E402
import icons as I  # noqa: E402

OUT = HERE.parent / "figures" / "fig1_overview.svg"
W, H = 1000, 1100
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"; HAIR = "#cbd5e1"
BLUE = "#1d4ed8"; BLUE_T = "#dbeafe"; BLUE_E = "#93c5fd"
VIOL = "#6d28d9"; VIOL_T = "#ede9fe"; VIOL_E = "#c4b5fd"
GREEN = "#15803d"; GREEN_T = "#dcfce7"; GREEN_E = "#86efac"
AMBER = "#d97706"; AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
RED = "#b91c1c"
GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"; NONE_DOT = "#d1d5db"
ORANGE = "#f97316"; ORANGE_T = "#fdba74"; ORANGE_BG = "#fff7ed"
FS = 14          # card titles and body labels
FS2 = 13         # secondary labels (the print minimum)
GHOST = "#9ca3af"   # organisms that are set aside


def text(svg, x, y, s, size=FS, fill=INK, anchor="start", weight="normal", style="normal"):
    svg.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight, style=style)


def tw(s, size=FS2, bold=False):
    """Approximate rendered width of a Helvetica label."""
    return len(s) * size * (0.58 if bold else 0.53)


def card(svg, x, y, w, h, fill=GRAY_T, edge=GRAY_E, rx=8):
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.2, rx=rx)


def title(svg, x, y, s, icon=None, size=FS):
    """Card title with an optional 22-unit marker icon at its left."""
    if icon:
        icon(svg, x, y - 16, 22)
        text(svg, x + 28, y, s, size=size, weight="bold")
    else:
        text(svg, x, y, s, size=size, weight="bold")


def pill(svg, cx, cy, label, fill, edge, icon=None, w=None, h=26, size=FS2):
    w = w or tw(label, size) + 24 + (28 if icon else 0)
    svg.rect(cx - w / 2, cy - h / 2, w, h, fill, stroke=edge, sw=1.2, rx=h / 2)
    if icon:
        lw = min(tw(label, size) + 24, w - 12)
        x0 = cx - lw / 2
        icon(svg, x0 - 2, cy - 10, 20)
        text(svg, x0 + 22, cy + size * 0.36, label, size=size)
    else:
        text(svg, cx, cy + size * 0.36, label, size=size, anchor="middle")


def arrow(svg, x1, y1, x2, y2, color=INK2, sw=1.4):
    svg.arrow(x1, y1, x2, y2, stroke=color, sw=sw, head=7)


def curve_arrow(svg, x1, y1, x2, y2, color=INK2, sw=1.4):
    """Horizontal S-curve ending in an arrowhead that points right."""
    mx = (x1 + x2) / 2
    svg.path(f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2 - 7},{y2}", stroke=color, sw=sw)
    svg.add(f'<path d="M{x2 - 8},{y2 - 4.5} L{x2},{y2} L{x2 - 8},{y2 + 4.5} Z" fill="{color}"/>')


def heading(svg, x, y, letter, s):
    svg.text(x, y, letter, size=22, weight="bold", fill=INK)
    text(svg, x + 26, y, s, size=15, fill=INK2)


def ghost(glyph):
    """Grey version of an organism glyph (set aside)."""
    return lambda svg, cx, cy, s: glyph(svg, cx, cy, s, ink=GHOST, fill="#f3f4f6")


def badge(svg, x, y, w, h, s, on):
    """Dominance badge: green 'dominant' or an empty grey dash."""
    card(svg, x, y, w, h, GREEN_T if on else "#ffffff", GREEN_E if on else GRAY_E, rx=4)
    text(svg, x + w / 2, y + h / 2 + 4.5, s if on else "–", size=FS2,
         fill=GREEN if on else MUTED, anchor="middle", weight="bold" if on else "normal")


def main() -> None:
    svg = SVG(W, H)

    # ---------------------------------------------------------------- key --------------------
    # Division of labour plus the organism glyphs used in every panel.
    ky = 30
    kx = 984
    items = [(None, "yeast", I.yeast), (None, "mould", I.fungus), (None, "virus", I.virus),
             (None, "mycobacterium", I.mycobacterium), (None, "bacterium", I.bacterium)]
    for _, lab, g in items:
        kx -= tw(lab)
        text(svg, kx, ky, lab, size=FS2, fill=INK2)
        g(svg, kx - (18 if g is I.bacterium else 13), ky - 5, 20)
        kx -= 44 if g is I.bacterium else 38
    svg.line(kx + 10, ky - 15, kx + 10, ky + 4, stroke=HAIR, sw=1)
    kx -= 14
    for icon, lab in ((I.cog, "Rules"), (I.brain_chip, "LLM")):
        kx -= tw(lab, bold=True)
        text(svg, kx, ky, lab, size=FS2, weight="bold")
        icon(svg, kx - 25, ky - 16, 20)
        kx -= 42

    # ================================================================ a ==========================
    heading(svg, 14, 30, "a", "Evidence extraction")
    # Seven modalities, each read by its own language-model agent (PI's layout, 2026-09-24).
    srcs = [
        ("Chest imaging", "report text", I.xray, "Imaging agent"),
        ("Clinical history", "comorbidities", I.clipboard, "History agent"),
        ("Blood counts", "CRP / labs", I.blood_tube, "Laboratory agent"),
        ("Galactomannan", "antigen", I.well_plate, "Antigen agent"),
        ("Multiplex PCR", "PCR / molecular", I.pcr_box, "PCR agent"),
        ("Cultures", "all specimens", I.petri, "Culture agent"),
        ("mNGS", "reads per organism", I.sequencer, "Analysis agent"),
    ]
    colw = 138; x0 = 16; ytop = 48
    cxs = [x0 + i * colw + colw / 2 for i in range(len(srcs))]
    for (l1, l2, icon, _), cx in zip(srcs, cxs):
        icon(svg, cx - 22, ytop, 44)
        text(svg, cx, ytop + 62, l1, size=FS2, anchor="middle", weight="bold")
        text(svg, cx, ytop + 77, l2, size=FS2, fill=MUTED, anchor="middle")
        arrow(svg, cx, ytop + 83, cx, ytop + 96)
    ya = ytop + 110
    pill_centres = []
    for (_, _, _, lab), cx in zip(srcs, cxs):
        pill(svg, cx, ya, lab, VIOL_T, VIOL_E, icon=I.brain_chip, w=colw - 4)
        pill_centres.append(cx)
    # bus into the structured evidence
    ybus = ya + 24
    for cx in pill_centres:
        svg.line(cx, ya + 13, cx, ybus, stroke=INK2, sw=1.2)
    svg.line(pill_centres[0], ybus, pill_centres[-1], ybus, stroke=INK2, sw=1.2)
    xc = cxs[3]   # the bus drop continues the centre column's line
    arrow(svg, xc, ybus, xc, ybus + 14)
    ex, ew, eh = 90, 820, 52
    ey = ybus + 14
    card(svg, ex, ey, ew, eh)
    I.document(svg, ex + 10, ey + 8, 34)
    text(svg, ex + 50, ey + 31, "Structured evidence", size=FS + 1, weight="bold")
    # Four fields, each drawn with the glyphs that carry it.
    fx0 = ex + 240; fw = (ew - 250) / 4
    fcx = [fx0 + i * fw + fw / 2 for i in range(4)]
    for i in range(1, 4):
        svg.line(fx0 + i * fw, ey + 8, fx0 + i * fw, ey + eh - 8, stroke=HAIR, sw=0.8)
    svg.line(fx0, ey + 8, fx0, ey + eh - 8, stroke=HAIR, sw=0.8)
    # per organism
    I.bacterium(svg, fcx[0] - 20, ey + 17, 15); I.virus(svg, fcx[0], ey + 17, 15)
    I.fungus(svg, fcx[0] + 20, ey + 17, 15)
    text(svg, fcx[0], ey + 44, "each organism", size=FS2, fill=INK2, anchor="middle")
    # support from each source: supports / no support / unknown
    I.check(svg, fcx[1] - 22, ey + 17, 18)
    svg.circle(fcx[1], ey + 17, 4.4, "#ffffff", stroke=MUTED, sw=1.25)
    svg.line(fcx[1] - 2.4, ey + 17, fcx[1] + 2.4, ey + 17, stroke=MUTED, sw=1.25)
    I.unknown(svg, fcx[1] + 22, ey + 17, 18, color=MUTED)
    text(svg, fcx[1], ey + 44, "support per source", size=FS2, fill=INK2, anchor="middle")
    # specimen and site
    I.bottle(svg, fcx[2] - 20, ey + 6, 20); I.site_pin(svg, fcx[2] + 1, ey + 6, 20)
    text(svg, fcx[2], ey + 44, "specimen & site", size=FS2, fill=INK2, anchor="middle")
    # host context
    I.person(svg, fcx[3] - 9, ey + 19, 17); I.shield(svg, fcx[3] + 2, ey + 6, 20)
    text(svg, fcx[3], ey + 44, "host context", size=FS2, fill=INK2, anchor="middle")

    # ================================================================ b ==========================
    yb = ey + eh + 34
    heading(svg, 14, yb, "b", "Candidate assembly and rule-based selection")
    top = yb + 20
    ix, iw = 16, 156
    rules_x, rules_w = 196, 246
    pool_x, pool_w = 468, 168
    guard_x, guard_w = 660, 124
    out_x, out_w = 808, 176
    lane_h = 88; lane_gap = 12

    # mNGS lane (orange = reads)
    m_y = top
    card(svg, ix, m_y, iw, lane_h, ORANGE_BG, ORANGE_T)
    title(svg, ix + 10, m_y + 22, "mNGS report", icon=I.sequencer)
    for j, (glyph, reads) in enumerate(((I.bacterium, 96), (I.virus, 62), (I.yeast, 38))):
        yy = m_y + 42 + j * 15
        glyph(svg, ix + 20, yy, 15)
        svg.rect(ix + 36, yy - 3.5, reads, 7, ORANGE if j == 0 else ORANGE_T, rx=1.5)
    card(svg, rules_x, m_y, rules_w, lane_h)
    title(svg, rules_x + 10, m_y + 22, "Sequencing rules", icon=I.cog)
    for j, label in enumerate(("Read count", "Dominance", "vs controls", "Site match")):
        xx = rules_x + 12 + (j % 2) * 120
        yy = m_y + 34 + (j // 2) * 26
        if j == 0:  # amount of organism sequence
            for k, height in enumerate((6, 11, 17)):
                svg.rect(xx + 2 + k * 7, yy + 19 - height, 5, height, ORANGE, rx=1)
        elif j == 1:  # one organism outweighs the others
            for k, height in enumerate((18, 7, 4)):
                svg.rect(xx + 2 + k * 8, yy + 19 - height, 6, height,
                         ORANGE if k == 0 else ORANGE_T, rx=1)
        elif j == 2:  # signal above the negative controls
            svg.rect(xx + 2, yy + 3, 8, 16, ORANGE, rx=1)
            svg.rect(xx + 14, yy + 13, 8, 6, HAIR, rx=1)
        else:  # organism agrees with the specimen site
            I.site_pin(svg, xx, yy, 21)
        text(svg, xx + 30, yy + 16, label, size=FS2, fill=INK2)
    arrow(svg, ix + iw, m_y + lane_h / 2, rules_x, m_y + lane_h / 2)

    # conventional-test lane (neutral)
    h_y = top + lane_h + lane_gap
    card(svg, ix, h_y, iw, lane_h)
    text(svg, ix + 10, h_y + 22, "Conventional tests", size=FS, weight="bold")
    for j, (icon, label) in enumerate(((I.petri, "culture"), (I.pcr_box, "PCR"), (I.well_plate, "GM"))):
        cx = ix + 30 + j * 48
        icon(svg, cx - 14, h_y + 30, 28)
        text(svg, cx, h_y + 76, label, size=FS2, fill=INK2, anchor="middle")
    card(svg, rules_x, h_y, rules_w, lane_h)
    title(svg, rules_x + 10, h_y + 22, "Direct-test rules", icon=I.cog)
    svg.line(rules_x + 118, h_y + 34, rules_x + 118, h_y + 80, stroke=HAIR, sw=0.8)
    for k, height in enumerate((9, 16, 25)):
        svg.rect(rules_x + 30 + k * 16, h_y + 62 - height, 11, height,
                 ("#d1d5db", "#9ca3af", INK2)[k], rx=2)
    text(svg, rules_x + 60, h_y + 80, "Assay strength", size=FS2, fill=INK2, anchor="middle")
    I.bottle(svg, rules_x + 140, h_y + 34, 28, growth=True)
    arrow(svg, rules_x + 170, h_y + 48, rules_x + 188, h_y + 48)
    I.site_pin(svg, rules_x + 190, h_y + 34, 28)
    text(svg, rules_x + 182, h_y + 80, "Specimen & site", size=FS2, fill=INK2, anchor="middle")
    arrow(svg, ix + iw, h_y + lane_h / 2, rules_x, h_y + lane_h / 2)

    # candidate pool: both lanes merge before the common guardrails
    pool_h = 118; pool_y = top + (2 * lane_h + lane_gap - pool_h) / 2
    card(svg, pool_x, pool_y, pool_w, pool_h)
    title(svg, pool_x + 10, pool_y + 22, "Candidate pool", icon=I.cog)
    # seven example detections: two picked, two flagged, three held back
    pool_glyphs = (I.bacterium, I.virus, I.fungus, I.mycobacterium, I.yeast, I.bacterium, I.virus)
    for j, glyph in enumerate(pool_glyphs):
        gx = pool_x + (27 + j * 38 if j < 4 else 46 + (j - 4) * 38)
        gy_ = pool_y + (58 if j < 4 else 96)
        glyph(svg, gx, gy_, 27)
    curve_arrow(svg, rules_x + rules_w, m_y + lane_h / 2, pool_x, pool_y + 40)
    curve_arrow(svg, rules_x + rules_w, h_y + lane_h / 2, pool_x, pool_y + pool_h - 30)

    # guardrails (amber = caution)
    gy, gh = pool_y, pool_h
    card(svg, guard_x, gy, guard_w, gh, AMBER_T, AMBER_E)
    title(svg, guard_x + 10, gy + 22, "Guardrails", icon=I.cog)
    text(svg, guard_x + guard_w / 2, gy + 44, "held back", size=FS2, fill=INK2, anchor="middle")
    for j, glyph in enumerate((I.yeast, I.bacterium, I.virus)):
        gx = guard_x + 26 + j * 36
        ghost(glyph)(svg, gx, gy + 84, 26)
        I.cross(svg, gx + 10, gy + 100, 14)
    arrow(svg, pool_x + pool_w, pool_y + pool_h / 2, guard_x, gy + gh / 2)

    # Picked (blue = selected)
    pick_y = top
    card(svg, out_x, pick_y, out_w, lane_h, BLUE_T, BLUE_E)
    title(svg, out_x + 10, pick_y + 22, "Picked", icon=I.cog)
    text(svg, out_x + 10, pick_y + 42, "selected by rules", size=FS2, fill=INK2)
    for j, glyph in enumerate((I.bacterium, I.virus)):
        gx = out_x + 28 + j * 60
        glyph(svg, gx, pick_y + 66, 24)
        I.check(svg, gx + 26, pick_y + 66, 15)
    curve_arrow(svg, guard_x + guard_w, gy + 34, out_x, pick_y + lane_h / 2 + 8)

    # Flagged: the language-model safety review sees unpicked organisms, never picks
    review_y = h_y
    card(svg, out_x, review_y, out_w, lane_h, VIOL_T, VIOL_E)
    title(svg, out_x + 10, review_y + 22, "Flagged", icon=I.brain_chip)
    text(svg, out_x + 10, review_y + 42, "LLM review of unpicked", size=FS2, fill=INK2)
    for j, glyph in enumerate((I.fungus, I.mycobacterium)):
        gx = out_x + 28 + j * 60
        glyph(svg, gx, review_y + 66, 24)
        I.flag(svg, gx + 26, review_y + 66, 15)
    curve_arrow(svg, guard_x + guard_w, gy + gh - 34, out_x, review_y + lane_h / 2 - 8, color=VIOL)


    # ================================================================ c ==========================
    # Evidence matrix: one row per carried organism, one column per evidence source. Column
    # headers are legends for the cells below; no column makes a decision.
    yc = review_y + lane_h + 40
    heading(svg, 14, yc, "c", "Evidence profile for each Picked or Flagged organism")
    ccy = yc + 14
    hdr_h = 112; row_h = 30; nrow = 4
    cols = {"lit": (128, 300), "seq": (436, 140), "dir": (584, 206), "site": (798, 186)}
    rows_y0 = ccy + hdr_h + 12

    # ---- Literature match: PubMed reports compared with this patient, one verdict per article
    x, w = cols["lit"]
    card(svg, x, ccy, w, hdr_h, VIOL_T, VIOL_E)
    title(svg, x + 10, ccy + 22, "Literature match", icon=I.brain_chip)
    for k in range(3):
        I.document(svg, x + 8 + k * 7, ccy + 34 + k * 4, 34)
    text(svg, x + 33, ccy + 102, "PubMed", size=FS2, fill=INK2, anchor="middle", weight="bold")
    text(svg, x + 72, ccy + 74, "+", size=FS + 5, fill=VIOL, anchor="middle", weight="bold")
    I.person(svg, x + 100, ccy + 66, 36)
    for k, (icon, lab) in enumerate(((I.site_pin, "site"), (I.shield, "host"), (I.clock, "timing"))):
        icon(svg, x + 124, ccy + 32 + k * 21, 18)
        text(svg, x + 144, ccy + 46 + k * 21, lab, size=FS2, fill=INK2)
    text(svg, x + 98, ccy + 102, "patient", size=FS2, fill=INK2, anchor="middle", weight="bold")
    arrow(svg, x + 190, ccy + 70, x + 206, ccy + 70, color=VIOL)
    for k, (col, lab) in enumerate(((GREEN, "strong"), (AMBER, "partial"),
                                    (RED, "mismatch"), (NONE_DOT, "insufficient"))):
        yy = ccy + 44 + k * 19
        svg.circle(x + 216, yy - 4.5, 5, col)
        text(svg, x + 227, yy, lab, size=FS2, fill=INK2)

    # ---- Sequencing: read count (bar) and dominance over the next organism (badge)
    x, w = cols["seq"]
    card(svg, x, ccy, w, hdr_h)
    title(svg, x + 10, ccy + 22, "Sequencing", icon=I.cog)
    svg.rect(x + 10, ccy + 48, 44, 10, "#ffffff", stroke=GRAY_E, sw=0.8, rx=2)
    svg.rect(x + 10, ccy + 48, 34, 10, ORANGE, rx=2)
    text(svg, x + 32, ccy + 78, "reads", size=FS2, fill=INK2, anchor="middle")
    badge(svg, x + 60, ccy + 42, 72, 22, "dominant", True)
    text(svg, x + 96, ccy + 78, "lead", size=FS2, fill=INK2, anchor="middle")
    text(svg, x + w / 2, ccy + 100, "over next organism", size=FS2, fill=MUTED, anchor="middle")

    # ---- Conventional tests: the specimen class matters, not only the result
    x, w = cols["dir"]
    card(svg, x, ccy, w, hdr_h)
    title(svg, x + 10, ccy + 22, "Conventional tests", icon=I.cog)
    sw_ = (w - 24) / 2
    card(svg, x + 8, ccy + 34, sw_, 70, "#ffffff", GRAY_E, rx=6)
    I.petri(svg, x + 14, ccy + 40, 30); I.pcr_box(svg, x + 50, ccy + 40, 30)
    text(svg, x + 8 + sw_ / 2, ccy + 94, "airway", size=FS2, fill=INK2, anchor="middle")
    card(svg, x + 16 + sw_, ccy + 34, sw_, 70, GREEN_T, GREEN_E, rx=6)
    I.petri(svg, x + 16 + sw_ + sw_ / 2 - 15, ccy + 40, 30)
    text(svg, x + 16 + sw_ + sw_ / 2, ccy + 94, "sterile site", size=FS2, fill=GREEN,
         anchor="middle", weight="bold")

    # ---- Site relevance: recorded for the final rule and for review, not a veto by itself
    x, w = cols["site"]
    card(svg, x, ccy, w, hdr_h)
    title(svg, x + 10, ccy + 22, "Site relevance", icon=I.cog)
    for k, (mark, lab) in enumerate(((I.check, "site fits"), (I.unknown, "possible colonizer"),
                                     (I.cross, "wrong site"))):
        yy = ccy + 48 + k * 22
        mark(svg, x + 20, yy - 4.5, 17)
        text(svg, x + 36, yy, lab, size=FS2, fill=INK2)

    # ---- rows: one evidence profile per Picked or Flagged organism
    G, A, N = GREEN, AMBER, NONE_DOT
    example = [
        # glyph, picked?, article verdicts, read-bar fraction, dominant?, test, site
        (I.bacterium, True, [G, G, G, A] + [N] * 6, 0.92, True, ("airway", "sputum culture"), "fits"),
        (I.virus, True, [G, A, A] + [N] * 7, 0.60, False, ("airway", "BAL PCR"), "fits"),
        (I.fungus, False, [G, G, A, A, A] + [N] * 5, 0.30, False, (None, "none"), "colonizer"),
        (I.mycobacterium, False, [A] + [N] * 9, 0.18, False, ("sterile", "pleural culture"), "fits"),
    ]
    for r, (g, picked, verd, frac, dom, (cls, test), site) in enumerate(example):
        ry = rows_y0 + r * row_h; ym = ry + row_h / 2
        if r:
            svg.line(16, ry, W - 16, ry, stroke=GRAY_E, sw=0.8)
        g(svg, 34, ym, 21)
        (I.check if picked else I.flag)(svg, 58, ym, 15)
        text(svg, 70, ym + 4.5, "picked" if picked else "flagged", size=FS2, fill=INK2)
        x, w = cols["lit"]
        for k, col in enumerate(verd):
            svg.circle(x + 16 + k * 19, ym, 5.5, col)
        x, w = cols["seq"]
        svg.rect(x + 10, ym - 5, 44, 10, "#ffffff", stroke=GRAY_E, sw=0.8, rx=2)
        svg.rect(x + 10, ym - 5, 44 * frac, 10, ORANGE, rx=2)
        badge(svg, x + 60, ym - 11, 72, 22, "dominant", dom)
        x, w = cols["dir"]
        if cls == "sterile":
            card(svg, x + 8, ym - 12, w - 16, 24, GREEN_T, GREEN_E, rx=5)
            I.petri(svg, x + 13, ym - 10, 20)
            text(svg, x + 38, ym + 4.5, test, size=FS2, fill=GREEN, weight="bold")
        elif cls == "airway":
            (I.petri if "culture" in test else I.pcr_box)(svg, x + 13, ym - 10, 20)
            text(svg, x + 38, ym + 4.5, test, size=FS2, fill=INK2)
        else:
            text(svg, x + 38, ym + 4.5, "no matching test", size=FS2, fill=MUTED)
        x, w = cols["site"]
        if site == "fits":
            I.check(svg, x + 20, ym, 17); lab = "site fits"
        else:
            I.unknown(svg, x + 20, ym, 17); lab = "possible colonizer"
        text(svg, x + 36, ym + 4.5, lab, size=FS2, fill=INK2)
    svg.rect(16, rows_y0 - 6, W - 32, nrow * row_h + 12, "none", stroke=INK2, sw=1, rx=6)

    # ================================================================ d ==========================
    # Final selection. Picked organisms are kept; a Flagged organism is rescued by one of two
    # routes (rule_path picked / C3_direct / A1_site_B in
    # OBER_patient_delivery/generate_r5_final_decisions.py:17-21,98-116). The example follows
    # the rows of c: the pleural-culture mycobacterium passes route 2; the mould fails route 3.
    yd = rows_y0 + nrow * row_h + 6 + 40
    heading(svg, 14, yd, "d", "Final selection, then clinical rationale")
    dy = yd + 18
    LH = (50, 56, 72); LGAP = 8
    dh = sum(LH) + 2 * LGAP
    lx, lw = 16, 402
    lane_y = (dy, dy + LH[0] + LGAP, dy + LH[0] + LH[1] + 2 * LGAP)
    lane_mid = tuple(ly + h / 2 for ly, h in zip(lane_y, LH))

    # ---- route 1: picked organisms are kept
    y = lane_y[0]
    card(svg, lx, y, lw, LH[0], BLUE_T, BLUE_E)
    I.check(svg, lx + 19, y + 25, 25)
    text(svg, lx + 38, y + 21, "Picked by the rules", size=FS2, weight="bold")
    text(svg, lx + 38, y + 39, "kept", size=FS2, fill=INK2)
    I.bacterium(svg, lx + 330, y + 25, 22); I.virus(svg, lx + 368, y + 25, 22)

    # ---- route 2: the same organism isolated from a sterile site or tissue
    y = lane_y[1]
    card(svg, lx, y, lw, LH[1])
    I.flag(svg, lx + 19, y + 28, 25)
    text(svg, lx + 38, y + 21, "Flagged + same organism from a sterile site", size=FS2, weight="bold")
    card(svg, lx + 38, y + 29, 170, 22, GREEN_T, GREEN_E, rx=5)
    I.petri(svg, lx + 42, y + 30, 20)
    text(svg, lx + 66, y + 45, "pleural culture", size=FS2, fill=GREEN, weight="bold")
    I.mycobacterium(svg, lx + 334, y + 42, 22); I.check(svg, lx + 360, y + 40, 16)
    text(svg, lx + 372, y + 45, "met", size=FS2, fill=GREEN, weight="bold")

    # ---- route 3: literature, site and sequencing all agree
    y = lane_y[2]
    card(svg, lx, y, lw, LH[2])
    I.flag(svg, lx + 19, y + 24, 25)
    text(svg, lx + 38, y + 20, "Flagged + literature, site and sequencing agree", size=FS2, weight="bold")
    cx3 = lx + 38
    for k2, (cw3, label) in enumerate(((96, "literature"), (70, "site"), (96, "sequencing"))):
        card(svg, cx3, y + 28, cw3, 38, "#ffffff", GRAY_E, rx=6)
        mid = cx3 + cw3 / 2
        if k2 == 0:
            for j, col in enumerate((GREEN, GREEN, AMBER)):
                svg.circle(mid + (j - 1) * 14, y + 38, 4.6, col)
        elif k2 == 1:
            I.site_pin(svg, mid - 9, y + 29, 18)
        else:
            for k3, hgt in enumerate((6, 11, 16)):
                svg.rect(mid - 11 + k3 * 8, y + 45 - hgt, 6, hgt, ORANGE, rx=1)
        text(svg, mid, y + 60, label, size=FS2, fill=INK2, anchor="middle")
        if k2 < 2:
            text(svg, cx3 + cw3 + 5, y + 51, "+", size=FS + 3, fill=INK2, anchor="middle", weight="bold")
        cx3 += cw3 + 10
    ghost(I.fungus)(svg, lx + 336, y + 44, 24); I.cross(svg, lx + 360, y + 44, 16)
    text(svg, lx + 372, y + 49, "not", size=FS2, fill=RED, weight="bold")
    text(svg, lx + 372, y + 63, "met", size=FS2, fill=RED, weight="bold")

    # ---- the three routes join at the final-list rule
    # three S-curves (the connector style of b) merge into one arrowhead at the rule cog
    bx = lx + lw + 14; gmid = dy + dh / 2
    jx = bx + 26                     # merge point
    for cy_ in lane_mid:
        svg.path(f"M{lx + lw},{cy_} C{lx + lw + 26},{cy_} {lx + lw + 26},{gmid} {jx},{gmid}",
                 stroke=INK2, sw=1.4)
    svg.add(f'<path d="M{jx},{gmid - 4.5} L{jx + 8},{gmid} L{jx},{gmid + 4.5} Z" fill="{INK2}"/>')
    I.cog(svg, jx + 9, gmid - 12, 24)
    arrow(svg, jx + 37, gmid, bx + 102, gmid)

    # ---- the list, frozen before any text is written
    fx = bx + 104; fw = 150
    card(svg, fx, dy, fw, dh, BLUE_T, BLUE_E)
    title(svg, fx + 10, dy + 24, "Final list", icon=I.lock)
    row1 = dy + 60
    svg.rect(fx + 8, row1 - 14, fw - 16, 28, "#ffffff", stroke=BLUE, sw=1.4, rx=8)
    final = [(I.bacterium, "selected", True), (I.virus, "selected", True),
             (I.mycobacterium, "rescued", True), (I.fungus, "not selected", False)]
    for j, (g, lab, sel) in enumerate(final):
        yy = row1 + j * 37
        (g if sel else ghost(g))(svg, fx + 26, yy, 22)
        text(svg, fx + 46, yy + 4.5, lab, size=FS2, fill=BLUE if sel else MUTED,
             weight="bold" if sel else "normal")

    # ---- clinical rationale: a language-model step that starts only after the list is fixed.
    # The organism is the prototype K. pneumoniae vignette of Fig. 3e (schematic, no values).
    cx0 = fx + fw + 20; cw = W - 16 - cx0
    card(svg, cx0, dy, cw, dh, VIOL_T, VIOL_E)
    title(svg, cx0 + 10, dy + 24, "Clinical rationale", icon=I.brain_chip)
    svg.arrow(fx + fw - 8, row1, cx0 + 9, row1, stroke=BLUE, sw=1.4, head=7)   # head stops at the row's edge
    card(svg, cx0 + 10, row1 - 14, cw - 20, 28, "#ffffff", VIOL_E, rx=8)
    I.bacterium(svg, cx0 + 30, row1, 22)
    text(svg, cx0 + 48, row1 + 4.5, "K. pneumoniae", size=FS2, weight="bold", style="italic")
    svg.rect(cx0 + cw - 92, row1 - 10, 74, 20, BLUE_T, stroke=BLUE_E, sw=1.1, rx=10)
    text(svg, cx0 + cw - 55, row1 + 4.5, "selected", size=FS2, fill=BLUE, anchor="middle", weight="bold")
    for k, (icon, lab) in enumerate(((I.sequencer, "dominant in BAL"),
                                     (I.petri, "BAL culture positive"),
                                     (I.xray, "new consolidation"),
                                     (I.blood_tube, "inflammation rising"))):
        yy = row1 + 36 + k * 27
        icon(svg, cx0 + 20, yy - 10, 20)
        text(svg, cx0 + 48, yy + 4.5, lab, size=FS2, fill=INK2)
        I.check(svg, cx0 + cw - 26, yy, 15)

    svg.height = dy + dh + 16
    svg.save(OUT)


if __name__ == "__main__":
    main()
