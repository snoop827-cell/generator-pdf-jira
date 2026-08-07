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


def color_for_feature(feature_key: str) -> str:
    """Return a stable, deterministic color for a Jira Feature key."""
    normalized_key = feature_key.strip().upper()
    numeric_suffix = re.search(r"(\d+)$", normalized_key)
    if numeric_suffix:
        palette_index = (int(numeric_suffix.group(1)) - 1) % len(PALETTE)
        return PALETTE[palette_index]

    digest = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()
    palette_index = int(digest[:8], 16) % len(PALETTE)
    return PALETTE[palette_index]
