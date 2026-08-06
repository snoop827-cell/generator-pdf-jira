import pytest

from backend.core.exceptions import CsvValidationError
from backend.core.models import Feature, UserStory
from backend.layout.pagination import (
    CARDS_PER_A4_PAGE,
    CardKind,
    paginate_feature,
    paginate_features,
)


def make_story(index: int, feature_key: str = "FEAT-1") -> UserStory:
    return UserStory(
        issue_type="Story",
        key=f"PROJ-{index}",
        summary=f"Story {index}",
        story_points=index,
        feature_key=feature_key,
        feature_summary=f"Feature {feature_key}",
    )


def make_feature(story_count: int, feature_key: str = "FEAT-1") -> Feature:
    return Feature(
        key=feature_key,
        summary=f"Feature {feature_key}",
        stories=tuple(make_story(index, feature_key) for index in range(1, story_count + 1)),
    )


def test_paginate_feature_rejects_empty_feature() -> None:
    with pytest.raises(CsvValidationError):
        paginate_feature(make_feature(0))


def test_first_page_contains_feature_card_and_seven_user_stories() -> None:
    print_job = paginate_feature(make_feature(7))

    assert print_job.page_count == 1
    assert print_job.card_count == 8
    assert print_job.pages[0].cards[0].kind == CardKind.FEATURE
    assert [card.kind for card in print_job.pages[0].cards[1:]] == [CardKind.USER_STORY] * 7


def test_eighth_user_story_goes_to_second_page() -> None:
    print_job = paginate_feature(make_feature(8))

    assert print_job.page_count == 2
    assert [page.card_count for page in print_job.pages] == [8, 1]
    assert print_job.pages[1].cards[0].key == "PROJ-8"
    assert print_job.pages[1].cards[0].issue_type == "Story"


def test_following_pages_contain_eight_user_stories_maximum() -> None:
    print_job = paginate_feature(make_feature(15))

    assert print_job.page_count == 2
    assert [page.card_count for page in print_job.pages] == [8, 8]
    assert all(page.card_count <= CARDS_PER_A4_PAGE for page in print_job.pages)


def test_pagination_preserves_story_order_without_duplicates() -> None:
    print_job = paginate_feature(make_feature(20))
    paginated_story_keys = [
        card.key
        for page in print_job.pages
        for card in page.cards
        if card.kind == CardKind.USER_STORY
    ]

    assert paginated_story_keys == [f"PROJ-{index}" for index in range(1, 21)]
    assert len(paginated_story_keys) == len(set(paginated_story_keys))


def test_paginate_features_creates_one_print_job_per_feature() -> None:
    print_jobs = paginate_features([make_feature(1, "FEAT-1"), make_feature(2, "FEAT-2")])

    assert [print_job.feature.key for print_job in print_jobs] == ["FEAT-1", "FEAT-2"]
