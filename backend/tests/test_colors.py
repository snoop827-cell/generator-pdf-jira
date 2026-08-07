from backend.colors.palette import EXTENDED_PALETTE, PALETTE, color_for_feature, colors_for_features


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


def test_colors_for_features_assigns_unique_colors() -> None:
    feature_colors = colors_for_features([f"FEAT-{index}" for index in range(1, 8)])

    assert len(feature_colors) == 7
    assert len(set(feature_colors.values())) == 7


def test_colors_for_features_rotates_generation_variant() -> None:
    base_colors = colors_for_features(["FEAT-1", "FEAT-2"], 0)
    alternate_colors = colors_for_features(["FEAT-1", "FEAT-2"], 1)

    assert base_colors["FEAT-1"] != alternate_colors["FEAT-1"]
    assert len(set(alternate_colors.values())) == 2


def test_palette_uses_colorblind_safe_colors() -> None:
    assert "#0072B2" in PALETTE
    assert "#E69F00" in PALETTE
    assert "#009E73" in PALETTE
    assert "#D32F2F" not in PALETTE
    assert len(EXTENDED_PALETTE) == len(set(EXTENDED_PALETTE))
