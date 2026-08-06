import pytest

from backend.core.exceptions import CsvValidationError
from backend.core.models import UserStory
from backend.services.grouping import group_stories_by_feature


def make_story(key: str, feature_key: str = "FEAT-1", feature_summary: str = "Feature one") -> UserStory:
    return UserStory(
        issue_type="Story",
        key=key,
        summary=f"Summary {key}",
        story_points=3,
        feature_key=feature_key,
        feature_summary=feature_summary,
    )


def test_group_stories_by_feature_key() -> None:
    features = group_stories_by_feature(
        [
            make_story("PROJ-1", "FEAT-2", "Feature two"),
            make_story("PROJ-2", "FEAT-1", "Feature one"),
            make_story("PROJ-3", "FEAT-2", "Feature two"),
        ]
    )

    assert [feature.key for feature in features] == ["FEAT-1", "FEAT-2"]
    assert [story.key for story in features[1].stories] == ["PROJ-1", "PROJ-3"]


def test_grouping_rejects_inconsistent_feature_summaries() -> None:
    with pytest.raises(CsvValidationError):
        group_stories_by_feature(
            [
                make_story("PROJ-1", "FEAT-1", "First name"),
                make_story("PROJ-2", "FEAT-1", "Second name"),
            ]
        )

