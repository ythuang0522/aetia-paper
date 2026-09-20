"""Chart primitives for the manuscript figures: precision-recall plane with iso-F1 curves,
grouped bars, single-series bars. Print-oriented (Nature double column = 1000 units)."""
from __future__ import annotations

from svgkit import SVG, AXIS, GRID, INK, INK2, MUTED

FS = 13


def marker(svg, cx, cy, shape, fill, r=7.0, ring="#ffffff"):
    """Marker with a 2-unit surface ring so overlapping points stay legible."""
    if shape == "circle":
        svg.circle(cx, cy, r + 2, ring); svg.circle(cx, cy, r, fill)
    elif shape == "square":
        svg.rect(cx - r - 2, cy - r - 2, 2 * r + 4, 2 * r + 4, ring, rx=2); svg.rect(cx - r, cy - r, 2 * r, 2 * r, fill, rx=1.5)
    elif shape == "triangle":
        for rr, col in ((r + 2.5, ring), (r, fill)):
            svg.add(f'<path d="M{cx:.2f},{cy - rr * 1.15:.2f} L{cx + rr * 1.1:.2f},{cy + rr * 0.75:.2f} L{cx - rr * 1.1:.2f},{cy + rr * 0.75:.2f} Z" fill="{col}"/>')
    elif shape == "diamond":
        for rr, col in ((r + 2.5, ring), (r, fill)):
            svg.add(f'<path d="M{cx:.2f},{cy - rr * 1.2:.2f} L{cx + rr * 1.2:.2f},{cy:.2f} L{cx:.2f},{cy + rr * 1.2:.2f} L{cx - rr * 1.2:.2f},{cy:.2f} Z" fill="{col}"/>')


def pr_plane(svg, x0, y0, w, h, points, iso=(20, 40, 60, 80), fs=FS, xlabel="Recall (%)", ylabel="Precision (%)"):
    """points: list of dicts {label, recall, precision, shape, color, dx, dy, anchor, bold}."""
    xr = lambda r: x0 + (r / 100.0) * w
    yp = lambda p: y0 + h - (p / 100.0) * h
    # grid + axes
    for t in range(0, 101, 20):
        svg.line(x0, yp(t), x0 + w, yp(t), stroke=GRID, sw=0.8)
        svg.line(xr(t), y0, xr(t), y0 + h, stroke=GRID, sw=0.8)
        svg.text(x0 - 6, yp(t), str(t), size=fs - 1, fill=INK2, anchor="end", baseline="middle")
        svg.text(xr(t), y0 + h + 15, str(t), size=fs - 1, fill=INK2, anchor="middle")
    svg.line(x0, y0, x0, y0 + h, stroke=AXIS, sw=1)
    svg.line(x0, y0 + h, x0 + w, y0 + h, stroke=AXIS, sw=1)
    svg.text(x0 + w / 2, y0 + h + 34, xlabel, size=fs, fill=INK2, anchor="middle")
    svg.text(x0 - 46, y0 + h / 2, ylabel, size=fs, fill=INK2, anchor="middle", baseline="middle", rotate=-90)
    # iso-F1 curves: P = F R / (2R - F)
    for F in iso:
        pts = []
        r = F / 2.0 + 0.4
        while r <= 100.0001:
            p = F * r / (2 * r - F)
            if p <= 100:
                pts.append((xr(r), yp(p)))
            r += 0.5
        if pts:
            d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
            svg.path(d, stroke="#9ca3af", sw=0.9, extra='stroke-dasharray="4 3"')
            ex, ey = pts[-1]
            svg.text(ex + 4, ey, f"F1 {F}", size=fs - 3, fill=MUTED, baseline="middle")
    # points
    for pt in points:
        cx, cy = xr(pt["recall"]), yp(pt["precision"])
        marker(svg, cx, cy, pt.get("shape", "circle"), pt["color"], r=pt.get("r", 7))
        svg.text(cx + pt.get("dx", 10), cy + pt.get("dy", 4), pt["label"], size=fs - 1, fill=INK,
                 anchor=pt.get("anchor", "start"), weight="bold" if pt.get("bold") else "normal")


