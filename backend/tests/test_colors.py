from backend.colors.palette import (
    EXTENDED_PALETTE,
    MIN_OKLAB_DISTANCE,
    MIN_TEXT_CONTRAST_RATIO,
    PALETTE,
    color_for_feature,
    colors_for_features,
    contrast_ratio,
    oklab_distance,
    readable_text_color,
)


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
    feature_colors = colors_for_features([f"FEAT-{index}" for index in range(1, 10)])

    assert len(feature_colors) == 9
    assert len(set(feature_colors.values())) == 9


def test_colors_for_features_rotates_generation_variant() -> None:
    base_colors = colors_for_features(["FEAT-1", "FEAT-2"], 0)
    alternate_colors = colors_for_features(["FEAT-1", "FEAT-2"], 1)

    assert base_colors["FEAT-1"] != alternate_colors["FEAT-1"]
    assert len(set(alternate_colors.values())) == 2


def test_colors_for_features_respects_oklab_distance_threshold() -> None:
    feature_colors = list(colors_for_features([f"FEAT-{index}" for index in range(1, 8)]).values())

    distances = [
        oklab_distance(first_color, second_color)
        for first_index, first_color in enumerate(feature_colors)
        for second_color in feature_colors[first_index + 1 :]
    ]

    assert min(distances) >= MIN_OKLAB_DISTANCE


def test_palette_keeps_readable_text_on_each_color() -> None:
    for color in EXTENDED_PALETTE:
        text_color = readable_text_color(color)
        assert text_color in ("#000000", "#FFFFFF")
        assert contrast_ratio(color, text_color) >= MIN_TEXT_CONTRAST_RATIO


def test_palette_uses_colorblind_safe_colors() -> None:
    assert "#0072B2" in PALETTE
    assert "#E69F00" in PALETTE
    assert "#009E73" in PALETTE
    assert "#D32F2F" not in PALETTE
    assert len(EXTENDED_PALETTE) == len(set(EXTENDED_PALETTE))
