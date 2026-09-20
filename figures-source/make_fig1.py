#!/usr/bin/env python3
"""Figure 1: overview of AETIA (figures/fig1_overview.svg). Edit this script, not the SVG.

Pictorial schematic in four rows: a, multimodal record -> one language-model agent per modality
-> structured evidence; b, deterministic sieve with guardrails and language-model safety review;
c, evidence modules per carried candidate; d, R5 gate -> frozen list -> post-hoc rationale ->
delivery. Canvas 1000 units = 180 mm (Nature double column); 13 units ~ 6.6 pt.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG  # noqa: E402
import icons as I  # noqa: E402

OUT = HERE.parent / "figures" / "fig1_overview.svg"
W, H = 1000, 1080
INK = "#1f2937"; INK2 = "#4b5563"; MUTED = "#6b7280"; HAIR = "#cbd5e1"
BLUE = "#1d4ed8"; BLUE_T = "#dbeafe"; BLUE_E = "#93c5fd"
VIOL = "#6d28d9"; VIOL_T = "#ede9fe"; VIOL_E = "#c4b5fd"
GREEN_T = "#dcfce7"; GREEN_E = "#86efac"
AMBER_T = "#fef3c7"; AMBER_E = "#fcd34d"
GRAY_T = "#f3f4f6"; GRAY_E = "#cbd5e1"
FS = 13


def text(svg, x, y, s, size=FS, fill=INK, anchor="start", weight="normal", style="normal"):
    svg.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight, style=style)


def chip(svg, x, y, w, h, label, fill=BLUE_T, edge=BLUE_E, size=FS, icon=None, weight="normal"):
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.2, rx=h / 2)
    if icon:
        icon(svg, x + 6, y + (h - 22) / 2, 22)
        text(svg, x + 32, y + h / 2 + size * 0.36, label, size=size, weight=weight)
    else:
        text(svg, x + w / 2, y + h / 2 + size * 0.36, label, size=size, anchor="middle", weight=weight)


def card(svg, x, y, w, h, title, fill=GRAY_T, edge=GRAY_E, title_size=FS + 1):
    svg.rect(x, y, w, h, fill, stroke=edge, sw=1.2, rx=8)
    text(svg, x + 12, y + 20, title, size=title_size, weight="bold")


def arrow(svg, x1, y1, x2, y2, color=INK2, sw=1.4):
    svg.arrow(x1, y1, x2, y2, stroke=color, sw=sw, head=6)


def heading(svg, x, y, letter, title):
    svg.text(x, y, letter, size=22, weight="bold", fill=INK)
    text(svg, x + 26, y, title, size=15, fill=INK2)


def main() -> None:
    svg = SVG(W, H)

    # ================================================================ a ==========================
    heading(svg, 14, 30, "a", "Multimodal record, one language-model agent per modality, structured evidence")
    mods = [
        ("Chest imaging", "report text", I.xray, [I.bacterium, I.fungus]),
        ("Blood counts,", "CRP, other labs", I.blood_tube, [I.person]),
        ("Galactomannan", "antigen", I.well_plate, [I.fungus]),
        ("Multiplex PCR", "FilmArray panel", I.pcr_box, [I.virus, I.bacterium]),
        ("Cultures", "blood, sputum, BAL", I.petri, [I.bacterium, I.yeast]),
        ("Diagnosis and", "comorbidities", I.clipboard, [I.person]),
        ("mNGS report", "reads, RK/NTC codes", I.sequencer, [I.bacterium, I.fungus, I.virus]),
    ]
    agents = ["Image agent", "Host / lab agent", "GM & panel agent", "Molecular agent",
              "Culture agent", "Host / lab agent", "mNGS-to-specimen"]
    colw = 138; x0 = 16; ytop = 46
    for i, ((l1, l2, icon, glyphs), ag) in enumerate(zip(mods, agents)):
        cx = x0 + i * colw + colw / 2
        icon(svg, cx - 30, ytop, 60)
        text(svg, cx, ytop + 78, l1, size=FS, anchor="middle", weight="bold")
        text(svg, cx, ytop + 94, l2, size=FS - 2, fill=MUTED, anchor="middle")
        arrow(svg, cx, ytop + 102, cx, ytop + 118)
        chip(svg, cx - 60, ytop + 120, 120, 26, ag, size=FS - 1)
        # organisms the agent can report
        n = len(glyphs); gap = 30
        for j, g in enumerate(glyphs):
            gx = cx + (j - (n - 1) / 2) * gap
            g(svg, gx, ytop + 172, 26)
    # bus to structured evidence
    ybus = ytop + 200
    for i in range(7):
        cx = x0 + i * colw + colw / 2
        svg.line(cx, ytop + 190, cx, ybus, stroke=INK2, sw=1.2)
    svg.line(x0 + colw / 2, ybus, x0 + 6 * colw + colw / 2, ybus, stroke=INK2, sw=1.2)
    xc = x0 + 3.5 * colw
    arrow(svg, xc, ybus, xc, ybus + 16)
    card(svg, xc - 340, ybus + 18, 680, 50, "")
    I.document(svg, xc - 330, ybus + 24, 38)
    text(svg, xc - 288, ybus + 38, "Structured evidence, fixed JSON schema", size=FS + 1, weight="bold")
    text(svg, xc - 288, ybus + 56, "per-organism support by modality · host tier V0–V3, opportunistic coverage O0–O2 · specimen, site, time window · no answer labels",
         size=FS - 3, fill=INK2)

    # ================================================================ b ==========================
    yb = ybus + 100
    heading(svg, 14, yb, "b", "Deterministic selection (v20): tiered sieve, guardrails, language-model safety review")
    # candidate column
    cx0 = 16; ylist = yb + 22
    text(svg, cx0, ylist, "mNGS candidates", size=FS, weight="bold")
    text(svg, cx0, ylist + 15, "reads, control codes", size=FS - 2, fill=MUTED)
    cands = [(I.bacterium, 96, "R4"), (I.virus, 70, "R3"), (I.yeast, 62, "R3"), (I.bacterium, 40, "R2"),
             (I.fungus, 30, "R2"), (I.bacterium, 18, "R1"), (I.virus, 10, "R1"), (I.bacterium, 5, "R0")]
    for j, (g, reads, tier) in enumerate(cands):
        yy = ylist + 36 + j * 22
        g(svg, cx0 + 14, yy, 20)
        svg.rect(cx0 + 32, yy - 4, reads, 8, "#fdba74" if j else "#f97316", rx=2)
        text(svg, cx0 + 36 + reads, yy + 4, tier, size=FS - 3, fill=MUTED)
    # pipe with four sieves
    px = 190; py = ylist + 20; ph = 150; pw = 430
    svg.rect(px, py, pw, ph, "#ffffff", stroke=HAIR, sw=1.2, rx=10)
    arrow(svg, cx0 + 150, py + ph / 2, px, py + ph / 2)
    sieves = [("Read burden", "R0–R4"), ("Dominance", "D0–D3"), ("Control rank", "1–5, percentile"), ("Site & hospital", "support")]
    sw_ = 22; sgap = (pw - 4 * sw_) / 5
    for i, (t1, t2) in enumerate(sieves):
        sx = px + sgap + i * (sw_ + sgap)
        svg.rect(sx, py + 8, sw_, ph - 16, GRAY_T, stroke=GRAY_E, sw=1.2, rx=4)
        for yy in range(int(py + 16), int(py + ph - 12), 8):
            svg.line(sx + 4, yy, sx + sw_ - 4, yy, stroke="#cbd5e1", sw=0.8)
        text(svg, sx + sw_ / 2, py + ph + 16, t1, size=FS - 1, anchor="middle", weight="bold")
        text(svg, sx + sw_ / 2, py + ph + 30, t2, size=FS - 3, fill=MUTED, anchor="middle")
        # organisms passing through: fewer after each sieve
        keep = [I.bacterium, I.virus, I.yeast, I.bacterium, I.fungus][: 5 - i]
        for j, g in enumerate(keep):
            g(svg, sx + sw_ + sgap / 2, py + 25 + j * 24, 18)
    # levels label inside pipe
    text(svg, px + pw - 8, py + ph - 8, "signal tier M1–M5 → causative level 1–5", size=FS - 3, fill=MUTED, anchor="end")
    # guardrail band below pipe: deflected organisms
    gy = py + ph + 46
    svg.rect(px, gy, pw, 44, AMBER_T, stroke=AMBER_E, sw=1.2, rx=8)
    text(svg, px + 12, gy + 18, "Guardrails (33 rules)", size=FS - 1, weight="bold")
    text(svg, px + 12, gy + 34, "respiratory Candida · oral flora · water / skin organisms · EBV, HHV · weak moulds", size=FS - 3, fill=INK2)
    for j, g in enumerate([I.yeast, I.bacterium, I.virus]):
        gx = px + pw - 110 + j * 36
        g(svg, gx, gy + 22, 18); I.cross(svg, gx + 9, gy + 13, 14)
    # picked
    okx = px + pw + 30
    card(svg, okx, py, 150, ph, "Picked")
    text(svg, okx + 12, py + 36, "levels 1–2; level 3 with", size=FS - 3, fill=INK2)
    text(svg, okx + 12, py + 49, "support; order immutable", size=FS - 3, fill=INK2)
    for j, g in enumerate([I.bacterium, I.virus]):
        g(svg, okx + 34, py + 78 + j * 30, 22); I.check(svg, okx + 60, py + 78 + j * 30, 16)
        text(svg, okx + 74, py + 82 + j * 30, ["primary, level 1", "secondary, level 2"][j], size=FS - 3, fill=INK2)
    arrow(svg, px + pw, py + ph / 2, okx, py + ph / 2)
    # LLM safety review
    rvx = okx + 170
    card(svg, rvx, py, 178, ph, "", fill=VIOL_T, edge=VIOL_E)
    I.brain_chip(svg, rvx + 8, py + 6, 30)
    text(svg, rvx + 42, py + 20, "Safety review (LLM)", size=FS + 1, weight="bold")
    text(svg, rvx + 12, py + 40, "reads only the unpicked;", size=FS - 3, fill=INK2)
    text(svg, rvx + 12, py + 53, "may flag, cannot pick", size=FS - 3, fill=INK2)
    for j, (g, lab, carried) in enumerate([(I.fungus, "high priority", True), (I.bacterium, "context needed", True),
                                            (I.yeast, "low specificity", False), (I.virus, "omitted", False)]):
        yy = py + 76 + j * 20
        g(svg, rvx + 22, yy, 16)
        if carried:
            I.flag(svg, rvx + 40, yy, 13)
        text(svg, rvx + 52, yy + 4, lab + ("" if carried else "  (audit only)"), size=FS - 3, fill=INK2 if carried else MUTED)
    # curved arrow from sieve outflow to review
    svg.path(f"M{px + pw - 40},{py + ph} C{px + pw - 40},{py + ph + 30} {rvx + 80},{py + ph + 30} {rvx + 80},{py + ph + 2}", stroke=VIOL, sw=1.2)
    svg.add(f'<path d="M{rvx + 76},{py + ph + 8} L{rvx + 80},{py + ph} L{rvx + 84},{py + ph + 8} Z" fill="{VIOL}"/>')
    text(svg, okx, gy + 27, "Carried forward: picked ∪ high priority ∪ context needed", size=FS - 1, fill=INK, weight="bold")

    # ================================================================ c ==========================
    yc = gy + 78
    heading(svg, 14, yc, "c", "Evidence modules computed for every carried candidate")
    ccy = yc + 16; ch = 168
    ax = 16; aw = 440
    card(svg, ax, ccy, aw, ch, "A  Literature  and  A1  patient case-fit", fill=GREEN_T, edge=GREEN_E)
    for j in range(3):
        I.document(svg, ax + 14 + j * 12, ccy + 30 + j * 5, 36)
    text(svg, ax + 92, ccy + 44, "PubMed, ≤10 articles per organism at the target site", size=FS - 2)
    text(svg, ax + 92, ccy + 58, "each judged: exact species · human clinical · site · quoted span", size=FS - 3, fill=INK2)
    I.check(svg, ax + 100, ccy + 72, 13); I.check(svg, ax + 116, ccy + 72, 13); I.cross(svg, ax + 132, ccy + 72, 13)
    text(svg, ax + 144, ccy + 76, "≥ 3 valid supports among ≥ 5 judgeable → A positive", size=FS - 3, fill=INK2)
    svg.line(ax + 14, ccy + 90, ax + aw - 14, ccy + 90, stroke=GREEN_E, sw=1)
    I.person(svg, ax + 34, ccy + 116, 36)
    text(svg, ax + 62, ccy + 108, "A1: every article re-judged against this patient — site, syndrome,", size=FS - 3, fill=INK2)
    text(svg, ax + 62, ccy + 121, "host, phenotype and timing; a traceability gate requires exact spans", size=FS - 3, fill=INK2)
    text(svg, ax + 62, ccy + 140, "strong match  ·  partial match  ·  mismatch  ·  insufficient", size=FS - 3, fill=INK, weight="bold")
    text(svg, ax + 62, ccy + 156, "counts per candidate feed R5", size=FS - 4, fill=MUTED)
    bx = ax + aw + 12; bw = 150
    card(svg, bx, ccy, bw, ch, "B  mNGS strength")
    for j, hgt in enumerate((16, 26, 38, 50)):
        svg.rect(bx + 16 + j * 13, ccy + 84 - hgt, 9, hgt, "#fdba74" if j < 2 else "#f97316", rx=2)
    text(svg, bx + 16, ccy + 97, "absolute", size=FS - 4, fill=MUTED)
    svg.rect(bx + 90, ccy + 38, 11, 46, "#f97316", rx=2); svg.rect(bx + 105, ccy + 74, 11, 10, "#fdba74", rx=2)
    text(svg, bx + 120, ccy + 82, "≥10×", size=FS - 4, fill=INK2)
    text(svg, bx + 90, ccy + 97, "relative", size=FS - 4, fill=MUTED)
    text(svg, bx + 14, ccy + 116, "absolute: M1/M2 or R3/R4", size=FS - 4, fill=INK2)
    text(svg, bx + 14, ccy + 128, "relative: D2/D3, or rank 1", size=FS - 4, fill=INK2)
    text(svg, bx + 14, ccy + 140, "with percentile ≥ 0.8", size=FS - 4, fill=INK2)
    text(svg, bx + 14, ccy + 156, "either axis; site aligned", size=FS - 4, fill=INK, weight="bold")
    cx_ = bx + bw + 12; cw = 175
    card(svg, cx_, ccy, cw, ch, "C  Direct evidence")
    I.petri(svg, cx_ + 14, ccy + 28, 42); I.pcr_box(svg, cx_ + 60, ccy + 28, 42)
    text(svg, cx_ + 108, ccy + 48, "same organism,", size=FS - 4, fill=INK2)
    text(svg, cx_ + 108, ccy + 60, "structured entry", size=FS - 4, fill=INK2)
    for j, (g, t) in enumerate([("C3", "sterile site or tissue"), ("C2", "site-matched assay"), ("C1", "context only"), ("C0", "none or pending"), ("CNEG", "explicit negative")]):
        yy = ccy + 90 + j * 13
        text(svg, cx_ + 14, yy, g, size=FS - 4, weight="bold"); text(svg, cx_ + 50, yy, t, size=FS - 4, fill=INK2)
    text(svg, cx_ + 14, ccy + 158, "C3 alone can select (R5)", size=FS - 4, fill=INK, weight="bold")
    dx = cx_ + cw + 12; dw = W - 16 - dx
    card(svg, dx, ccy, dw, ch, "D  Colonization gate")
    I.sieve(svg, dx + 14, ccy + 36, dw - 28, 16)
    for j, (t, col) in enumerate([("pass", "#15803d"), ("guarded", "#d97706"), ("block", "#b91c1c"), ("unknown", "#6b7280")]):
        yy = ccy + 76 + j * 14
        svg.circle(dx + 22, yy - 4, 4, col); text(svg, dx + 32, yy, t, size=FS - 4, fill=INK2)
    text(svg, dx + 14, ccy + 142, "site coherence and", size=FS - 4, fill=INK2)
    text(svg, dx + 14, ccy + 154, "colonization guardrails", size=FS - 4, fill=INK2)
    text(svg, dx + 14, ccy + 164, "reported; not an R5 gate", size=FS - 4, fill=MUTED)
    text(svg, 16, ccy + ch + 20, "Missing or pending tests are unknown, never negative. Reference labels enter only the evaluation code.", size=FS - 2, fill=INK2)

    # ================================================================ d ==========================
    yd = ccy + ch + 50
    heading(svg, 14, yd, "d", "Final rule R5, frozen selection, post-hoc rationale, auditable delivery")
    dy = yd + 18; dh = 138
    inx = 16; inw = 230
    inputs = [("Picked upstream", ["immutable; keeps its order"], BLUE_T, BLUE_E),
              ("C3 direct evidence", ["exact organism, sterile site or tissue"], GRAY_T, GRAY_E),
              ("A1 ∧ site ∧ B", ["strong ≥ 2 or strong + partial ≥ 7;", "site aligned; B absolute or relative"], GREEN_T, GREEN_E)]
    for j, (lab, subs, fill, edge) in enumerate(inputs):
        yy = dy + j * 46
        svg.rect(inx, yy, inw, 40, fill, stroke=edge, sw=1.2, rx=6)
        text(svg, inx + 10, yy + 14, lab, size=FS - 1, weight="bold")
        for k_, sub in enumerate(subs):
            text(svg, inx + 10, yy + 26 + k_ * 11, sub, size=FS - 4, fill=INK2)
        svg.line(inx + inw, yy + 20, inx + inw + 30, yy + 20, stroke=INK2, sw=1.2)
    gx0 = inx + inw + 30; gmid = dy + 66
    svg.path(f"M{gx0},{dy + 6} Q{gx0 + 22},{gmid} {gx0},{dy + 126} Q{gx0 + 50},{dy + 126} {gx0 + 74},{gmid} Q{gx0 + 50},{dy + 6} {gx0},{dy + 6} Z", stroke=INK, sw=1.6, fill="#ffffff")
    text(svg, gx0 + 30, gmid + 5, "OR", size=FS + 1, anchor="middle", weight="bold")
    text(svg, gx0 + 36, dy + dh + 14, "R5", size=FS - 1, anchor="middle", fill=MUTED)
    arrow(svg, gx0 + 74, gmid, gx0 + 104, gmid)
    fx = gx0 + 106; fw = 160
    card(svg, fx, dy, fw, dh, "Frozen decision", fill=BLUE_T, edge=BLUE_E)
    I.lock(svg, fx + 8, dy + 30, 40)
    for j, g in enumerate([I.bacterium, I.virus, I.fungus]):
        g(svg, fx + 70 + j * 28, dy + 52, 20)
    text(svg, fx + 54, dy + 80, "rule path per organism", size=FS - 4, fill=INK2)
    text(svg, fx + 54, dy + 92, "SHA-256 of every input", size=FS - 4, fill=INK2)
    text(svg, fx + 54, dy + 104, "rescued organisms are", size=FS - 4, fill=INK2)
    text(svg, fx + 54, dy + 116, "appended after the picks", size=FS - 4, fill=INK2)
    arrow(svg, fx + fw, gmid, fx + fw + 28, gmid)
    rx = fx + fw + 30; rw = 172
    card(svg, rx, dy, rw, dh, "", fill=VIOL_T, edge=VIOL_E)
    I.brain_chip(svg, rx + 8, dy + 6, 30)
    text(svg, rx + 42, dy + 20, "Rationale (LLM)", size=FS + 1, weight="bold")
    text(svg, rx + 12, dy + 44, "written after the list is frozen", size=FS - 4, fill=INK2)
    text(svg, rx + 12, dy + 56, "limited to the evidence window", size=FS - 4, fill=INK2)
    text(svg, rx + 12, dy + 68, "structure-audited before delivery", size=FS - 4, fill=INK2)
    text(svg, rx + 12, dy + 90, "cannot alter or re-rank", size=FS - 3, fill=INK, weight="bold")
    text(svg, rx + 12, dy + 103, "the selection", size=FS - 3, fill=INK, weight="bold")
    arrow(svg, rx + rw, gmid, rx + rw + 28, gmid)
    dlx = rx + rw + 30; dlw = W - 16 - dlx
    card(svg, dlx, dy, dlw, dh, "Delivery")
    I.table_icon(svg, dlx + 8, dy + 30, 40)
    text(svg, dlx + 52, dy + 46, "simple table: hospital, patient,", size=FS - 4, fill=INK2)
    text(svg, dlx + 52, dy + 58, "selected pathogens, reasons", size=FS - 4, fill=INK2)
    text(svg, dlx + 52, dy + 76, "traceable JSON / Markdown / XLSX", size=FS - 4, fill=INK2)
    text(svg, dlx + 52, dy + 88, "with rule paths and hashes", size=FS - 4, fill=INK2)
    text(svg, dlx + 52, dy + 100, "automated delivery audit", size=FS - 4, fill=INK2)
    text(svg, dlx + 52, dy + 118, "research use, pending review", size=FS - 4, fill=MUTED)
    svg.save(OUT)


if __name__ == "__main__":
    main()
