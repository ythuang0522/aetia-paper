"""Flat vector icons for the manuscript figures (stroke-based, consistent 2-unit line weight).

Every icon draws inside a square of side `s` whose top-left corner is (x, y); callers place and
scale them. Colours come from the caller (ink) so the set stays monochrome with one accent.
"""
from __future__ import annotations

import math

INK = "#1f2937"
INK2 = "#4b5563"
LIGHT = "#e5e7eb"
PALE = "#f3f4f6"
WHITE = "#ffffff"


def _p(svg, d, stroke=INK, sw=2.0, fill="none", extra=""):
    svg.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _r(svg, x, y, w, h, fill=WHITE, stroke=INK, sw=2.0, rx=3):
    svg.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def _c(svg, cx, cy, r, fill=WHITE, stroke=INK, sw=2.0):
    svg.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


# ---------------------------------------------------------------- modalities ------------------
def xray(svg, x, y, s, ink=INK):
    """Chest radiograph: dark plate, two lung fields, trachea and heart shadow."""
    k = s / 40
    _r(svg, x + 2 * k, y + 2 * k, 36 * k, 36 * k, fill="#374151", stroke=ink, sw=1.5 * k, rx=4 * k)
    for sgn in (-1, 1):
        cx = x + 20 * k + sgn * 8.5 * k
        d = (f"M{cx - sgn * 1.5 * k:.2f},{y + 11 * k:.2f} "
             f"C{cx + sgn * 10 * k:.2f},{y + 12 * k:.2f} {cx + sgn * 10 * k:.2f},{y + 31 * k:.2f} {cx + sgn * 1 * k:.2f},{y + 32 * k:.2f} "
             f"C{cx - sgn * 4 * k:.2f},{y + 31 * k:.2f} {cx - sgn * 4 * k:.2f},{y + 16 * k:.2f} {cx - sgn * 1.5 * k:.2f},{y + 11 * k:.2f} Z")
        _p(svg, d, stroke="#9ca3af", sw=1.2 * k, fill="#6b7280")
    _p(svg, f"M{x + 20 * k:.2f},{y + 6 * k:.2f} V{y + 14 * k:.2f}", stroke="#d1d5db", sw=1.8 * k)
    _p(svg, f"M{x + 19 * k:.2f},{y + 22 * k:.2f} a{6 * k:.2f},{6 * k:.2f} 0 1 0 {0.1 * k:.2f},0", stroke="#9ca3af", sw=1 * k, fill="#4b5563")


def blood_tube(svg, x, y, s, ink=INK, accent="#dc2626"):
    """Blood tube with cap and a small CBC histogram."""
    k = s / 40
    # tube
    _p(svg, f"M{x + 8 * k:.2f},{y + 8 * k:.2f} V{y + 30 * k:.2f} A{5 * k:.2f},{5 * k:.2f} 0 0 0 {x + 18 * k:.2f},{y + 30 * k:.2f} V{y + 8 * k:.2f} Z",
       stroke=ink, sw=1.8 * k, fill=WHITE)
    _p(svg, f"M{x + 9.5 * k:.2f},{y + 18 * k:.2f} V{y + 30 * k:.2f} A{3.5 * k:.2f},{3.5 * k:.2f} 0 0 0 {x + 16.5 * k:.2f},{y + 30 * k:.2f} V{y + 18 * k:.2f} Z",
       stroke="none", fill=accent)
    _r(svg, x + 6.5 * k, y + 4 * k, 13 * k, 5 * k, fill="#9ca3af", stroke=ink, sw=1.4 * k, rx=1.5 * k)
    # histogram
    _p(svg, f"M{x + 23 * k:.2f},{y + 32 * k:.2f} V{y + 10 * k:.2f} M{x + 23 * k:.2f},{y + 32 * k:.2f} H{x + 38 * k:.2f}", stroke=ink, sw=1.4 * k)
    d = (f"M{x + 24 * k:.2f},{y + 31 * k:.2f} C{x + 26 * k:.2f},{y + 14 * k:.2f} {x + 27 * k:.2f},{y + 14 * k:.2f} {x + 29 * k:.2f},{y + 31 * k:.2f} "
         f"C{x + 31 * k:.2f},{y + 22 * k:.2f} {x + 32 * k:.2f},{y + 22 * k:.2f} {x + 34 * k:.2f},{y + 31 * k:.2f} C{x + 35 * k:.2f},{y + 27 * k:.2f} {x + 36 * k:.2f},{y + 27 * k:.2f} {x + 37 * k:.2f},{y + 31 * k:.2f}")
    _p(svg, d, stroke=accent, sw=1.4 * k, fill="none")


