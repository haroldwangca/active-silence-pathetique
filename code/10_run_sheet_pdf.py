#!/usr/bin/env python3
"""Render the live demo recording run sheet as a printable PDF."""

from __future__ import annotations

import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "live_recording_run_sheet.md"
OUTPUT = ROOT / "docs" / "live_recording_run_sheet.pdf"


def page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(
        letter[0] - 0.55 * inch,
        0.36 * inch,
        f"Live recording run sheet - page {doc.page}",
    )
    canvas.restoreState()


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "RunSheetTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1f2933"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "RunSheetSubtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#4b5563"),
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "RunSheetH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "RunSheetBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.2,
            textColor=colors.HexColor("#111827"),
            spaceAfter=5,
        ),
        "label": ParagraphStyle(
            "RunSheetLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.8,
            leading=11,
            textColor=colors.HexColor("#374151"),
            spaceBefore=4,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "RunSheetQuote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.3,
            leading=12.6,
            leftIndent=12,
            rightIndent=6,
            borderColor=colors.HexColor("#cbd5e1"),
            borderWidth=0,
            borderPadding=0,
            textColor=colors.HexColor("#111827"),
            spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "RunSheetBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=11.5,
            textColor=colors.HexColor("#111827"),
            leftIndent=12,
        ),
        "code": ParagraphStyle(
            "RunSheetCode",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.8,
            leading=9.6,
            textColor=colors.HexColor("#111827"),
            backColor=colors.HexColor("#f3f4f6"),
            borderColor=colors.HexColor("#d1d5db"),
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=3,
            spaceAfter=8,
        ),
    }
    return styles


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    parts = escaped.split("`")
    for i in range(1, len(parts), 2):
        parts[i] = f'<font name="Courier">{parts[i]}</font>'
    return "".join(parts)


def flush_bullets(story, bullets, styles):
    if not bullets:
        return
    items = [
        ListItem(Paragraph(inline_markup(item), styles["bullet"]), leftIndent=8)
        for item in bullets
    ]
    story.append(
        ListFlowable(
            items,
            bulletType="bullet",
            start="circle",
            leftIndent=14,
            bulletFontName="Helvetica",
            bulletFontSize=6,
            spaceAfter=4,
        )
    )
    bullets.clear()


def render_markdown(md: str):
    styles = make_styles()
    story = []
    bullets: list[str] = []
    code_lines: list[str] = []
    in_code = False

    for raw in md.splitlines():
        line = raw.rstrip()

        if line.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["code"]))
                code_lines = []
                in_code = False
            else:
                flush_bullets(story, bullets, styles)
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line:
            flush_bullets(story, bullets, styles)
            story.append(Spacer(1, 3))
            continue

        if line.startswith("# "):
            flush_bullets(story, bullets, styles)
            story.append(Paragraph(inline_markup(line[2:]), styles["title"]))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1")))
            story.append(Spacer(1, 7))
            continue

        if line.startswith("## "):
            flush_bullets(story, bullets, styles)
            title = line[3:]
            block = [
                Paragraph(inline_markup(title), styles["h2"]),
                HRFlowable(width="100%", thickness=0.35, color=colors.HexColor("#e5e7eb")),
            ]
            story.append(KeepTogether(block))
            continue

        if line.startswith("- "):
            bullets.append(line[2:])
            continue

        flush_bullets(story, bullets, styles)

        if line.startswith("> "):
            story.append(Paragraph(inline_markup(line[2:]), styles["quote"]))
        elif line.endswith(":") and len(line) < 35:
            story.append(Paragraph(inline_markup(line), styles["label"]))
        else:
            story.append(Paragraph(inline_markup(line), styles["body"]))

    flush_bullets(story, bullets, styles)
    if code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["code"]))

    return story


def main() -> None:
    md = SOURCE.read_text(encoding="utf-8")
    story = render_markdown(md)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Live Recording Run Sheet",
        author="Harold Wang",
    )
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
