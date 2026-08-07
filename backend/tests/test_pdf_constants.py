from backend.pdf.constants import (
    CROP_MARK_LENGTH,
    CROP_MARK_OFFSET,
    CROP_MARK_WIDTH,
    STORY_POINTS_CIRCLE_RADIUS,
    STORY_POINTS_CIRCLE_STROKE_WIDTH,
)


def test_crop_mark_dimensions_are_defined() -> None:
    assert CROP_MARK_LENGTH > 0
    assert CROP_MARK_OFFSET > 0
    assert CROP_MARK_WIDTH == 0.5


def test_story_points_circle_dimensions_are_defined() -> None:
    assert STORY_POINTS_CIRCLE_RADIUS > 0
    assert STORY_POINTS_CIRCLE_STROKE_WIDTH == 1
