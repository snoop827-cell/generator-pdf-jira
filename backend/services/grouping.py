from __future__ import annotations

from collections import defaultdict

from backend.core.exceptions import CsvValidationError
from backend.core.models import Feature, UserStory


def group_stories_by_feature(stories: list[UserStory]) -> list[Feature]:
    grouped: dict[str, list[UserStory]] = defaultdict(list)
    summaries_by_feature: dict[str, str] = {}

    for story in stories:
        if not story.feature_key:
            raise CsvValidationError(f"Ticket {story.key} has no parent Feature key.")
        if not story.feature_summary:
            raise CsvValidationError(f"Ticket {story.key} has no parent Feature summary.")

        existing_summary = summaries_by_feature.get(story.feature_key)
        if existing_summary is not None and existing_summary != story.feature_summary:
            raise CsvValidationError(
                f"Feature {story.feature_key} has inconsistent summaries: "
                f"{existing_summary!r} and {story.feature_summary!r}."
            )

        summaries_by_feature[story.feature_key] = story.feature_summary
        grouped[story.feature_key].append(story)

    return [
        Feature(
            key=feature_key,
            summary=summaries_by_feature[feature_key],
            stories=tuple(grouped[feature_key]),
        )
        for feature_key in sorted(grouped)
    ]

