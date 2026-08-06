from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm


PAGE_WIDTH, PAGE_HEIGHT = A4

CARD_WIDTH = 9 * cm
CARD_HEIGHT = 6 * cm
CARD_BORDER_WIDTH = 3 * mm

PAGE_MARGIN_X = (PAGE_WIDTH - (2 * CARD_WIDTH)) / 2
PAGE_MARGIN_Y = (PAGE_HEIGHT - (4 * CARD_HEIGHT)) / 2

CARD_PADDING = 7 * mm
CARD_PADDING_WITH_BORDER = CARD_PADDING + CARD_BORDER_WIDTH
CROP_MARK_LENGTH = 5 * mm
CROP_MARK_OFFSET = 2 * mm
CROP_MARK_WIDTH = 0.5

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
