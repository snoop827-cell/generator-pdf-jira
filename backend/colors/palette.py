from __future__ import annotations

import hashlib
import re


PALETTE: tuple[str, ...] = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#D55E00",
    "#F0E442",
    "#000000",
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
    "#DDDDDD",
)


def color_for_feature(feature_key: str, variant: int = 0) -> str:
    """Return a stable, deterministic color for a Jira Feature key."""
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
    """Return one unique color per Feature key for a single generation."""
    unique_keys = list(dict.fromkeys(feature_keys))
    color_variant = max(0, variant)
    if len(unique_keys) > len(EXTENDED_PALETTE):
        raise ValueError(
            f"Cannot assign unique accessible colors to {len(unique_keys)} Features. "
            f"The current palette supports {len(EXTENDED_PALETTE)} unique colors."
        )

    return {
        feature_key: EXTENDED_PALETTE[(index + color_variant) % len(EXTENDED_PALETTE)]
        for index, feature_key in enumerate(unique_keys)
    }
