from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas

from backend.colors.palette import color_for_feature
from backend.core.models import ColorMode, GenerationOptions
from backend.layout.pagination import CardKind, FeaturePrintJob, PrintableCard
from backend.pdf.constants import (
    CARD_BORDER_WIDTH,
    CARD_HEIGHT,
    CARD_PADDING,
    CARD_PADDING_WITH_BORDER,
    CARD_WIDTH,
    FONT_BOLD,
    FONT_REGULAR,
    PAGE_HEIGHT,
    PAGE_MARGIN_X,
    PAGE_MARGIN_Y,
    PAGE_WIDTH,
)


def render_feature_pdf(
    print_job: FeaturePrintJob,
    output_path: str | Path,
    options: GenerationOptions | None = None,
) -> Path:
    """Render one Feature print job to a deterministic A4 PDF."""
    generation_options = options or GenerationOptions()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(output), pagesize=(PAGE_WIDTH, PAGE_HEIGHT), pageCompression=0)
    canvas.setTitle(print_job.feature.label)
    canvas.setAuthor("jira-card-generator")

    for page in print_job.pages:
        for index, card in enumerate(page.cards):
            x, y = _card_position(index)
            _draw_card(canvas, card, x, y, generation_options)
        canvas.showPage()

    canvas.save()
    return output


def _card_position(index: int) -> tuple[float, float]:
    column = index % 2
    row = index // 2
    x = PAGE_MARGIN_X + (column * CARD_WIDTH)
    y = PAGE_HEIGHT - PAGE_MARGIN_Y - ((row + 1) * CARD_HEIGHT)
    return x, y


def _draw_card(canvas: Canvas, card: PrintableCard, x: float, y: float, options: GenerationOptions) -> None:
    border_color = color_for_feature(card.feature_key)
    padding = CARD_PADDING

    canvas.saveState()
    if options.color_mode == ColorMode.COLOR:
        canvas.setStrokeColor(colors.HexColor(border_color))
        canvas.setLineWidth(CARD_BORDER_WIDTH)
        inset = CARD_BORDER_WIDTH / 2
        canvas.rect(
            x + inset,
            y + inset,
            CARD_WIDTH - CARD_BORDER_WIDTH,
            CARD_HEIGHT - CARD_BORDER_WIDTH,
            stroke=1,
            fill=0,
        )
        padding = CARD_PADDING_WITH_BORDER
    else:
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.5)
        canvas.rect(
            x,
            y,
            CARD_WIDTH,
            CARD_HEIGHT,
            stroke=1,
            fill=0,
        )

    content_x = x + padding
    content_y = y + CARD_HEIGHT - padding
    content_width = CARD_WIDTH - (2 * padding)

    _draw_header(canvas, card, content_x, content_y, content_width)
    _draw_title(canvas, card, content_x, content_y - 25, content_width)
    _draw_footer(canvas, card, content_x, y + padding, content_width)
    canvas.restoreState()


def _draw_header(canvas: Canvas, card: PrintableCard, x: float, y: float, width: float) -> None:
    label = "FEATURE" if card.kind == CardKind.FEATURE else "USER STORY"
    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_BOLD, 9)
    canvas.drawString(x, y, label)
    canvas.setFont(FONT_BOLD, 12)
    canvas.drawRightString(x + width, y, card.key)


def _draw_title(canvas: Canvas, card: PrintableCard, x: float, y: float, width: float) -> None:
    font_size = 15 if card.kind == CardKind.FEATURE else 13
    line_height = font_size + 3
    max_lines = 4

    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_BOLD, font_size)

    lines = _wrap_text(card.title, width, FONT_BOLD, font_size, max_lines)
    for line_index, line in enumerate(lines):
        canvas.drawString(x, y - (line_index * line_height), line)


def _draw_footer(canvas: Canvas, card: PrintableCard, x: float, y: float, width: float) -> None:
    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_REGULAR, 8)
    canvas.drawString(x, y, card.feature_key)

    if card.kind == CardKind.USER_STORY and card.story_points is not None:
        canvas.setFont(FONT_BOLD, 20)
        story_points = _format_story_points(card.story_points)
        canvas.drawRightString(x + width, y, story_points)


def _wrap_text(text: str, width: float, font_name: str, font_size: int, max_lines: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        if canvas_width(candidate, font_name, font_size) <= width:
            current_line = candidate
            continue

        if current_line:
            lines.append(current_line)
        current_line = word

        if len(lines) == max_lines:
            break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    if len(lines) == max_lines and words:
        last_line = lines[-1]
        while canvas_width(f"{last_line}...", font_name, font_size) > width and last_line:
            last_line = last_line[:-1].rstrip()
        lines[-1] = f"{last_line}..." if last_line else "..."

    return lines or [""]


def canvas_width(text: str, font_name: str, font_size: int) -> float:
    return pdfmetrics.stringWidth(text, font_name, font_size)


def _format_story_points(story_points: float) -> str:
    if story_points.is_integer():
        return str(int(story_points))
    return str(story_points).rstrip("0").rstrip(".")