def test_strip(svg, x, y, s, ink=INK, accent="#dc2626"):
    """Lateral-flow cassette (CRP) with a dropper above."""
    k = s / 40
    _r(svg, x + 3 * k, y + 20 * k, 34 * k, 14 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=3 * k)
    _c(svg, x + 10 * k, y + 27 * k, 3 * k, fill=PALE, stroke=ink, sw=1.2 * k)
    _r(svg, x + 17 * k, y + 23.5 * k, 15 * k, 7 * k, fill=PALE, stroke=ink, sw=1.2 * k, rx=1 * k)
    _p(svg, f"M{x + 22 * k:.2f},{y + 24.5 * k:.2f} V{y + 29.5 * k:.2f} M{x + 27 * k:.2f},{y + 24.5 * k:.2f} V{y + 29.5 * k:.2f}", stroke=accent, sw=1.6 * k)
    # dropper
    _p(svg, f"M{x + 26 * k:.2f},{y + 4 * k:.2f} L{x + 16 * k:.2f},{y + 14 * k:.2f}", stroke=ink, sw=2.2 * k)
    _r(svg, x + 25 * k, y + 2 * k, 8 * k, 5 * k, fill="#9ca3af", stroke=ink, sw=1.2 * k, rx=2 * k)
    _p(svg, f"M{x + 14 * k:.2f},{y + 16 * k:.2f} q{-1.5 * k:.2f},{2.5 * k:.2f} 0,{3.5 * k:.2f} q{1.5 * k:.2f},{-1 * k:.2f} 0,{-3.5 * k:.2f}", stroke=accent, sw=1.2 * k, fill=accent)


def well_plate(svg, x, y, s, ink=INK, accent="#0f766e"):
    """96-well plate with a few positive (dark) wells."""
    k = s / 40
    _r(svg, x + 2 * k, y + 10 * k, 36 * k, 26 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=3 * k)
    positives = {(1, 2), (2, 5), (0, 6), (3, 1)}
    for r in range(4):
        for c in range(8):
            cx = x + (6 + c * 4.1) * k
            cy = y + (15 + r * 5.3) * k
            fill = accent if (r, c) in positives else PALE
            _c(svg, cx, cy, 1.5 * k, fill=fill, stroke=ink, sw=0.6 * k)
    # dropper
    _p(svg, f"M{x + 30 * k:.2f},{y + 2 * k:.2f} L{x + 24 * k:.2f},{y + 9 * k:.2f}", stroke=ink, sw=2 * k)


def pcr_box(svg, x, y, s, ink=INK, accent="#1d4ed8"):
    """Bench instrument (multiplex PCR) with screen and tube strip."""
    k = s / 40
    _r(svg, x + 3 * k, y + 8 * k, 26 * k, 26 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=3 * k)
    _r(svg, x + 7 * k, y + 12 * k, 12 * k, 9 * k, fill="#374151", stroke=ink, sw=1.2 * k, rx=1.5 * k)
    _p(svg, f"M{x + 9 * k:.2f},{y + 18 * k:.2f} l{2 * k:.2f},{-3 * k:.2f} l{2 * k:.2f},{2 * k:.2f} l{2 * k:.2f},{-2.5 * k:.2f}", stroke="#93c5fd", sw=1 * k)
    for i in range(3):
        _c(svg, x + (9 + i * 4) * k, y + 27 * k, 1.3 * k, fill=PALE, stroke=ink, sw=0.9 * k)
    # tube strip
    for i in range(4):
        tx = x + (31 + i * 2.6) * k
        _p(svg, f"M{tx:.2f},{y + 14 * k:.2f} V{y + 27 * k:.2f} l{1 * k:.2f},{3 * k:.2f} l{1 * k:.2f},{-3 * k:.2f} V{y + 14 * k:.2f} Z", stroke=ink, sw=0.9 * k, fill=accent if i in (1, 3) else PALE)


