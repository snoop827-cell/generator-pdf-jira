from backend.colors.palette import color_for_feature


def test_feature_color_is_stable() -> None:
    assert color_for_feature("FEAT-123") == color_for_feature(" feat-123 ")


def test_different_features_can_receive_different_colors() -> None:
    assert color_for_feature("FEAT-123") != color_for_feature("FEAT-124")

