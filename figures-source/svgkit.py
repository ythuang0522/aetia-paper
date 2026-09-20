"""Minimal SVG helpers shared by the figure scripts (no third-party dependencies).

Conventions (journal figure, printed on white): Helvetica/Arial, hairline recessive axes,
bars <= 24 px thick with a 4 px rounded data-end and a square base, 2 px surface gaps
between touching bars, text in ink tokens (never in a series colour).
"""
from __future__ import annotations

from pathlib import Path

FONT = "Helvetica, Arial, sans-serif"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#ffffff"

# Categorical slots (validated with the dataviz palette validator on #ffffff:
# adjacent CVD dE 9.2, normal-vision dE 27.6; aqua needs direct labels, which every bar carries).
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
VIOLET = "#4a3aa7"
RED = "#e34948"
NEUTRAL = "#b9b7ae"      # de-emphasised bars (non-highlighted entities)
LIGHTBLUE = "#cde2fb"    # box fills in schematics
LIGHTGREY = "#f1f0ec"


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class SVG:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.parts: list[str] = []

    # --- primitives -------------------------------------------------------------
    def add(self, s: str) -> None:
        self.parts.append(s)

    def rect(self, x, y, w, h, fill, stroke="none", sw=0, rx=0, opacity=1.0, extra="") -> None:
        self.add(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" {extra}/>'
        )

    def bar(self, x, y_top, w, y_base, fill, r=4.0) -> None:
        """Column with a rounded top (data end) and a square base."""
        h = y_base - y_top
        if h <= 0.01:
            return
        r = min(r, w / 2, h)
        d = (
            f"M{x:.2f},{y_base:.2f} V{y_top + r:.2f} "
            f"Q{x:.2f},{y_top:.2f} {x + r:.2f},{y_top:.2f} "
            f"H{x + w - r:.2f} Q{x + w:.2f},{y_top:.2f} {x + w:.2f},{y_top + r:.2f} "
            f"V{y_base:.2f} Z"
        )
        self.add(f'<path d="{d}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, stroke=AXIS, sw=1.0, dash="", cap="butt") -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{dash_attr}/>'
        )

    def path(self, d, stroke=INK2, sw=1.2, fill="none", extra="") -> None:
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" {extra}/>')

    def circle(self, cx, cy, r, fill, stroke="none", sw=0) -> None:
        self.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=9, fill=INK, anchor="start", weight="normal", style="normal",
             rotate=None, baseline="alphabetic", family=FONT, letter=None) -> None:
        tr = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate is not None else ""
        ls = f' letter-spacing="{letter}"' if letter is not None else ""
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" font-style="{style}" '
            f'dominant-baseline="{baseline}"{ls}{tr}>{esc(s)}</text>'
        )

    def rich(self, x, y, runs, size=9, fill=INK, anchor="start", baseline="alphabetic") -> None:
        """Text with mixed runs: list of (string, {'style':'italic','weight':'bold'})."""
        spans = []
        for s, attrs in runs:
            a = " ".join(f'{k}="{v}"' for k, v in (attrs or {}).items())
            spans.append(f"<tspan {a}>{esc(s)}</tspan>")
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" dominant-baseline="{baseline}">{"".join(spans)}</text>'
        )

    def panel_label(self, x, y, letter, size=12) -> None:
        self.text(x, y, letter, size=size, weight="bold")

    def arrow(self, x1, y1, x2, y2, stroke=INK2, sw=1.2, head=5.0) -> None:
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        bx = x2 - head * math.cos(ang)
        by = y2 - head * math.sin(ang)
        self.line(x1, y1, bx, by, stroke=stroke, sw=sw)
        left = (x2 - head * math.cos(ang - 0.5), y2 - head * math.sin(ang - 0.5))
        right = (x2 - head * math.cos(ang + 0.5), y2 - head * math.sin(ang + 0.5))
        self.add(
            f'<path d="M{x2:.2f},{y2:.2f} L{left[0]:.2f},{left[1]:.2f} L{right[0]:.2f},{right[1]:.2f} Z" '
            f'fill="{stroke}"/>'
        )

    def box(self, x, y, w, h, lines, fill=LIGHTGREY, stroke="#c9c7bf", size=8.5, rx=4,
            title=None, title_size=9, ink=INK, line_gap=None, italic_words=()) -> None:
        """Rounded box with centred text lines; optional bold title line."""
        self.rect(x, y, w, h, fill, stroke=stroke, sw=0.8, rx=rx)
        gap = line_gap or size * 1.32
        n = len(lines) + (1 if title else 0)
        y0 = y + h / 2 - (n - 1) * gap / 2
        cx = x + w / 2
        if title:
            self.text(cx, y0, title, size=title_size, weight="bold", anchor="middle", baseline="middle", fill=ink)
            y0 += gap
        for i, s in enumerate(lines):
            self.text(cx, y0 + i * gap, s, size=size, anchor="middle", baseline="middle", fill=ink)

    # --- axes ---------------------------------------------------------------------
    def yaxis_pct(self, x0, x1, y_of, ticks, size=8, label=None, label_x=None, grid=True, fmt="{:.0f}"):
        for t in ticks:
            y = y_of(t)
            if grid and t != ticks[0]:
                self.line(x0, y, x1, y, stroke=GRID, sw=0.8)
            self.line(x0 - 3, y, x0, y, stroke=AXIS, sw=0.8)
            self.text(x0 - 5, y, fmt.format(t), size=size, fill=INK2, anchor="end", baseline="middle")
        self.line(x0, y_of(ticks[0]), x0, y_of(ticks[-1]), stroke=AXIS, sw=0.8)
        if label:
            lx = label_x if label_x is not None else x0 - 28
            ly = (y_of(ticks[0]) + y_of(ticks[-1])) / 2
            self.text(lx, ly, label, size=size + 0.5, fill=INK2, anchor="middle", baseline="middle", rotate=-90)

    def legend(self, x, y, items, size=8, swatch=9, gap=14, horizontal=True) -> None:
        cx = x
        cy = y
        for label, color in items:
            self.rect(cx, cy - swatch / 2, swatch, swatch, color, rx=2)
            self.text(cx + swatch + 4, cy, label, size=size, fill=INK2, baseline="middle")
            if horizontal:
                cx += swatch + 4 + len(label) * size * 0.55 + gap
            else:
                cy += gap

    # --- output -------------------------------------------------------------------
    def render(self) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">\n'
            f'<rect width="{self.width}" height="{self.height}" fill="{SURFACE}"/>\n'
        )
        return head + "\n".join(self.parts) + "\n</svg>\n"

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        print(f"wrote {path}")


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """CSV reader that skips '#' comment lines (stdlib only)."""
    import csv
    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        lines = [ln for ln in handle if not ln.lstrip().startswith("#")]
    for row in csv.DictReader(lines):
        rows.append(row)
    return rows
