from backend.colors.palette import PALETTE, color_for_feature


def test_feature_color_is_stable() -> None:
    assert color_for_feature("FEAT-123") == color_for_feature(" feat-123 ")


def test_different_features_can_receive_different_colors() -> None:
    assert color_for_feature("FEAT-123") != color_for_feature("FEAT-124")


def test_numeric_feature_suffixes_walk_accessible_palette_order() -> None:
    assert color_for_feature("FEAT-1") == "#0072B2"
    assert color_for_feature("FEAT-2") == "#E69F00"
    assert color_for_feature("FEAT-3") == "#009E73"


def test_color_variant_rotates_palette() -> None:
    assert color_for_feature("FEAT-1", 1) == "#E69F00"
    assert color_for_feature("FEAT-1", 2) == "#009E73"


def test_palette_uses_colorblind_safe_colors() -> None:
    assert "#0072B2" in PALETTE
    assert "#E69F00" in PALETTE
    assert "#009E73" in PALETTE
    assert "#D32F2F" not in PALETTE
