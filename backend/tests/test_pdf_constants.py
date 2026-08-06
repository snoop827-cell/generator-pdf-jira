from backend.pdf.constants import CROP_MARK_LENGTH, CROP_MARK_OFFSET, CROP_MARK_WIDTH


def test_crop_mark_dimensions_are_defined() -> None:
    assert CROP_MARK_LENGTH > 0
    assert CROP_MARK_OFFSET > 0
    assert CROP_MARK_WIDTH == 0.5

