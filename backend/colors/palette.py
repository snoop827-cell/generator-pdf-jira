from __future__ import annotations

import hashlib


PALETTE: tuple[str, ...] = (
    "#D32F2F",
    "#C2185B",
    "#7B1FA2",
    "#512DA8",
    "#303F9F",
    "#1976D2",
    "#00796B",
    "#388E3C",
    "#689F38",
    "#FBC02D",
    "#F57C00",
    "#E64A19",
)


def color_for_feature(feature_key: str) -> str:
    """Return a stable, deterministic color for a Jira Feature key."""
    normalized_key = feature_key.strip().upper()
    digest = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()
    palette_index = int(digest[:8], 16) % len(PALETTE)
    return PALETTE[palette_index]