def clipboard(svg, x, y, s, ink=INK):
    """Clinical record: clipboard with lines and a person mark."""
    k = s / 40
    _r(svg, x + 7 * k, y + 5 * k, 26 * k, 32 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=3 * k)
    _r(svg, x + 15 * k, y + 2 * k, 10 * k, 6 * k, fill="#9ca3af", stroke=ink, sw=1.2 * k, rx=1.5 * k)
    _c(svg, x + 14 * k, y + 15 * k, 2.6 * k, fill=PALE, stroke=ink, sw=1.1 * k)
    _p(svg, f"M{x + 10 * k:.2f},{y + 22 * k:.2f} a{4 * k:.2f},{4 * k:.2f} 0 0 1 {8 * k:.2f},0", stroke=ink, sw=1.1 * k)
    for i, w in enumerate((10, 10, 7)):
        yy = y + (14 + i * 4.2) * k
        _p(svg, f"M{x + 20 * k:.2f},{yy:.2f} H{x + (20 + w) * k:.2f}", stroke=ink, sw=1.1 * k)
    for i, w in enumerate((18, 14)):
        yy = y + (28 + i * 4.2) * k
        _p(svg, f"M{x + 11 * k:.2f},{yy:.2f} H{x + (11 + w) * k:.2f}", stroke=ink, sw=1.1 * k)


