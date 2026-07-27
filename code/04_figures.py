#!/usr/bin/env python3
"""Render the trajectory figure as both PDF and PNG."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.pdfgen import canvas

EVENTS = ["P1", "P2", "P3", "P4"]
NEG_COLOR = (70, 70, 70)
POS_COLOR = (150, 150, 150)
GRID_COLOR = (224, 224, 224)
BLACK = (0, 0, 0)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if row["condition"] == "source"]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    values = sorted(values)
    n = len(values)
    mid = n // 2
    if n % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def covariance(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def grouped_profiles(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_pianist: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_pianist[row["pianist"]][row["pause"]] = row
    profiles = []
    for pianist in sorted(by_pianist):
        event_map = by_pianist[pianist]
        ds = [float(event_map[event]["d_s"]) for event in EVENTS]
        dl = [float(event_map[event]["d_l"]) for event in EVENTS]
        profiles.append(
            {
                "pianist": pianist,
                "dl": dl,
                "sign": "negative" if covariance(ds, dl) < 0 else "positive",
            }
        )
    return profiles


def y_map(value: float, top: float, height: float, max_y: float) -> float:
    return top + height - (value / max_y) * height


def y_map_pdf(value: float, bottom: float, height: float, max_y: float) -> float:
    return bottom + (value / max_y) * height


def dash_segments(points: list[tuple[float, float]], dash: float = 8.0, gap: float = 5.0) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    segments = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        dx = x2 - x1
        dy = y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            continue
        pos = 0.0
        while pos < length:
            start = pos / length
            end = min(length, pos + dash) / length
            sx = x1 + dx * start
            sy = y1 + dy * start
            ex = x1 + dx * end
            ey = y1 + dy * end
            segments.append(((sx, sy), (ex, ey)))
            pos += dash + gap
    return segments


def render_png(out_path: Path, profiles: list[dict[str, object]]) -> None:
    width, height = 940, 550
    left, top = 120, 50
    plot_w, plot_h = 700, 430
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    max_y = max(max(profile["dl"]) for profile in profiles)
    x_positions = [left + i * (plot_w / (len(EVENTS) - 1)) for i in range(len(EVENTS))]

    for i in range(5):
        y_val = float(i)
        y = y_map(y_val, top, plot_h, max_y)
        draw.line((left, y, left + plot_w, y), fill=GRID_COLOR, width=1)
        draw.text((left - 32, y - 6), f"{y_val:.1f}", fill=BLACK, font=font)
    draw.line((left, top, left, top + plot_h), fill=BLACK, width=1)
    draw.line((left, top + plot_h, left + plot_w, top + plot_h), fill=BLACK, width=1)
    draw.text((left + plot_w // 2 - 18, top + plot_h + 34), "Pause", fill=BLACK, font=font)
    draw.text((20, top + plot_h // 2), "d_l (s)", fill=BLACK, font=font)
    for x, event in zip(x_positions, EVENTS):
        draw.line((x, top, x, top + plot_h), fill=GRID_COLOR, width=1)
        draw.text((x - 10, top + plot_h + 12), event, fill=BLACK, font=font)

    for profile in profiles:
        pts = [(x_positions[i], y_map(profile["dl"][i], top, plot_h, max_y)) for i in range(len(EVENTS))]
        if profile["sign"] == "negative":
            draw.line(pts, fill=NEG_COLOR, width=2)
        else:
            for segment in dash_segments(pts):
                draw.line((*segment[0], *segment[1]), fill=POS_COLOR, width=2)

    for sign, color, y_offset in [("negative", NEG_COLOR, 0), ("positive", POS_COLOR, 18)]:
        group = [profile["dl"] for profile in profiles if profile["sign"] == sign]
        if not group:
            continue
        med = [median([vals[i] for vals in group]) for i in range(len(EVENTS))]
        pts = [(x_positions[i], y_map(med[i], top, plot_h, max_y)) for i in range(len(EVENTS))]
        if sign == "negative":
            draw.line(pts, fill=color, width=4)
        else:
            for segment in dash_segments(pts, dash=12, gap=6):
                draw.line((*segment[0], *segment[1]), fill=color, width=4)

    all_med = [median([profile["dl"][i] for profile in profiles]) for i in range(len(EVENTS))]
    med_pts = [(x_positions[i], y_map(all_med[i], top, plot_h, max_y)) for i in range(len(EVENTS))]
    draw.line(med_pts, fill=BLACK, width=4)
    for x, y in med_pts:
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=BLACK)

    legend_x = left + plot_w + 26
    legend_y = top + 40
    legend = [
        ("neg. traj.", NEG_COLOR, "solid", 2),
        ("neg. med.", NEG_COLOR, "solid", 4),
        ("pos. traj.", POS_COLOR, "dash", 2),
        ("pos. med.", POS_COLOR, "dash", 4),
        ("all med.", BLACK, "solid", 4),
    ]
    for index, (label, color, style, line_width) in enumerate(legend):
        y = legend_y + index * 24
        if style == "dash":
            for segment in dash_segments([(legend_x, y), (legend_x + 36, y)], dash=8, gap=5):
                draw.line((*segment[0], *segment[1]), fill=color, width=line_width)
        else:
            draw.line((legend_x, y, legend_x + 36, y), fill=color, width=line_width)
        draw.text((legend_x + 44, y - 6), label, fill=BLACK, font=font)
    img.save(out_path)


def set_stroke_pdf(pdf: canvas.Canvas, rgb: tuple[int, int, int], width: float = 1.0, dash: tuple[int, int] | None = None) -> None:
    pdf.setStrokeColor(colors.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
    pdf.setLineWidth(width)
    if dash is None:
        pdf.setDash()
    else:
        pdf.setDash(dash[0], dash[1])


def render_pdf(out_path: Path, profiles: list[dict[str, object]]) -> None:
    width, height = 520, 340
    pdf = canvas.Canvas(str(out_path), pagesize=(width, height))
    left, top = 62, height - 22
    plot_w, plot_h = 350, 270
    max_y = max(max(profile["dl"]) for profile in profiles)
    x_positions = [left + i * (plot_w / (len(EVENTS) - 1)) for i in range(len(EVENTS))]

    pdf.setFont("Helvetica", 8)

    for i in range(5):
        y_val = float(i)
        y = y_map_pdf(y_val, top - plot_h, plot_h, max_y)
        set_stroke_pdf(pdf, GRID_COLOR, 0.6)
        pdf.line(left, y, left + plot_w, y)
        pdf.setFillColor(colors.black)
        pdf.drawRightString(left - 8, y - 3, f"{y_val:.1f}")
    set_stroke_pdf(pdf, BLACK, 1.0)
    pdf.line(left, top - plot_h, left, top)
    pdf.line(left, top - plot_h, left + plot_w, top - plot_h)
    pdf.drawCentredString(left + plot_w / 2, top - plot_h - 32, "Pause")
    pdf.drawString(left - 52, top - plot_h / 2, "d_l (s)")
    for x, event in zip(x_positions, EVENTS):
        set_stroke_pdf(pdf, GRID_COLOR, 0.6)
        pdf.line(x, top - plot_h, x, top)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(x, top - plot_h - 14, event)

    for profile in profiles:
        pts = [(x_positions[i], y_map_pdf(profile["dl"][i], top - plot_h, plot_h, max_y)) for i in range(len(EVENTS))]
        if profile["sign"] == "negative":
            set_stroke_pdf(pdf, NEG_COLOR, 1.2)
        else:
            set_stroke_pdf(pdf, POS_COLOR, 1.2, dash=(5, 3))
        path = pdf.beginPath()
        path.moveTo(*pts[0])
        for x, y in pts[1:]:
            path.lineTo(x, y)
        pdf.drawPath(path)

    for sign, color, dash in [("negative", NEG_COLOR, None), ("positive", POS_COLOR, (7, 4))]:
        group = [profile["dl"] for profile in profiles if profile["sign"] == sign]
        if not group:
            continue
        med = [median([vals[i] for vals in group]) for i in range(len(EVENTS))]
        pts = [(x_positions[i], y_map_pdf(med[i], top - plot_h, plot_h, max_y)) for i in range(len(EVENTS))]
        set_stroke_pdf(pdf, color, 2.4, dash=dash)
        path = pdf.beginPath()
        path.moveTo(*pts[0])
        for x, y in pts[1:]:
            path.lineTo(x, y)
        pdf.drawPath(path)

    all_med = [median([profile["dl"][i] for profile in profiles]) for i in range(len(EVENTS))]
    med_pts = [(x_positions[i], y_map_pdf(all_med[i], top - plot_h, plot_h, max_y)) for i in range(len(EVENTS))]
    set_stroke_pdf(pdf, BLACK, 2.4)
    path = pdf.beginPath()
    path.moveTo(*med_pts[0])
    for x, y in med_pts[1:]:
        path.lineTo(x, y)
    pdf.drawPath(path)
    pdf.setFillColor(colors.black)
    for x, y in med_pts:
        pdf.circle(x, y, 2.5, stroke=0, fill=1)

    legend_x = left + plot_w + 18
    legend_y = top - 55
    legend_items = [
        ("neg. traj.", NEG_COLOR, None, 1.2),
        ("neg. med.", NEG_COLOR, None, 2.4),
        ("pos. traj.", POS_COLOR, (5, 3), 1.2),
        ("pos. med.", POS_COLOR, (7, 4), 2.4),
        ("all med.", BLACK, None, 2.4),
    ]
    pdf.setFont("Helvetica", 8)
    for index, (label, color, dash, line_width) in enumerate(legend_items):
        y = legend_y - index * 16
        set_stroke_pdf(pdf, color, line_width, dash=dash)
        pdf.line(legend_x, y, legend_x + 28, y)
        pdf.setFillColor(colors.black)
        pdf.drawString(legend_x + 34, y - 3, label)

    pdf.save()


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    rows = read_rows(base / "data/events.csv")
    profiles = grouped_profiles(rows)
    figures_dir = base / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    render_png(figures_dir / "figure1_trajectories.png", profiles)
    render_pdf(figures_dir / "figure1_trajectories.pdf", profiles)
    print(f"Wrote figure outputs to {figures_dir}")


if __name__ == "__main__":
    main()
