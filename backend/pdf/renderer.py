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
    CROP_MARK_WIDTH,
    FEATURE_CARD_HEIGHT,
    FEATURE_CARD_WIDTH,
    FIRST_PAGE_MARGIN_Y,
    FONT_BOLD,
    FONT_REGULAR,
    PAGE_HEIGHT,
    PAGE_MARGIN_X,
    PAGE_MARGIN_Y,
    PAGE_WIDTH,
    STORY_POINTS_CIRCLE_RADIUS,
    STORY_POINTS_CIRCLE_STROKE_WIDTH,
    TEMPLATE_HEIGHT,
    TEMPLATE_WIDTH,
    USER_STORY_INNER_MARGIN,
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
            x, y = _card_position(page.number, index)
            width, height = _card_dimensions(card)
            _draw_card(canvas, card, x, y, width, height, generation_options)
        _draw_crop_marks(canvas, page.number)
        canvas.showPage()

    canvas.save()
    return output


def _card_position(page_number: int, index: int) -> tuple[float, float]:
    if page_number == 1 and index == 0:
        return (
            (PAGE_WIDTH - FEATURE_CARD_WIDTH) / 2,
            PAGE_HEIGHT - FIRST_PAGE_MARGIN_Y - FEATURE_CARD_HEIGHT,
        )

    if page_number == 1:
        story_index = index - 1
        column = story_index % 2
        row = story_index // 2
        x = PAGE_MARGIN_X + (column * CARD_WIDTH)
        feature_y = PAGE_HEIGHT - FIRST_PAGE_MARGIN_Y - FEATURE_CARD_HEIGHT
        y = feature_y - ((row + 1) * CARD_HEIGHT)
        return x, y

    column = index % 2
    row = index // 2
    x = PAGE_MARGIN_X + (column * CARD_WIDTH)
    y = PAGE_HEIGHT - PAGE_MARGIN_Y - ((row + 1) * CARD_HEIGHT)
    return x, y


def _card_dimensions(card: PrintableCard) -> tuple[float, float]:
    if card.kind == CardKind.FEATURE:
        return FEATURE_CARD_WIDTH, FEATURE_CARD_HEIGHT
    return CARD_WIDTH, CARD_HEIGHT


def _draw_crop_marks(canvas: Canvas, page_number: int) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(CROP_MARK_WIDTH)

    if page_number == 1:
        _draw_first_page_cut_lines(canvas)
    else:
        _draw_regular_page_cut_lines(canvas)

    canvas.restoreState()


def _draw_regular_page_cut_lines(canvas: Canvas) -> None:
    left = PAGE_MARGIN_X
    right = PAGE_MARGIN_X + (2 * CARD_WIDTH)
    bottom = PAGE_MARGIN_Y
    top = PAGE_MARGIN_Y + (4 * CARD_HEIGHT)
    x_positions = [PAGE_MARGIN_X, PAGE_MARGIN_X + CARD_WIDTH, PAGE_MARGIN_X + (2 * CARD_WIDTH)]
    y_positions = [
        PAGE_MARGIN_Y,
        PAGE_MARGIN_Y + CARD_HEIGHT,
        PAGE_MARGIN_Y + (2 * CARD_HEIGHT),
        PAGE_MARGIN_Y + (3 * CARD_HEIGHT),
        PAGE_MARGIN_Y + (4 * CARD_HEIGHT),
    ]

    for x in x_positions:
        canvas.line(x, bottom, x, top)
        canvas.line(x, 0, x, bottom)
        canvas.line(x, top, x, PAGE_HEIGHT)

    for y in y_positions:
        canvas.line(left, y, right, y)
        canvas.line(0, y, left, y)
        canvas.line(right, y, PAGE_WIDTH, y)