def sequencer(svg, x, y, s, ink=INK, accent="#c2410c"):
    """Sequencer with stacked reads aligned under a reference."""
    k = s / 40
    _r(svg, x + 6 * k, y + 2 * k, 28 * k, 18 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=3 * k)
    _r(svg, x + 10 * k, y + 5 * k, 20 * k, 9 * k, fill="#374151", stroke=ink, sw=1.1 * k, rx=1.5 * k)
    _p(svg, f"M{x + 12 * k:.2f},{y + 11 * k:.2f} h{4 * k:.2f} m{2 * k:.2f},0 h{6 * k:.2f} m{-10 * k:.2f},{-3 * k:.2f} h{7 * k:.2f}", stroke="#fbbf24", sw=1 * k)
    # reference + reads
    _p(svg, f"M{x + 4 * k:.2f},{y + 24 * k:.2f} H{x + 36 * k:.2f}", stroke=ink, sw=1.6 * k)
    reads = [(4, 12), (14, 10), (22, 12), (7, 9), (18, 11), (11, 8), (24, 10)]
    for i, (rx, rw) in enumerate(reads):
        yy = y + (27.5 + (i // 3) * 3.2) * k
        off = (i % 3) * 1.5
        _p(svg, f"M{x + (rx + off) * k:.2f},{yy:.2f} h{rw * k:.2f}", stroke=accent, sw=1.7 * k)


# ---------------------------------------------------------------- microbes ---------------------
def bacterium(svg, cx, cy, s, ink=INK, fill=LIGHT, angle=-20):
    """Rod-shaped bacterium with flagella."""
    k = s / 40
    svg.add(f'<g transform="rotate({angle} {cx:.2f} {cy:.2f})">')
    _r(svg, cx - 14 * k, cy - 6 * k, 28 * k, 12 * k, fill=fill, stroke=ink, sw=1.8 * k, rx=6 * k)
    for dx in (-6, 0, 6):
        _c(svg, cx + dx * k, cy, 1.6 * k, fill=ink, stroke="none", sw=0)
    _p(svg, f"M{cx + 14 * k:.2f},{cy - 2 * k:.2f} q{4 * k:.2f},{-4 * k:.2f} {8 * k:.2f},0 q{3 * k:.2f},{3 * k:.2f} {6 * k:.2f},0", stroke=ink, sw=1.2 * k)
    _p(svg, f"M{cx + 14 * k:.2f},{cy + 3 * k:.2f} q{4 * k:.2f},{4 * k:.2f} {8 * k:.2f},{1 * k:.2f}", stroke=ink, sw=1.2 * k)
    svg.add("</g>")


def fungus(svg, cx, cy, s, ink=INK, fill=LIGHT):
    """Conidiophore-like mould head with a stalk."""
    k = s / 40
    _p(svg, f"M{cx:.2f},{cy + 16 * k:.2f} V{cy + 2 * k:.2f}", stroke=ink, sw=1.8 * k)
    _c(svg, cx, cy - 2 * k, 4.5 * k, fill=fill, stroke=ink, sw=1.6 * k)
    for i in range(10):
        a = math.radians(i * 36 - 90)
        x1, y1 = cx + 5 * k * math.cos(a), cy - 2 * k + 5 * k * math.sin(a)
        x2, y2 = cx + 10.5 * k * math.cos(a), cy - 2 * k + 10.5 * k * math.sin(a)
        _p(svg, f"M{x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f}", stroke=ink, sw=1.3 * k)
        _c(svg, x2, y2, 1.7 * k, fill=fill, stroke=ink, sw=1 * k)


def virus(svg, cx, cy, s, ink=INK, fill=LIGHT):
    """Icosahedral virion: hexagonal capsid with knobbed spikes at the vertices.

    Drawn angular on purpose so it cannot be read as the round, toothed rule cog."""
    k = s / 40
    verts = [(cx + 10 * k * math.cos(math.radians(a)), cy + 10 * k * math.sin(math.radians(a)))
             for a in range(-90, 270, 60)]
    for vx, vy in verts:
        ux, uy = (vx - cx) / (10 * k), (vy - cy) / (10 * k)
        _p(svg, f"M{vx:.2f},{vy:.2f} L{cx + 15 * k * ux:.2f},{cy + 15 * k * uy:.2f}", stroke=ink, sw=1.5 * k)
        _c(svg, cx + 16.5 * k * ux, cy + 16.5 * k * uy, 2.3 * k, fill=ink, stroke="none", sw=0)
    d = "M" + " L".join(f"{vx:.2f},{vy:.2f}" for vx, vy in verts) + " Z"
    _p(svg, d, stroke=ink, sw=1.8 * k, fill=fill)
    # inner facets
    inner = "".join(f"M{cx:.2f},{cy:.2f} L{vx:.2f},{vy:.2f} " for vx, vy in verts[::2])
    _p(svg, inner, stroke=ink, sw=1.0 * k)


def yeast(svg, cx, cy, s, ink=INK, fill=LIGHT):
    """Budding yeast cluster."""
    k = s / 40
    _c(svg, cx, cy + 2 * k, 8 * k, fill=fill, stroke=ink, sw=1.7 * k)
    _c(svg, cx + 8 * k, cy - 6 * k, 5 * k, fill=fill, stroke=ink, sw=1.5 * k)
    _c(svg, cx - 8 * k, cy - 5 * k, 3.5 * k, fill=fill, stroke=ink, sw=1.4 * k)


def mycobacterium(svg, cx, cy, s, ink=INK, fill=LIGHT):
    """Curved, beaded rod."""
    k = s / 40
    d = f"M{cx - 14 * k:.2f},{cy + 4 * k:.2f} Q{cx:.2f},{cy - 12 * k:.2f} {cx + 14 * k:.2f},{cy + 4 * k:.2f}"
    _p(svg, d, stroke=ink, sw=7 * k, fill="none")
    _p(svg, d, stroke=fill, sw=4 * k, fill="none")
    for t in (0.2, 0.5, 0.8):
        # point on the quadratic curve
        px = (1 - t) ** 2 * (cx - 14 * k) + 2 * (1 - t) * t * cx + t ** 2 * (cx + 14 * k)
        py = (1 - t) ** 2 * (cy + 4 * k) + 2 * (1 - t) * t * (cy - 12 * k) + t ** 2 * (cy + 4 * k)
        _c(svg, px, py, 1.3 * k, fill=ink, stroke="none", sw=0)


# ---------------------------------------------------------------- symbols ----------------------
def document(svg, x, y, s, ink=INK, fill=WHITE, lines=4):
    k = s / 40
    _p(svg, f"M{x + 8 * k:.2f},{y + 3 * k:.2f} H{x + 24 * k:.2f} L{x + 32 * k:.2f},{y + 11 * k:.2f} V{y + 37 * k:.2f} H{x + 8 * k:.2f} Z", stroke=ink, sw=1.8 * k, fill=fill)
    _p(svg, f"M{x + 24 * k:.2f},{y + 3 * k:.2f} V{y + 11 * k:.2f} H{x + 32 * k:.2f}", stroke=ink, sw=1.4 * k)
    for i in range(lines):
        yy = y + (17 + i * 5) * k
        _p(svg, f"M{x + 12 * k:.2f},{yy:.2f} H{x + (28 if i % 2 == 0 else 22) * k:.2f}", stroke=ink, sw=1.2 * k)


def check(svg, cx, cy, s, color="#15803d"):
    k = s / 40
    _c(svg, cx, cy, 12 * k, fill=color, stroke="none", sw=0)
    _p(svg, f"M{cx - 6 * k:.2f},{cy:.2f} l{4 * k:.2f},{4 * k:.2f} l{8 * k:.2f},{-9 * k:.2f}", stroke=WHITE, sw=2.6 * k)


def cross(svg, cx, cy, s, color="#b91c1c"):
    k = s / 40
    _c(svg, cx, cy, 12 * k, fill=color, stroke="none", sw=0)
    _p(svg, f"M{cx - 5 * k:.2f},{cy - 5 * k:.2f} l{10 * k:.2f},{10 * k:.2f} M{cx + 5 * k:.2f},{cy - 5 * k:.2f} l{-10 * k:.2f},{10 * k:.2f}", stroke=WHITE, sw=2.6 * k)


def flag(svg, cx, cy, s, color="#d97706"):
    k = s / 40
    _c(svg, cx, cy, 12 * k, fill=color, stroke="none", sw=0)
    _p(svg, f"M{cx - 4 * k:.2f},{cy + 7 * k:.2f} V{cy - 7 * k:.2f} h{9 * k:.2f} l{-3 * k:.2f},{3.5 * k:.2f} l{3 * k:.2f},{3.5 * k:.2f} h{-9 * k:.2f}", stroke=WHITE, sw=1.8 * k, fill=WHITE)


def lock(svg, x, y, s, ink=INK, fill=LIGHT):
    k = s / 40
    _r(svg, x + 8 * k, y + 17 * k, 24 * k, 18 * k, fill=fill, stroke=ink, sw=1.8 * k, rx=3 * k)
    _p(svg, f"M{x + 13 * k:.2f},{y + 17 * k:.2f} V{y + 12 * k:.2f} a{7 * k:.2f},{7 * k:.2f} 0 0 1 {14 * k:.2f},0 V{y + 17 * k:.2f}", stroke=ink, sw=1.8 * k)
    _c(svg, x + 20 * k, y + 26 * k, 2.2 * k, fill=ink, stroke="none", sw=0)


def brain_chip(svg, x, y, s, ink=INK, fill="#ede9fe"):
    """Language-model marker: a chip with a small sparkle."""
    k = s / 40
    _r(svg, x + 8 * k, y + 8 * k, 24 * k, 24 * k, fill=fill, stroke=ink, sw=1.8 * k, rx=4 * k)
    for i in range(3):
        yy = y + (13 + i * 7) * k
        _p(svg, f"M{x + 3 * k:.2f},{yy:.2f} H{x + 8 * k:.2f} M{x + 32 * k:.2f},{yy:.2f} H{x + 37 * k:.2f}", stroke=ink, sw=1.4 * k)
        xx = x + (13 + i * 7) * k
        _p(svg, f"M{xx:.2f},{y + 3 * k:.2f} V{y + 8 * k:.2f} M{xx:.2f},{y + 32 * k:.2f} V{y + 37 * k:.2f}", stroke=ink, sw=1.4 * k)
    _p(svg, f"M{x + 20 * k:.2f},{y + 13 * k:.2f} q{1 * k:.2f},{6 * k:.2f} {7 * k:.2f},{7 * k:.2f} q{-6 * k:.2f},{1 * k:.2f} {-7 * k:.2f},{7 * k:.2f} q{-1 * k:.2f},{-6 * k:.2f} {-7 * k:.2f},{-7 * k:.2f} q{6 * k:.2f},{-1 * k:.2f} {7 * k:.2f},{-7 * k:.2f} Z", stroke=ink, sw=1.2 * k, fill="#a78bfa")


def petri(svg, x, y, s, ink=INK):
    k = s / 40
    _c(svg, x + 20 * k, y + 20 * k, 15 * k, fill="#fef3c7", stroke=ink, sw=1.8 * k)
    _c(svg, x + 20 * k, y + 20 * k, 11.5 * k, fill="none", stroke=ink, sw=0.8 * k)
    for (dx, dy, r) in ((-4, -3, 2.2), (3, -5, 1.8), (5, 3, 2.4), (-3, 5, 1.6), (0, 0, 1.4)):
        _c(svg, x + (20 + dx) * k, y + (20 + dy) * k, r * k, fill="#f59e0b", stroke="none", sw=0)


def table_icon(svg, x, y, s, ink=INK):
    k = s / 40
    _r(svg, x + 4 * k, y + 8 * k, 32 * k, 24 * k, fill=WHITE, stroke=ink, sw=1.8 * k, rx=2 * k)
    _r(svg, x + 4 * k, y + 8 * k, 32 * k, 6 * k, fill="#dbeafe", stroke=ink, sw=1.2 * k, rx=2 * k)
    for i in (1, 2):
        yy = y + (14 + i * 6) * k
        _p(svg, f"M{x + 4 * k:.2f},{yy:.2f} H{x + 36 * k:.2f}", stroke=ink, sw=1 * k)
    for xx in (14, 25):
        _p(svg, f"M{x + xx * k:.2f},{y + 8 * k:.2f} V{y + 32 * k:.2f}", stroke=ink, sw=1 * k)


def person(svg, cx, cy, s, ink=INK, fill=LIGHT):
    k = s / 40
    _c(svg, cx, cy - 9 * k, 6 * k, fill=fill, stroke=ink, sw=1.8 * k)
    _p(svg, f"M{cx - 12 * k:.2f},{cy + 14 * k:.2f} a{12 * k:.2f},{12 * k:.2f} 0 0 1 {24 * k:.2f},0 Z", stroke=ink, sw=1.8 * k, fill=fill)


def sieve(svg, x, y, w, h, ink=INK, fill=PALE):
    """A horizontal filter bar with a mesh pattern."""
    _r(svg, x, y, w, h, fill=fill, stroke=ink, sw=1.6, rx=3)
    for i in range(1, int(w // 10)):
        xx = x + i * 10
        _p(svg, f"M{xx:.2f},{y + 3:.2f} V{y + h - 3:.2f}", stroke="#cbd5e1", sw=0.8)


def cog(svg, x, y, s, ink=INK, fill=LIGHT, teeth=8):
    """Deterministic-rule marker: a cog wheel."""
    k = s / 40
    cx, cy = x + 20 * k, y + 20 * k
    ro, ri, rh = 15 * k, 11 * k, 4.5 * k
    pts = []
    n = teeth * 2
    for i in range(n):
        a0 = math.radians(i * 360 / n - 90)
        a1 = math.radians((i + 1) * 360 / n - 90)
        r = ro if i % 2 == 0 else ri
        pts.append((cx + r * math.cos(a0), cy + r * math.sin(a0)))
        pts.append((cx + r * math.cos(a1), cy + r * math.sin(a1)))
    d = "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts) + " Z"
    _p(svg, d, stroke=ink, sw=1.6 * k, fill=fill)
    _c(svg, cx, cy, rh, fill=WHITE, stroke=ink, sw=1.6 * k)


def magnifier(svg, x, y, s, ink=INK, fill=WHITE):
    """Search marker: a magnifying glass."""
    k = s / 40
    _c(svg, x + 16 * k, y + 16 * k, 10 * k, fill=fill, stroke=ink, sw=2 * k)
    _p(svg, f"M{x + 23.5 * k:.2f},{y + 23.5 * k:.2f} L{x + 35 * k:.2f},{y + 35 * k:.2f}", stroke=ink, sw=3 * k)


def antibody(svg, cx, cy, s, ink=INK, accent="#0f766e"):
    """Y-shaped immunoglobulin (serology marker)."""
    k = s / 40
    _p(svg, f"M{cx:.2f},{cy + 16 * k:.2f} V{cy:.2f} M{cx:.2f},{cy:.2f} L{cx - 11 * k:.2f},{cy - 14 * k:.2f} "
            f"M{cx:.2f},{cy:.2f} L{cx + 11 * k:.2f},{cy - 14 * k:.2f}", stroke=ink, sw=3.2 * k)
    _p(svg, f"M{cx - 3 * k:.2f},{cy - 4 * k:.2f} L{cx - 14 * k:.2f},{cy - 18 * k:.2f} "
            f"M{cx + 3 * k:.2f},{cy - 4 * k:.2f} L{cx + 14 * k:.2f},{cy - 18 * k:.2f}", stroke=accent, sw=2.4 * k)


def bottle(svg, x, y, s, ink=INK, growth=False, accent="#f59e0b"):
    """Blood-culture bottle; growth draws colonies in the broth."""
    k = s / 40
    _r(svg, x + 15 * k, y + 2 * k, 10 * k, 7 * k, fill="#9ca3af", stroke=ink, sw=1.4 * k, rx=1.5 * k)
    _p(svg, f"M{x + 12 * k:.2f},{y + 9 * k:.2f} H{x + 28 * k:.2f} V{y + 14 * k:.2f} L{x + 32 * k:.2f},{y + 19 * k:.2f} "
            f"V{y + 34 * k:.2f} a{4 * k:.2f},{4 * k:.2f} 0 0 1 {-4 * k:.2f},{4 * k:.2f} H{x + 12 * k:.2f} "
            f"a{4 * k:.2f},{4 * k:.2f} 0 0 1 {-4 * k:.2f},{-4 * k:.2f} V{y + 19 * k:.2f} Z", stroke=ink, sw=1.8 * k, fill=WHITE)
    _r(svg, x + 10 * k, y + 24 * k, 20 * k, 12 * k, fill="#fef3c7" if growth else "#f3f4f6", stroke="none", sw=0, rx=2 * k)
    if growth:
        for (dx, dy, r) in ((14, 28, 2.2), (20, 31, 1.8), (25, 27, 2.0), (17, 33, 1.5)):
            _c(svg, x + dx * k, y + dy * k, r * k, fill=accent, stroke="none", sw=0)


def site_pin(svg, x, y, s, ink=INK, fill=LIGHT):
    """Specimen-site marker: a map pin."""
    k = s / 40
    _p(svg, f"M{x + 20 * k:.2f},{y + 37 * k:.2f} C{x + 20 * k:.2f},{y + 28 * k:.2f} {x + 33 * k:.2f},{y + 25 * k:.2f} "
            f"{x + 33 * k:.2f},{y + 16 * k:.2f} a{13 * k:.2f},{13 * k:.2f} 0 1 0 {-26 * k:.2f},0 "
            f"C{x + 7 * k:.2f},{y + 25 * k:.2f} {x + 20 * k:.2f},{y + 28 * k:.2f} {x + 20 * k:.2f},{y + 37 * k:.2f} Z",
       stroke=ink, sw=1.8 * k, fill=fill)
    _c(svg, x + 20 * k, y + 16 * k, 5 * k, fill=WHITE, stroke=ink, sw=1.6 * k)


def fingerprint(svg, x, y, s, ink=INK):
    """Traceability marker: nested fingerprint arcs."""
    k = s / 40
    for i, r in enumerate((5, 9.5, 14)):
        _p(svg, f"M{x + (20 - r) * k:.2f},{y + 22 * k:.2f} a{r * k:.2f},{r * k:.2f} 0 0 1 {2 * r * k:.2f},0",
           stroke=ink, sw=1.6 * k)
        if i:
            _p(svg, f"M{x + (20 - r) * k:.2f},{y + 22 * k:.2f} V{y + (22 + r * 0.7) * k:.2f} "
                    f"M{x + (20 + r) * k:.2f},{y + 22 * k:.2f} V{y + (22 + r * 0.7) * k:.2f}", stroke=ink, sw=1.6 * k)
    _p(svg, f"M{x + 20 * k:.2f},{y + 17 * k:.2f} V{y + 30 * k:.2f}", stroke=ink, sw=1.6 * k)


def shield(svg, x, y, s, ink=INK, fill="#fef3c7"):
    """Guardrail marker: a shield."""
    k = s / 40
    _p(svg, f"M{x + 20 * k:.2f},{y + 5 * k:.2f} L{x + 34 * k:.2f},{y + 11 * k:.2f} V{y + 22 * k:.2f} "
            f"C{x + 34 * k:.2f},{y + 30 * k:.2f} {x + 27 * k:.2f},{y + 34 * k:.2f} {x + 20 * k:.2f},{y + 36 * k:.2f} "
            f"C{x + 13 * k:.2f},{y + 34 * k:.2f} {x + 6 * k:.2f},{y + 30 * k:.2f} {x + 6 * k:.2f},{y + 22 * k:.2f} "
            f"V{y + 11 * k:.2f} Z", stroke=ink, sw=1.8 * k, fill=fill)
    _p(svg, f"M{x + 13 * k:.2f},{y + 20 * k:.2f} H{x + 27 * k:.2f}", stroke=ink, sw=1.8 * k)


def no_entry(svg, cx, cy, s, color="#b91c1c", fill=WHITE):
    """Blocked action: a circle with a bar."""
    k = s / 40
    _c(svg, cx, cy, 13 * k, fill=fill, stroke=color, sw=2.6 * k)
    _p(svg, f"M{cx - 7 * k:.2f},{cy:.2f} H{cx + 7 * k:.2f}", stroke=color, sw=2.6 * k)


def dna(svg, x, y, s, ink=INK, accent="#7c3aed"):
    """Targeted molecular assay: a tube holding a short double helix."""
    k = s / 40
    _p(svg, f"M{x + 12 * k:.2f},{y + 6 * k:.2f} V{y + 30 * k:.2f} A{8 * k:.2f},{8 * k:.2f} 0 0 0 {x + 28 * k:.2f},{y + 30 * k:.2f} V{y + 6 * k:.2f}",
       stroke=ink, sw=1.8 * k, fill=WHITE)
    _r(svg, x + 10 * k, y + 3 * k, 20 * k, 5 * k, fill="#9ca3af", stroke=ink, sw=1.3 * k, rx=1.5 * k)
    pts_a, pts_b = [], []
    for i in range(13):
        t = i / 12
        yy = y + (11 + t * 24) * k
        off = 5.5 * k * math.sin(t * 2 * math.pi * 1.25)
        pts_a.append((x + 20 * k + off, yy)); pts_b.append((x + 20 * k - off, yy))
    for i in (1, 4, 7, 10):
        _p(svg, f"M{pts_a[i][0]:.2f},{pts_a[i][1]:.2f} L{pts_b[i][0]:.2f},{pts_b[i][1]:.2f}", stroke="#9ca3af", sw=1.0 * k)
    for pts in (pts_a, pts_b):
        _p(svg, "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts), stroke=accent, sw=1.6 * k)


def clock(svg, x, y, s, ink=INK, fill=WHITE):
    """Timing marker: a clock face."""
    k = s / 40
    _c(svg, x + 20 * k, y + 20 * k, 15 * k, fill=fill, stroke=ink, sw=2.2 * k)
    _p(svg, f"M{x + 20 * k:.2f},{y + 11 * k:.2f} V{y + 20 * k:.2f} L{x + 27 * k:.2f},{y + 24 * k:.2f}", stroke=ink, sw=2.2 * k)


def unknown(svg, cx, cy, s, color="#d97706"):
    """Open circle with a question mark (possible, not established)."""
    k = s / 40
    _c(svg, cx, cy, 12 * k, fill=WHITE, stroke=color, sw=2.6 * k)
    # question mark as a stroked path (not text), so no glyph falls below the print minimum
    _p(svg, f"M{cx - 4 * k:.2f},{cy - 3.5 * k:.2f} a{4 * k:.2f},{4 * k:.2f} 0 1 1 {5.5 * k:.2f},{3.7 * k:.2f} "
            f"c{-1.5 * k:.2f},{0.8 * k:.2f} {-1.5 * k:.2f},{1.8 * k:.2f} {-1.5 * k:.2f},{3.3 * k:.2f}", stroke=color, sw=2.6 * k)
    _c(svg, cx, cy + 7 * k, 1.6 * k, fill=color, stroke="none", sw=0)
