#!/usr/bin/env python3
"""Figure 3: what no single read-out can say, and the cases in which the record says it
(figures/fig3_explanation.svg).

Fifth design, 2026-09-21 (PI: "panel a reads like methodology instead of results; use the 32 KMUH
admissions as the denominator").  Panel a is one wide panel built from the KMUH per-patient source
workbooks (tables/make_kmuh_record.py -> kmuh_record.csv), describing the study cohort's own records:
  a1 what one admission leaves behind -- the median admission's results as one square each, coloured by
     modality, with the mNGS report as a single blue square; below, the record span, the days that carry
     a new result and the free-text word count
  a2 the organisms that record names -- the median count per admission and three overlapping read-out
     sets (culture, panel/galactomannan, mNGS) over the organism-admission pairs, with the share named
     by one read-out only and the share that never grew from a sterile site
  a3 what the other read-outs settle -- the chest report names pneumonia but hedges it; a culture reports
     no growth twice as slowly as growth; a resistance marker arrives with no organism attached
  b-d  three worked cases drawn as evidence trails: for each organism a row of chips, one per read-out that the
     record cites (icon + result glyph + a two-word label), tinted by what it does to the call (supports /
     argues against / context or absent / rule), ending in the frozen decision
     b  colonization or infection: K. pneumoniae selected and C. albicans set aside from one lavage specimen
     c  the same yeast and the same guardrail, the opposite call: C. tropicalis with blood cultures growing it
     d  the pathogen the sequenced specimen did not contain: Chlamydophila pneumoniae by IgM, lavage report
        negative -- a registry case, disposition drawn from the serology rule as implemented (todo: replace with
        the delivered record)
  e  every candidate leaves with a disposition (518 -> 123 selected, 395 set aside with a reason)
Numbers in a and e come from figures-source/discordance_summary.json, discordance.csv and sampling.csv
(tables/make_discordance.py, verified=yes) and docs/VALIDATION.md; case content of b, c is the two prototype
vignettes of the 2026-01-17 talk
(regenerate from the delivered records before submission).  Edit this script, not the SVG.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG, read_csv  # noqa: E402
import icons as I  # noqa: E402

OUT = HERE.parent / "figures" / "fig3_explanation.svg"
W = 1000
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"; HAIR = "#d1d5db"; GHOST = "#9ca3af"
GREEN = "#15803d"; GREEN_T = "#dcfce7"; GREEN_E = "#86bf9e"
RED = "#b91c1c"; RED_T = "#fee2e2"; RED_E = "#f0a9a7"
AMBER = "#b45309"; AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
BLUE = "#2a78d6"; BLUE_D = "#1d4ed8"; BLUE_T = "#dbeafe"
ORANGE = "#eb6834"; TEAL = "#0f766e"
GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"
FS = 13; FS2 = 12; FS3 = 11          # nothing below 11 units
C_SEQ = "#c2410c"; C_LAB = "#0f766e"; C_CLIN = "#7c6bd0"; C_LIT = "#b45309"

SUMMARY = json.loads((HERE / "discordance_summary.json").read_text())
DETECTIONS = read_csv(HERE / "discordance.csv")
SAMPLING = {r["lane"]: r for r in read_csv(HERE / "sampling.csv")}
RECORD = {r["metric"]: r for r in read_csv(HERE / "kmuh_record.csv")}
ADMISSIONS = read_csv(HERE / "kmuh_admissions.csv")
LATENCY = read_csv(HERE / "kmuh_latency.csv")
AXIS_C = "#b6bcc6"
svg_ = None   # the SVG being drawn; set in main()


def num(lane, field):
    """One aggregate from sampling.csv (tables/make_discordance.py); never a typed-in number."""
    return float(SAMPLING[lane][field])


def text(svg, x, y, s, size=FS, fill=INK, anchor="start", weight="normal", style="normal",
         baseline="alphabetic", rotate=None):
    svg.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight, style=style,
             baseline=baseline, rotate=rotate)


def heading(svg, x, y, letter, title):
    svg.text(x, y, letter, size=22, weight="bold", fill=INK)
    text(svg, x + 26, y, title, size=15, fill=INK2)


_clip = [0]


def clipped(svg, x, y, w, h, draw):
    """Run draw() inside a rectangular clip."""
    _clip[0] += 1
    cid = f"clip{_clip[0]}"
    svg.add(f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath>')
    svg.add(f'<g clip-path="url(#{cid})">')
    draw()
    svg.add("</g>")


# ---- panels a-c: the record these decisions are made from -----------------------------------------
# Fifth design, 2026-09-21 (PI: "not Nature or NEJM style"): the three statements of the old folded
# panel are drawn as three ordinary statistical graphics, one per panel letter, with axes, units and
# every admission plotted -- no display numerals, pictograms or callouts.  Data: the 32 KMUH admissions
# (figures-source/kmuh_admissions.csv, kmuh_latency.csv, kmuh_record.csv; tables/make_kmuh_record.py).
import math

MOD_ROWS = [("Chemistry, blood gas", "chemistry"), ("Blood counts", "blood_counts"),
            ("Panel targets", "panel_targets"), ("Imaging studies", "imaging_studies"),
            ("Culture reports", "culture_reports"), ("Galactomannan assays", "galactomannan"),
            ("  mNGS reports", "mngs_reports")]
SEG = [("organisms_1_readout", "#cbd5e1", "1"), ("organisms_2_readouts", "#7f9fc9", "2"),
       ("organisms_3_readouts", BLUE, "3")]


def kv(metric, field="value"):
    return float(RECORD[metric][field])


def med_iqr(xs):
    xs = sorted(xs)
    def qq(p):
        i = p * (len(xs) - 1); lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return qq(0.5), qq(0.25), qq(0.75)


def panel_results(svg, x, y, w, h):
    """a: results per admission, by modality; every admission plotted, log axis."""
    heading(svg, x, y, "a", "Results per admission, by modality")
    lab_w = 108
    x0, x1 = x + lab_w, x + w - 8
    lo, hi = 0.8, 420.0
    def sx(v):
        v = max(v, lo)
        return x0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)
    y0 = y + 26
    step = 17
    for t in (1, 3, 10, 30, 100, 300):
        svg.line(sx(t), y0 - 4, sx(t), y0 + len(MOD_ROWS) * step - 4, stroke="#eceef2", sw=0.8)
    for i, (lab, key) in enumerate(MOD_ROWS):
        cy = y0 + i * step + 6
        vals = [int(a[key]) for a in ADMISSIONS]
        col = BLUE if key == "mngs_reports" else "#9ca3af"
        text(svg, x0 - 8, cy + 3, lab, size=FS3, fill=INK2, anchor="end")
        for j, v in enumerate(vals):
            jitter = ((j * 7919) % 11 - 5) * 0.62
            if v <= 0:
                svg.circle(sx(lo), cy + jitter, 1.9, "#ffffff", stroke=col, sw=0.9)
            else:
                svg.add(f'<circle cx="{sx(v):.2f}" cy="{cy + jitter:.2f}" r="1.9" fill="{col}" opacity="0.55"/>')
        m, q1, q3 = med_iqr(vals)          # zeros included, as in kmuh_record.csv
        svg.line(sx(q1), cy, sx(q3), cy, stroke=INK, sw=0.9)
        svg.line(sx(m), cy - 6, sx(m), cy + 6, stroke=INK, sw=1.8)
    ay = y0 + len(MOD_ROWS) * step - 2
    svg.line(x0, ay, x1, ay, stroke=AXIS_C, sw=0.9)
    for t in (1, 3, 10, 30, 100, 300):
        svg.line(sx(t), ay, sx(t), ay + 3.5, stroke=AXIS_C, sw=0.9)
        text(svg, sx(t), ay + 15, str(t), size=FS3, fill=MUTED, anchor="middle")
    text(svg, (x0 + x1) / 2, ay + 30, "results per admission (log scale)", size=FS3, fill=INK2, anchor="middle")
    text(svg, x, ay + 46, "one dot per admission (n = 32); bar, median; line, interquartile range;",
         size=FS3, fill=MUTED)
    text(svg, x, ay + 58, "open dot on the axis, none recorded", size=FS3, fill=MUTED)
    return ay + 58


def panel_organisms(svg, x, y, w, h):
    """b: organisms named per admission, split by how many read-outs named each."""
    heading(svg, x, y, "b", "Organisms named per admission")
    x0, x1 = x + 26, x + w - 6
    y1 = y + 26
    ymax = 18
    y_base = y1 + 118
    def sy(v):
        return y_base - v / ymax * 118
    for t in (0, 5, 10, 15):
        svg.line(x0, sy(t), x1, sy(t), stroke="#eceef2", sw=0.8)
        text(svg, x0 - 6, sy(t) + 3, str(t), size=FS3, fill=MUTED, anchor="end")
    n = len(ADMISSIONS)
    slot = (x1 - x0) / n
    bw = slot * 0.72
    for j, a in enumerate(ADMISSIONS):
        base = 0.0
        for key, col, _ in SEG:
            v = int(a[key])
            if v:
                svg.rect(x0 + j * slot + (slot - bw) / 2, sy(base + v), bw, sy(base) - sy(base + v), col)
                base += v
    svg.line(x0, y_base, x1, y_base, stroke=AXIS_C, sw=0.9)
    text(svg, x0 - 22, (sy(0) + sy(ymax)) / 2, "organisms", size=FS3, fill=INK2, anchor="middle", rotate=-90)
    text(svg, (x0 + x1) / 2, y_base + 16, "admissions, ordered by organisms named", size=FS3, fill=INK2, anchor="middle")
    ly = y_base + 34
    text(svg, x0, ly, "named by", size=FS3, fill=MUTED)
    cx = x0 + 54
    for key, col, lab in SEG:
        svg.rect(cx, ly - 8, 9, 9, col, rx=1.5)
        text(svg, cx + 12, ly, lab, size=FS3, fill=INK2)
        cx += 28
    text(svg, cx - 8, ly, "read-outs", size=FS3, fill=INK2)
    text(svg, x, ly + 18, f"{kv('organisms_single_readout_pct'):.0f}% of the "
                          f"{kv('organism_admission_pairs'):.0f} organism–admission pairs were named by one",
         size=FS3, fill=MUTED)
    text(svg, x, ly + 30, f"read-out only; {kv('organisms_no_sterile_site_pct'):.0f}% never grew from a sterile-site culture",
         size=FS3, fill=MUTED)
    return ly + 30


def panel_latency(svg, x, y, w, h):
    """c: time from collection to the final culture report, by outcome."""
    heading(svg, x, y, "c", "Time to the final culture report")
    x0, x1 = x + 30, x + w - 8
    y1 = y + 26
    y_base = y1 + 112
    xmax = 20.0
    def sx(d):
        return x0 + min(d, xmax) / xmax * (x1 - x0)
    def sy(p):
        return y_base - p / 100 * 112
    for t in (0, 25, 50, 75, 100):
        svg.line(x0, sy(t), x1, sy(t), stroke="#eceef2", sw=0.8)
        text(svg, x0 - 6, sy(t) + 3, str(t), size=FS3, fill=MUTED, anchor="end")
    series = [("growth", BLUE, "grew an organism"), ("no growth", ORANGE, "no growth")]
    for outcome, col, lab in series:
        days = sorted(float(r["hours"]) / 24 for r in LATENCY if r["outcome"] == outcome)
        n = len(days)
        pts = [(0.0, 0.0)]
        for i, d in enumerate(days, 1):
            pts.append((d, 100 * i / n))
        path = f"M{sx(pts[0][0]):.2f},{sy(pts[0][1]):.2f}"
        for (dx_, py) in pts[1:]:
            path += f" H{sx(dx_):.2f} V{sy(py):.2f}"
        svg.path(path, stroke=col, sw=1.8)
        med = days[len(days) // 2]
        svg.line(sx(med), sy(0), sx(med), sy(50), stroke=col, sw=0.9, dash="3 3")
        svg.line(x0, sy(50), sx(med), sy(50), stroke="#d1d5db", sw=0.8, dash="3 3")
        text(svg, sx(med), y_base + 26, f"{med:.0f} d", size=FS3, fill=col, anchor="middle", weight="bold")
        ly_lab = sy(32) if outcome == "growth" else sy(16)      # both labels clear of both curves
        svg.line(sx(6.6), ly_lab - 3.5, sx(7.8), ly_lab - 3.5, stroke=col, sw=1.8)
        text(svg, sx(8.2), ly_lab, f"{lab} (n = {n})", size=FS3, fill=col)
    svg.line(x0, y_base, x1, y_base, stroke=AXIS_C, sw=0.9)
    for t in (0, 5, 10, 15, 20):
        svg.line(sx(t), y_base, sx(t), y_base + 3.5, stroke=AXIS_C, sw=0.9)
        text(svg, sx(t), y_base + 14, str(t), size=FS3, fill=MUTED, anchor="middle")
    text(svg, (x0 + x1) / 2, y_base + 40, "days from collection", size=FS3, fill=INK2, anchor="middle")
    text(svg, x0 - 22, (sy(0) + sy(100)) / 2, "reports issued (%)", size=FS3, fill=INK2, anchor="middle", rotate=-90)
    text(svg, x, y_base + 58, "median dashed; a culture takes twice as long to report", size=FS3, fill=MUTED)
    text(svg, x, y_base + 70, "no growth as it takes to report growth", size=FS3, fill=MUTED)
    return y_base + 70


def panel_imaging(svg, x, y, w):
    """d: what a chest study actually says about pneumonia, as shares of all chest studies."""
    heading(svg, x, y, "d", "What the chest report says")
    segs = [("chest_class_hedged_pct", ORANGE, "names pneumonia, qualified"),
            ("chest_class_stated_pct", "#9ca3af", "names pneumonia, unqualified"),
            ("chest_class_none_pct", "#dfe3e8", "no pneumonia term")]
    bx0, bx1 = x + 4, x + w - 200
    by, bh = y + 24, 17
    cx = bx0
    for metric, col, _lab in segs:
        v = kv(metric)
        seg = (bx1 - bx0) * v / 100
        svg.rect(cx, by, seg, bh, col)
        text(svg, cx + seg / 2, by + 12, f"{v:.0f}%", size=FS3,
             fill="#ffffff" if col != "#dfe3e8" else INK2, anchor="middle", weight="bold")
        cx += seg
    svg.line(bx0, by + bh + 4, bx1, by + bh + 4, stroke=AXIS_C, sw=0.9)
    for t in (0, 25, 50, 75, 100):
        tx = bx0 + (bx1 - bx0) * t / 100
        svg.line(tx, by + bh + 4, tx, by + bh + 7.5, stroke=AXIS_C, sw=0.9)
        text(svg, tx, by + bh + 18, str(t), size=FS3, fill=MUTED, anchor="middle")
    text(svg, (bx0 + bx1) / 2, by + bh + 32, "% of chest studies", size=FS3, fill=INK2, anchor="middle")
    lx = bx1 + 18
    for j, (metric, col, lab) in enumerate(segs):
        yy = by - 4 + j * 15
        svg.rect(lx, yy - 8, 9, 9, col, rx=1.5)
        text(svg, lx + 14, yy, lab, size=FS3, fill=INK2)
    text(svg, lx, by + bh + 32, f"{kv('chest_studies'):.0f} chest studies; qualified means the finding is "
                                f"hedged", size=FS3, fill=MUTED)
    text(svg, lx, by + bh + 44, "(probably, suspect, favour, cannot be excluded)", size=FS3, fill=MUTED)
    return by + bh + 44


def panel_a(svg, y):
    b1 = panel_results(svg, 14, y, 320, 0)
    b2 = panel_organisms(svg, 372, y, 294, 0)
    b3 = panel_latency(svg, 706, y, 280, 0)
    return panel_imaging(svg, 14, max(b1, b2, b3) + 24, 760) + 6


# ---- evidence chips ----------------------------------------------------------------------------
CW, CH = 84, 64
TINT = {"S": (GREEN_T, GREEN_E), "X": (RED_T, RED_E), "C": (GRAY_T, GRAY_E), "R": (AMBER_T, AMBER_E), "V": (RED_T, GREEN)}


def chip(svg, x, y, verdict, icon, glyph, l1, l2=""):
    fill, edge = TINT[verdict]
    svg.rect(x, y, CW, CH, fill, stroke=edge, sw=2.2 if verdict == "V" else 1.0, rx=8)
    icon(x + 5, y + 5)
    glyph(x + 36, y + 6)
    badge = {"S": I.check, "X": I.cross, "R": I.flag, "V": I.check}.get(verdict)
    if badge:
        badge(svg, x + CW - 9, y + 9, 16)
    text(svg, x + CW / 2, y + 47, l1, size=FS3, fill=INK, anchor="middle")
    text(svg, x + CW / 2, y + 59, l2, size=FS3, fill=INK2, anchor="middle")


# result glyphs (a 44 x 30 box whose top-left corner is gx, gy)
def g_reads(frac, color=C_SEQ):
    def draw(gx, gy):
        svg_.rect(gx, gy + 9, 40, 10, "#ffffff", stroke=HAIR, sw=1, rx=3)
        svg_.rect(gx, gy + 9, max(4, 40 * frac), 10, color, stroke="none", rx=3)
    return draw


def g_bar_pair(top, runner, color=C_SEQ):
    """Top organism versus runner-up (dominance)."""
    def draw(gx, gy):
        svg_.rect(gx, gy + 4, 40 * top, 8, color, stroke="none", rx=2)
        svg_.rect(gx, gy + 16, 40 * runner, 8, GHOST, stroke="none", rx=2)
    return draw


def g_lungs(shaded=True, effusion=True):
    def draw(gx, gy):
        for sgn in (-1, 1):
            cx = gx + 20 + sgn * 9
            svg_.add(f'<ellipse cx="{cx:.1f}" cy="{gy + 15:.1f}" rx="8" ry="13" fill="#ffffff" stroke="{INK2}" stroke-width="1.4"/>')
            if shaded:
                svg_.add(f'<ellipse cx="{cx + sgn * 1:.1f}" cy="{gy + 12:.1f}" rx="5" ry="6" fill="{C_CLIN}" opacity="0.55"/>')
            if effusion:
                svg_.path(f"M{cx - 7},{gy + 24} Q{cx},{gy + 20} {cx + 7},{gy + 24}", stroke=C_CLIN, sw=2.2)
    return draw


def g_spark(peak=True):
    def draw(gx, gy):
        svg_.line(gx, gy + 26, gx + 40, gy + 26, stroke=HAIR, sw=1)
        d = f"M{gx},{gy + 22} L{gx + 10},{gy + 18} L{gx + 20},{gy + 4} L{gx + 30},{gy + 12} L{gx + 40},{gy + 16}" if peak else \
            f"M{gx},{gy + 20} L{gx + 40},{gy + 18}"
        svg_.path(d, stroke=C_CLIN, sw=2.2)
        if peak:
            svg_.circle(gx + 20, gy + 4, 3, C_CLIN)
    return draw


def g_bottles(n, growth):
    def draw(gx, gy):
        for i in range(n):
            I.bottle(svg_, gx + i * 13 - 2, gy - 2, 30, growth=growth)
        if not growth:
            svg_.line(gx + 8, gy + 20, gx + 20, gy + 20, stroke=GHOST, sw=2)
    return draw


def g_colonies(n):
    def draw(gx, gy):
        cx, cy = gx + 20, gy + 15
        svg_.circle(cx, cy, 13, "#fef9ee", stroke=INK2, sw=1.4)
        for (ddx, ddy) in ((-4, -3), (5, 2), (-1, 6), (3, -6), (-6, 4))[:n]:
            svg_.circle(cx + ddx, cy + ddy, 2, "#f59e0b")
    return draw


def g_articles(ok):
    def draw(gx, gy):
        for i in range(3):
            I.document(svg_, gx + i * 7, gy - 4 + i * 2, 30, lines=3)
        (I.check if ok else I.cross)(svg_, gx + 36, gy + 24, 14)
    return draw


def g_sieve(held, overridden=False):
    def draw(gx, gy):
        I.yeast(svg_, gx + 20, gy + 7, 18, ink=GHOST if held else INK, fill=GRAY_T)
        I.sieve(svg_, gx + 2, gy + 17, 36, 9)
        if overridden:
            svg_.path(f"M{gx + 20},{gy + 14} V{gy + 30}", stroke=GREEN, sw=2.4)
            svg_.path(f"M{gx + 15},{gy + 25} L{gx + 20},{gy + 31} L{gx + 25},{gy + 25}", stroke=GREEN, sw=2.4)
    return draw


def g_ghosts():
    def draw(gx, gy):
        I.bacterium(svg_, gx + 8, gy + 8, 14, ink=GHOST, fill=GRAY_T)
        I.mycobacterium(svg_, gx + 26, gy + 10, 16, ink=GHOST, fill=GRAY_T)
        I.bacterium(svg_, gx + 16, gy + 24, 14, ink=GHOST, fill=GRAY_T, angle=25)
        svg_.circle(gx + 36, gy + 24, 6, "#ffffff", stroke=RED, sw=1.6)
        svg_.line(gx + 33, gy + 24, gx + 39, gy + 24, stroke=RED, sw=1.6)
    return draw


def g_igm():
    def draw(gx, gy):
        I.antibody(svg_, gx + 12, gy + 16, 26, accent=C_LAB)
        I.antibody(svg_, gx + 30, gy + 12, 20, accent=C_LAB)
    return draw


def g_rule():
    def draw(gx, gy):
        I.cog(svg_, gx + 6, gy - 2, 30, fill=AMBER_T)
        I.flag(svg_, gx + 36, gy + 22, 14)
    return draw


def g_none():
    def draw(gx, gy):
        svg_.circle(gx + 20, gy + 14, 10, "#ffffff", stroke=GHOST, sw=1.4)
        svg_.line(gx + 15, gy + 14, gx + 25, gy + 14, stroke=GHOST, sw=1.6)
    return draw


def g_specimens():
    def draw(gx, gy):
        I.blood_tube(svg_, gx - 2, gy - 4, 26, accent="#dc2626")
        I.sequencer(svg_, gx + 18, gy - 2, 24)
        svg_.path(f"M{gx + 10},{gy + 26} H{gx + 34}", stroke=GREEN, sw=2)
    return draw


# icons for chips (24 units)
def ic(fn, **kw):
    return lambda ix, iy: fn(svg_, ix, iy, 24, **kw)


def ic_centered(fn, **kw):
    return lambda ix, iy: fn(svg_, ix + 12, iy + 12, 24, **kw)


# ---- case rows ---------------------------------------------------------------------------------
def call_chip(svg, x, y, kind, l1, l2):
    fill, edge, ink = {"sel": (GREEN_T, GREEN_E, GREEN), "exc": (RED_T, RED_E, RED), "rev": (AMBER_T, AMBER_E, AMBER)}[kind]
    svg.rect(x, y, 150, CH, fill, stroke=edge, sw=1.2, rx=10)
    I.lock(svg, x + 4, y + 2, 20)
    text(svg, x + 75, y + 28, l1, size=FS, fill=ink, anchor="middle", weight="bold")
    text(svg, x + 75, y + 46, l2, size=FS3, fill=ink, anchor="middle")


def organism_row(svg, y, glyph, name, sub, chips, call):
    x_org, x_chip, x_call = 20, 210, 830
    glyph(svg, x_org + 16, y + 26, 30)
    svg.rich(x_org + 38, y + 26, [(name, {"font-style": "italic", "font-weight": "bold"})], size=FS3, fill=INK)
    text(svg, x_org + 38, y + 41, sub, size=FS3, fill=MUTED)
    for k, (verdict, icon, glyph_fn, l1, l2) in enumerate(chips):
        chip(svg, x_chip + k * (CW + 8), y, verdict, icon, glyph_fn, l1, l2)
    xe = x_chip + len(chips) * (CW + 8) - 8
    svg.arrow(xe + 6, y + CH / 2, x_call - 6, y + CH / 2, stroke=INK2, sw=1.4, head=6)
    call_chip(svg, x_call, y, *call)


def case_header(svg, y, letter, title, note=""):
    heading(svg, 14, y, letter, title)
    if note:
        text(svg, W - 14, y, note, size=FS3, fill=MUTED, anchor="end")


def cases(svg, y):
    seq = ic(I.sequencer); xr = ic(I.xray); tube = ic(I.blood_tube); petri = ic(I.petri); pcr = ic(I.pcr_box)
    doc = ic(I.document); cog = ic(I.cog); bott = ic(I.bottle); ab = ic_centered(I.antibody)
    # c: colonization or infection
    case_header(svg, y, "e", "Colonization or infection: two organisms in one lavage specimen", "Case 1 · ventilated patient")
    organism_row(svg, y + 16, I.bacterium, "Klebsiella pneumoniae", "on the lavage report", [
        ("S", seq, g_bar_pair(1.0, 0.08), "68,569 reads", "dominant"),
        ("S", xr, g_lungs(), "bilateral", "consolidation"),
        ("S", tube, g_spark(), "CRP peak", "hypoxaemia"),
        ("C", bott, g_bottles(2, False), "blood culture", "no growth"),
        ("S", doc, g_articles(True), "same species,", "site and host"),
    ], ("sel", "SELECTED", "primary pathogen"))
    organism_row(svg, y + 16 + CH + 12, I.yeast, "Candida albicans", "on the same report", [
        ("X", seq, g_bar_pair(0.08, 1.0), "low reads", "not dominant"),
        ("C", petri, g_colonies(2), "repeated", "low burden"),
        ("X", bott, g_bottles(2, False), "no sterile-", "site isolate"),
        ("R", cog, g_sieve(True), "respiratory", "yeast guardrail"),
        ("X", doc, g_articles(False), "colonization", "in this setting"),
    ], ("exc", "NOT SELECTED", "airway colonization"))
    y2 = y + 16 + 2 * CH + 12 + 40
    # d: same yeast, same rule, opposite call
    case_header(svg, y2, "f", "The same yeast and the same guardrail, the opposite call", "Case 2")
    organism_row(svg, y2 + 16, I.yeast, "Candida tropicalis", "on the lavage report", [
        ("S", seq, g_reads(0.8), "high reads", "lavage fluid"),
        ("S", bott, g_bottles(3, True), "blood cultures", "same species"),
        ("V", cog, g_sieve(False, overridden=True), "guardrail", "overridden"),
        ("S", tube, g_specimens(), "two specimens", "concordant"),
    ], ("sel", "SELECTED", "invasive candidiasis"))
    y3 = y2 + 16 + CH + 40
    # e: the pathogen the sequenced specimen did not contain
    case_header(svg, y3, "g", "The pathogen the sequenced specimen did not contain", "Case 3 · registry")
    organism_row(svg, y3 + 16, I.bacterium, "Chlamydophila pneumoniae", "adjudicated pathogen", [
        ("X", seq, g_ghosts(), "lavage report:", "3 others, not this"),
        ("S", ab, g_igm(), "serum IgM", "day −1"),
        ("C", pcr, g_none(), "no molecular", "test for it"),
        ("R", cog, g_rule(), "indirect", "serology rule"),
    ], ("rev", "HELD FOR REVIEW", "delivered with reason"))
    return y3 + 16 + CH + 14


def key(svg, y):
    """Chip tint key and the lock."""
    items = [("S", "supports the call"), ("X", "argues against it"), ("C", "context or absent"), ("R", "rule applied"), ("V", "guardrail overridden")]
    x = 20
    for code, lab in items:
        fill, edge = TINT[code]
        svg.rect(x, y - 9, 22, 14, fill, stroke=edge, sw=2 if code == "V" else 1, rx=4)
        text(svg, x + 28, y + 2, lab, size=FS3, fill=INK2)
        x += 28 + len(lab) * 5.4 + 18
    I.lock(svg, x + 4, y - 12, 18)
    text(svg, x + 26, y + 2, "decision frozen before the explanation is written", size=FS3, fill=INK2)


# ---- panel h: every candidate leaves with a disposition ------------------------------------------
def panel_h(svg, y):
    heading(svg, 14, y, "h", "Every candidate leaves with a disposition")
    total, picked, rescued, notsel = 518, 114, 9, 395
    bx, by, bw, bh = 40, y + 14, 560, 18
    cx = bx
    for n, col in ((picked, BLUE_D), (rescued, TEAL), (notsel, "#d1d5db")):
        w = bw * n / total
        svg.rect(cx, by, w, bh, col, stroke="#ffffff", sw=1)
        cx += w
    x_p = bx + bw * (picked / 2) / total
    x_r = bx + bw * (picked + rescued / 2) / total
    x_n = bx + bw * (picked + rescued + notsel / 2) / total
    text(svg, x_p, by + bh + 14, "114 picked by the rules", size=FS3, fill=BLUE_D, anchor="middle", weight="bold")
    svg.line(x_r, by + bh, x_r, by + bh + 22, stroke=TEAL, sw=1)
    text(svg, x_r + 4, by + bh + 32, "9 rescued by traced evidence", size=FS3, fill=TEAL, weight="bold")
    text(svg, x_n + 40, by + bh + 14, "395 set aside, each with its reason", size=FS3, fill=INK2, anchor="middle", weight="bold")
    text(svg, bx, by - 4, "518 candidates in 55 patients", size=FS3, fill=MUTED)
    px = bx + bw + 40
    svg.rect(px, by - 10, 130, 38, GRAY_T, stroke="none", rx=6)
    text(svg, px + 65, by + 8, "9.4", size=FS + 5, fill=INK, anchor="middle", weight="bold")
    text(svg, px + 65, by + 22, "candidates per patient", size=FS3, fill=MUTED, anchor="middle")
    svg.arrow(px + 136, by + 8, px + 150, by + 8, stroke=INK2, sw=1.3)
    svg.rect(px + 154, by - 10, 130, 38, BLUE_T, stroke="none", rx=6)
    text(svg, px + 219, by + 8, "2.2", size=FS + 5, fill=BLUE_D, anchor="middle", weight="bold")
    text(svg, px + 219, by + 22, "selected, each explained", size=FS3, fill=MUTED, anchor="middle")
    return by + bh + 40


def main() -> None:
    global svg_
    svg = SVG(W, 900)
    svg_ = svg
    ytop = panel_a(svg, 30) + 8
    svg.line(14, ytop, W - 14, ytop, stroke=HAIR, sw=0.8)
    yc = cases(svg, ytop + 32)
    key(svg, yc + 6)
    svg.line(14, yc + 22, W - 14, yc + 22, stroke=HAIR, sw=0.8)
    yf = panel_h(svg, yc + 50)
    text(svg, 14, yf + 8, "Cases 1 and 2: KMUH intensive-care series, first pipeline version (17 January 2026). Case 3: registry case; "
                          "disposition drawn from the serology rule as implemented, delivered record pending.", size=FS3, fill=MUTED)
    svg.height = yf + 18
    svg.save(OUT)


if __name__ == "__main__":
    main()