def _draw_first_page_cut_lines(canvas: Canvas) -> None:
    feature_left = (PAGE_WIDTH - FEATURE_CARD_WIDTH) / 2
    feature_right = feature_left + FEATURE_CARD_WIDTH
    feature_top = PAGE_HEIGHT - FIRST_PAGE_MARGIN_Y
    feature_bottom = feature_top - FEATURE_CARD_HEIGHT

    story_left = PAGE_MARGIN_X
    story_middle = PAGE_MARGIN_X + CARD_WIDTH
    story_right = PAGE_MARGIN_X + (2 * CARD_WIDTH)
    story_bottom = feature_bottom - (3 * CARD_HEIGHT)

    for x in (feature_left, feature_right):
        canvas.line(x, feature_bottom, x, feature_top)
        canvas.line(x, feature_top, x, PAGE_HEIGHT)

    for x in (story_left, story_middle, story_right):
        canvas.line(x, story_bottom, x, feature_bottom)
        canvas.line(x, 0, x, story_bottom)

    canvas.line(0, feature_top, feature_left, feature_top)
    canvas.line(feature_left, feature_top, feature_right, feature_top)
    canvas.line(feature_right, feature_top, PAGE_WIDTH, feature_top)

    canvas.line(0, feature_bottom, story_left, feature_bottom)
    canvas.line(story_left, feature_bottom, story_right, feature_bottom)
    canvas.line(story_right, feature_bottom, PAGE_WIDTH, feature_bottom)

    for row_index in range(1, 4):
        y = feature_bottom - (row_index * CARD_HEIGHT)
        canvas.line(0, y, story_left, y)
        canvas.line(story_left, y, story_right, y)
        canvas.line(story_right, y, PAGE_WIDTH, y)


def _draw_card(
    canvas: Canvas,
    card: PrintableCard,
    x: float,
    y: float,
    width: float,
    height: float,
    options: GenerationOptions,
) -> None:
    border_color = options.feature_colors.get(card.feature_key) or color_for_feature(
        card.feature_key,
        options.color_variant,
    )
    padding = CARD_PADDING

    canvas.saveState()
    if card.kind == CardKind.FEATURE and options.color_mode == ColorMode.COLOR:
        canvas.setFillColor(colors.HexColor(border_color))
        canvas.setFillAlpha(0.16)
        canvas.rect(x, y, width, height, stroke=0, fill=1)
        canvas.setFillAlpha(1)

    if options.color_mode == ColorMode.COLOR:
        canvas.setStrokeColor(colors.HexColor(border_color))
        canvas.setLineWidth(CARD_BORDER_WIDTH)
        inset = CARD_BORDER_WIDTH / 2
        canvas.rect(
            x + inset,
            y + inset,
            width - CARD_BORDER_WIDTH,
            height - CARD_BORDER_WIDTH,
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
            width,
            height,
            stroke=1,
            fill=0,
        )

    if card.kind == CardKind.FEATURE:
        _draw_feature_template(canvas, card, x, y, width, height, padding)
    else:
        _draw_user_story_template(canvas, card, x, y, padding)
    canvas.restoreState()


def _draw_feature_template(
    canvas: Canvas,
    card: PrintableCard,
    x: float,
    y: float,
    width: float,
    height: float,
    padding: float,
) -> None:
    inner_margin = max(padding, USER_STORY_INNER_MARGIN)
    content_left = x + inner_margin
    content_right = x + width - inner_margin
    content_top = y + height - inner_margin
    content_bottom = y + inner_margin
    content_width = content_right - content_left

    title_font_size = 15
    summary_font_size = 12
    title_summary_gap = (5 * 2.8346456693) * (2 / 3)
    key_top = content_top - _scale_y(3)
    summary_top = key_top - title_font_size - title_summary_gap

    canvas.setFillColor(colors.black)
    _draw_fitted_text(canvas, card.key, content_left, key_top, content_width, title_font_size + 2, FONT_BOLD, 15, 9, 1)
    _draw_fitted_text(
        canvas,
        card.title,
        content_left,
        summary_top,
        content_width,
        summary_top - content_bottom,
        FONT_BOLD,
        summary_font_size,
        8,
        5,
    )