def grouped_bars(svg, x0, y0, w, h, groups, series, bar_w=22, gap=3, fs=FS, ylabel="Score (%)", value_fmt="{:.1f}",
                 sub_labels=None, ymax=100, ticks=(0, 20, 40, 60, 80, 100)):
    """groups: list of (label, {series_key: value}); series: list of (name, key, color)."""
    y_of = lambda v: y0 + h - (v / ymax) * h
    for t in ticks:
        if t:
            svg.line(x0, y_of(t), x0 + w, y_of(t), stroke=GRID, sw=0.8)
        svg.line(x0 - 3, y_of(t), x0, y_of(t), stroke=AXIS, sw=0.8)
        svg.text(x0 - 6, y_of(t), str(t), size=fs - 1, fill=INK2, anchor="end", baseline="middle")
    svg.line(x0, y0, x0, y0 + h, stroke=AXIS, sw=1)
    svg.line(x0, y0 + h, x0 + w, y0 + h, stroke=AXIS, sw=1)
    svg.text(x0 - 46, y0 + h / 2, ylabel, size=fs, fill=INK2, anchor="middle", baseline="middle", rotate=-90)
    slot = w / len(groups)
    gw = len(series) * bar_w + (len(series) - 1) * gap
    for gi, (glabel, vals) in enumerate(groups):
        gx = x0 + slot * gi + (slot - gw) / 2
        for si, (name, key, color) in enumerate(series):
            v = float(vals[key])
            x = gx + si * (bar_w + gap)
            svg.bar(x, y_of(v), bar_w, y0 + h, color, r=4)
            svg.text(x + bar_w / 2, y_of(v) - 4, value_fmt.format(v), size=fs - 3, fill=INK2, anchor="middle")
        svg.text(gx + gw / 2, y0 + h + 17, glabel, size=fs - 1, fill=INK, anchor="middle")
        if sub_labels and sub_labels[gi]:
            svg.text(gx + gw / 2, y0 + h + 31, sub_labels[gi], size=fs - 4, fill=MUTED, anchor="middle")


def single_bars(svg, x0, y0, w, h, items, ymax, ticks, ylabel, fs=FS, bar_w=24, value_fmt="{:.0f}", tick_fmt="{:.0f}",
                highlight="AETIA", hi_color="#1d4ed8", base_color="#b9b7ae", rotate_labels=True):
    """items: list of (label, value)."""
    y_of = lambda v: y0 + h - (v / ymax) * h
    for t in ticks:
        if t:
            svg.line(x0, y_of(t), x0 + w, y_of(t), stroke=GRID, sw=0.8)
        svg.line(x0 - 3, y_of(t), x0, y_of(t), stroke=AXIS, sw=0.8)
        svg.text(x0 - 6, y_of(t), tick_fmt.format(t), size=fs - 1, fill=INK2, anchor="end", baseline="middle")
    svg.line(x0, y0, x0, y0 + h, stroke=AXIS, sw=1)
    svg.line(x0, y0 + h, x0 + w, y0 + h, stroke=AXIS, sw=1)
    svg.text(x0 - 46, y0 + h / 2, ylabel, size=fs, fill=INK2, anchor="middle", baseline="middle", rotate=-90)
    slot = w / len(items)
    for i, (label, v) in enumerate(items):
        x = x0 + slot * i + (slot - bar_w) / 2
        color = hi_color if label == highlight else base_color
        svg.bar(x, y_of(v), bar_w, y0 + h, color, r=4)
        svg.text(x + bar_w / 2, y_of(v) - 4, value_fmt.format(v), size=fs - 3, fill=INK2, anchor="middle")
        if rotate_labels:
            svg.text(x + bar_w / 2 + 4, y0 + h + 10, label, size=fs - 1, fill=INK, anchor="end", rotate=-35)
        else:
            svg.text(x + bar_w / 2, y0 + h + 17, label, size=fs - 1, fill=INK, anchor="middle")
