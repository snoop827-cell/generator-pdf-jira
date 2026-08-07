from __future__ import annotations

import hashlib
import math
import re


MIN_OKLAB_DISTANCE = 0.13
MIN_TEXT_CONTRAST_RATIO = 4.5

PALETTE: tuple[str, ...] = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#D55E00",
    "#F0E442",
    "#4477AA",
    "#AA3377",
    "#228833",
    "#EE6677",
)


EXTENDED_PALETTE: tuple[str, ...] = (
    *PALETTE,
    "#332288",
    "#88CCEE",
    "#44AA99",
    "#117733",
    "#999933",
    "#DDCC77",
    "#CC6677",
    "#882255",
    "#AA4499",
    "#004488",
    "#DDAA33",
    "#BB5566",
    "#77AADD",
    "#EE8866",
    "#99DDFF",
)


def color_for_feature(feature_key: str, variant: int = 0) -> str:
    """Return a stable fallback color for a single Jira Feature key."""
    color_variant = max(0, variant)
    normalized_key = feature_key.strip().upper()
    numeric_suffix = re.search(r"(\d+)$", normalized_key)
    if numeric_suffix:
        palette_index = (int(numeric_suffix.group(1)) - 1 + color_variant) % len(PALETTE)
        return PALETTE[palette_index]

    digest = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()
    palette_index = (int(digest[:8], 16) + color_variant) % len(PALETTE)
    return PALETTE[palette_index]


def colors_for_features(feature_keys: list[str], variant: int = 0) -> dict[str, str]:
    """Return visually distinct, colorblind-friendly colors for one generation."""
    unique_keys = list(dict.fromkeys(feature_keys))
    if not unique_keys:
        return {}

    candidates = _readable_candidates()
    if len(unique_keys) > len(candidates):
        raise ValueError(
            f"Cannot assign unique accessible colors to {len(unique_keys)} Features. "
            f"The current palette supports {len(candidates)} unique colors."
        )

    color_variant = max(0, variant)
    ordered_candidates = _rotate(candidates, color_variant % len(candidates))
    selected_colors = _select_distinct_colors(ordered_candidates, len(unique_keys))

    return dict(zip(unique_keys, selected_colors, strict=True))


def readable_text_color(background_hex: str) -> str:
    """Return black or white text, whichever is more readable on the background."""
    black_contrast = contrast_ratio(background_hex, "#000000")
    white_contrast = contrast_ratio(background_hex, "#FFFFFF")
    return "#000000" if black_contrast >= white_contrast else "#FFFFFF"


def oklab_distance(first_hex: str, second_hex: str) -> float:
    first = _hex_to_oklab(first_hex)
    second = _hex_to_oklab(second_hex)
    return math.sqrt(sum((first[index] - second[index]) ** 2 for index in range(3)))


def contrast_ratio(first_hex: str, second_hex: str) -> float:
    first_luminance = _relative_luminance(_hex_to_rgb(first_hex))
    second_luminance = _relative_luminance(_hex_to_rgb(second_hex))
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _readable_candidates() -> list[str]:
    return [
        color
        for color in EXTENDED_PALETTE
        if max(contrast_ratio(color, "#000000"), contrast_ratio(color, "#FFFFFF")) >= MIN_TEXT_CONTRAST_RATIO
    ]


def _select_distinct_colors(candidates: list[str], count: int) -> list[str]:
    selected = [candidates[0]]
    remaining = candidates[1:]

    while len(selected) < count:
        best_color = max(
            remaining,
            key=lambda color: (
                min(oklab_distance(color, selected_color) for selected_color in selected),
                _lightness_spread_score(color, selected),
            ),
        )
        best_distance = min(oklab_distance(best_color, selected_color) for selected_color in selected)
        if best_distance < MIN_OKLAB_DISTANCE:
            raise ValueError(
                "Cannot generate a palette with sufficiently distinct colors for this number of Features."
            )
        selected.append(best_color)
        remaining.remove(best_color)

    return selected


def _lightness_spread_score(color: str, selected: list[str]) -> float:
    color_lightness = _hex_to_oklab(color)[0]
    return min(abs(color_lightness - _hex_to_oklab(selected_color)[0]) for selected_color in selected)


def _rotate(values: list[str], offset: int) -> list[str]:
    return values[offset:] + values[:offset]


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    normalized = value.strip().lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"Invalid hex color: {value}")
    return tuple(int(normalized[index : index + 2], 16) / 255 for index in (0, 2, 4))


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    linear = tuple(_srgb_to_linear(channel) for channel in rgb)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _hex_to_oklab(value: str) -> tuple[float, float, float]:
    red, green, blue = (_srgb_to_linear(channel) for channel in _hex_to_rgb(value))

    long = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    medium = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    short = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue

    long_root = math.copysign(abs(long) ** (1 / 3), long)
    medium_root = math.copysign(abs(medium) ** (1 / 3), medium)
    short_root = math.copysign(abs(short) ** (1 / 3), short)

    return (
        0.2104542553 * long_root + 0.7936177850 * medium_root - 0.0040720468 * short_root,
        1.9779984951 * long_root - 2.4285922050 * medium_root + 0.4505937099 * short_root,
        0.0259040371 * long_root + 0.7827717662 * medium_root - 0.8086757660 * short_root,
    )


def _srgb_to_linear(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4