def _draw_user_story_template(canvas: Canvas, card: PrintableCard, x: float, y: float, padding: float) -> None:
    inner_margin = max(padding, USER_STORY_INNER_MARGIN)
    content_left = x + inner_margin
    content_right = x + CARD_WIDTH - inner_margin
    content_top = y + CARD_HEIGHT - inner_margin
    content_bottom = y + inner_margin
    content_width = content_right - content_left

    title_font_size = 15
    summary_font_size = 12
    feature_font_size = 12
    story_points_font_size = 28
    story_points_circle_radius = STORY_POINTS_CIRCLE_RADIUS

    header_top = content_top - _scale_y(3)
    title_summary_gap = (5 * 2.8346456693) * (2 / 3)
    summary_top = header_top - title_font_size - title_summary_gap
    summary_line_height = summary_font_size * 1.12
    feature_baseline = content_bottom + feature_font_size * 0.15
    points_center_x = content_right - story_points_circle_radius
    points_center_y = content_bottom + story_points_circle_radius
    points_baseline = points_center_y - (story_points_font_size * 0.35)
    feature_text_x = content_left
    feature_text_width = max(1, points_center_x - story_points_circle_radius - _scale_x(12) - feature_text_x)

    canvas.setFillColor(colors.black)
    header = card.key
    _draw_fitted_text(canvas, header, content_left, header_top, content_width, title_font_size + 2, FONT_BOLD, 20, 9, 1)

    _draw_fitted_text(
        canvas,
        card.title,
        content_left,
        summary_top,
        content_width,
        summary_line_height * 4,
        FONT_BOLD,
        summary_font_size,
        8,
        4,
    )

    if card.story_points is not None:
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(STORY_POINTS_CIRCLE_STROKE_WIDTH)
        canvas.circle(points_center_x, points_center_y, story_points_circle_radius, stroke=1, fill=0)
        canvas.setFillColor(colors.black)
        canvas.setFont(FONT_BOLD, story_points_font_size)
        story_points = _format_story_points(card.story_points)
        canvas.drawCentredString(points_center_x, points_baseline, story_points)

    canvas.setFillColor(colors.black)
    _draw_fitted_text(
        canvas,
        card.feature_key,
        feature_text_x,
        feature_baseline,
        feature_text_width,
        feature_font_size + 2,
        FONT_BOLD,
        feature_font_size,
        7,
        1,
    )


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
    was_truncated = False

    for word_index, word in enumerate(words):
        candidate = f"{current_line} {word}".strip()
        if canvas_width(candidate, font_name, font_size) <= width:
            current_line = candidate
            continue

        if current_line:
            lines.append(current_line)
        current_line = word

        if len(lines) == max_lines:
            was_truncated = word_index < len(words)
            break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    if was_truncated and len(lines) == max_lines and words:
        last_line = lines[-1]
        while canvas_width(f"{last_line}...", font_name, font_size) > width and last_line:
            last_line = last_line[:-1].rstrip()
        lines[-1] = f"{last_line}..." if last_line else "..."

    return lines or [""]


def _draw_fitted_text(
    canvas: Canvas,
    text: str,
    x: float,
    top_y: float,
    width: float,
    height: float,
    font_name: str,
    max_font_size: int,
    min_font_size: int,
    max_lines: int,
) -> None:
    for font_size in range(max_font_size, min_font_size - 1, -1):
        line_height = font_size * 1.12
        allowed_lines = min(max_lines, max(1, int(height // line_height)))
        lines = _wrap_text(text, width, font_name, font_size, allowed_lines)
        if len(lines) * line_height <= height:
            canvas.setFont(font_name, font_size)
            for line_index, line in enumerate(lines):
                canvas.drawString(x, top_y - (line_index * line_height), line)
            return

    canvas.setFont(font_name, min_font_size)
    canvas.drawString(x, top_y, _ellipsize(text, width, font_name, min_font_size))


def _ellipsize(text: str, width: float, font_name: str, font_size: int) -> str:
    if canvas_width(text, font_name, font_size) <= width:
        return text
    shortened = text
    while shortened and canvas_width(f"{shortened}...", font_name, font_size) > width:
        shortened = shortened[:-1].rstrip()
    return f"{shortened}..." if shortened else "..."


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
