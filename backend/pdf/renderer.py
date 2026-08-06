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
    CROP_MARK_LENGTH,
    CROP_MARK_OFFSET,
    CROP_MARK_WIDTH,
    FONT_BOLD,
    FONT_REGULAR,
    PAGE_HEIGHT,
    PAGE_MARGIN_X,
    PAGE_MARGIN_Y,
    PAGE_WIDTH,
    TEMPLATE_HEIGHT,
    TEMPLATE_WIDTH,
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
        _draw_crop_marks(canvas)
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


def _draw_crop_marks(canvas: Canvas) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(CROP_MARK_WIDTH)

    x_positions = [PAGE_MARGIN_X, PAGE_MARGIN_X + CARD_WIDTH, PAGE_MARGIN_X + (2 * CARD_WIDTH)]
    y_positions = [
        PAGE_MARGIN_Y,
        PAGE_MARGIN_Y + CARD_HEIGHT,
        PAGE_MARGIN_Y + (2 * CARD_HEIGHT),
        PAGE_MARGIN_Y + (3 * CARD_HEIGHT),
        PAGE_MARGIN_Y + (4 * CARD_HEIGHT),
    ]

    top = PAGE_MARGIN_Y + (4 * CARD_HEIGHT)
    bottom = PAGE_MARGIN_Y
    left = PAGE_MARGIN_X
    right = PAGE_MARGIN_X + (2 * CARD_WIDTH)

    for x in x_positions:
        _draw_vertical_crop_mark(canvas, x, bottom, -1)
        _draw_vertical_crop_mark(canvas, x, top, 1)

    for y in y_positions:
        _draw_horizontal_crop_mark(canvas, left, y, -1)
        _draw_horizontal_crop_mark(canvas, right, y, 1)

    canvas.restoreState()


def _draw_vertical_crop_mark(canvas: Canvas, x: float, grid_y: float, direction: int) -> None:
    start_y = grid_y + (direction * CROP_MARK_OFFSET)
    end_y = start_y + (direction * CROP_MARK_LENGTH)
    canvas.line(x, start_y, x, end_y)


def _draw_horizontal_crop_mark(canvas: Canvas, grid_x: float, y: float, direction: int) -> None:
    start_x = grid_x + (direction * CROP_MARK_OFFSET)
    end_x = start_x + (direction * CROP_MARK_LENGTH)
    canvas.line(start_x, y, end_x, y)


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

    if card.kind == CardKind.FEATURE:
        _draw_feature_template(canvas, card, x, y, padding)
    else:
        _draw_user_story_template(canvas, card, x, y, padding)
    canvas.restoreState()


def _draw_feature_template(canvas: Canvas, card: PrintableCard, x: float, y: float, padding: float) -> None:
    icon_x = x + _scale_x(13)
    header_y = y + CARD_HEIGHT - _scale_y(42)
    _draw_lightning_icon(canvas, icon_x, header_y - _scale_y(14), _scale_x(38), _scale_y(50))

    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_REGULAR, 26)
    canvas.drawString(x + _scale_x(58), header_y, "FEATURE")

    text_x = x + max(padding, _scale_x(15))
    text_width = CARD_WIDTH - (2 * max(padding, _scale_x(15)))
    key_y = y + CARD_HEIGHT - _scale_y(124)
    summary_y = y + CARD_HEIGHT - _scale_y(171)

    canvas.setFont(FONT_BOLD, 26)
    for line_index, line in enumerate(_wrap_text(card.key, text_width, FONT_BOLD, 26, 1)):
        canvas.drawString(text_x, key_y - (line_index * 30), line)
    for line_index, line in enumerate(_wrap_text(card.title, text_width, FONT_BOLD, 25, 3)):
        canvas.drawString(text_x, summary_y - (line_index * 29), line)


def _draw_user_story_template(canvas: Canvas, card: PrintableCard, x: float, y: float, padding: float) -> None:
    text_x = x + max(padding, _scale_x(13))
    text_width = CARD_WIDTH - (2 * max(padding, _scale_x(13)))
    header_y = y + CARD_HEIGHT - _scale_y(38)
    summary_y = y + CARD_HEIGHT - _scale_y(84)

    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_BOLD, 21)
    header = f"{card.issue_type or 'User Story'} {card.key}"
    for line_index, line in enumerate(_wrap_text(header, text_width, FONT_BOLD, 21, 1)):
        canvas.drawString(text_x, header_y - (line_index * 24), line)

    canvas.setFont(FONT_BOLD, 21)
    for line_index, line in enumerate(_wrap_text(card.title, text_width, FONT_BOLD, 21, 4)):
        canvas.drawString(text_x, summary_y - (line_index * 24), line)

    if card.story_points is not None:
        canvas.setFont(FONT_BOLD, 44)
        story_points = _format_story_points(card.story_points)
        canvas.drawRightString(x + CARD_WIDTH - max(padding, _scale_x(18)), y + _scale_y(98), story_points)

    footer_y = y + _scale_y(42)
    _draw_lightning_icon(canvas, x + _scale_x(17), footer_y - _scale_y(19), _scale_x(25), _scale_y(32))
    canvas.setFillColor(colors.black)
    canvas.setFont(FONT_REGULAR, 22)
    canvas.drawString(x + _scale_x(52), footer_y, f"FEATURE {card.feature_key}")


def _draw_lightning_icon(canvas: Canvas, x: float, y: float, width: float, height: float) -> None:
    points = [
        x + width * 0.62,
        y + height,
        x + width * 0.08,
        y + height * 0.43,
        x + width * 0.42,
        y + height * 0.43,
        x + width * 0.28,
        y,
        x + width * 0.92,
        y + height * 0.62,
        x + width * 0.55,
        y + height * 0.62,
    ]
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#B052F2"))
    canvas.setLineWidth(2.2)
    canvas.setFillColor(colors.white)
    path = canvas.beginPath()
    path.moveTo(points[0], points[1])
    for index in range(2, len(points), 2):
        path.lineTo(points[index], points[index + 1])
    path.close()
    canvas.drawPath(path, stroke=1, fill=0)
    canvas.restoreState()


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


def _scale_x(value: float) -> float:
    return (value / TEMPLATE_WIDTH) * CARD_WIDTH


def _scale_y(value: float) -> float:
    return (value / TEMPLATE_HEIGHT) * CARD_HEIGHT


def _format_story_points(story_points: float) -> str:
    if story_points.is_integer():
        return str(int(story_points))
    return str(story_points).rstrip("0").rstrip(".")
