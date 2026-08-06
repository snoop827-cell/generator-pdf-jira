from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.exceptions import CsvValidationError
from backend.core.models import Feature, UserStory


CARDS_PER_A4_PAGE = 8
USER_STORIES_ON_FIRST_PAGE = 7


class CardKind(StrEnum):
    FEATURE = "feature"
    USER_STORY = "user_story"


class PrintableCard(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: CardKind
    key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    issue_type: str | None = None
    story_points: float | None = None
    feature_key: str = Field(min_length=1)


class PrintablePage(BaseModel):
    model_config = ConfigDict(frozen=True)

    number: int = Field(ge=1)
    cards: tuple[PrintableCard, ...]

    @property
    def card_count(self) -> int:
        return len(self.cards)


class FeaturePrintJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    feature: Feature
    pages: tuple[PrintablePage, ...]

    @property
    def card_count(self) -> int:
        return sum(page.card_count for page in self.pages)

    @property
    def page_count(self) -> int:
        return len(self.pages)


def paginate_feature(feature: Feature) -> FeaturePrintJob:
    """Create deterministic A4 pages for one Feature PDF."""
    if not feature.stories:
        raise CsvValidationError(f"Feature {feature.key} has no User Story.")

    first_page_cards = [_feature_card(feature)]
    remaining_stories = list(feature.stories)

    first_page_stories = remaining_stories[:USER_STORIES_ON_FIRST_PAGE]
    del remaining_stories[:USER_STORIES_ON_FIRST_PAGE]
    first_page_cards.extend(_story_card(story) for story in first_page_stories)

    pages: list[PrintablePage] = [
        PrintablePage(number=1, cards=tuple(first_page_cards)),
    ]

    while remaining_stories:
        page_stories = remaining_stories[:CARDS_PER_A4_PAGE]
        del remaining_stories[:CARDS_PER_A4_PAGE]
        pages.append(
            PrintablePage(
                number=len(pages) + 1,
                cards=tuple(_story_card(story) for story in page_stories),
            )
        )

    _validate_pages(feature, pages)
    return FeaturePrintJob(feature=feature, pages=tuple(pages))


def paginate_features(features: list[Feature]) -> list[FeaturePrintJob]:
    return [paginate_feature(feature) for feature in features]


def _feature_card(feature: Feature) -> PrintableCard:
    return PrintableCard(
        kind=CardKind.FEATURE,
        key=feature.key,
        title=feature.summary,
        feature_key=feature.key,
    )


def _story_card(story: UserStory) -> PrintableCard:
    return PrintableCard(
        kind=CardKind.USER_STORY,
        key=story.key,
        title=story.summary,
        issue_type=story.issue_type,
        story_points=story.story_points,
        feature_key=story.feature_key,
    )


def _validate_pages(feature: Feature, pages: list[PrintablePage]) -> None:
    story_keys = [story.key for story in feature.stories]
    paginated_story_keys = [
        card.key
        for page in pages
        for card in page.cards
        if card.kind == CardKind.USER_STORY
    ]

    if story_keys != paginated_story_keys:
        raise CsvValidationError(f"Pagination lost or reordered tickets for Feature {feature.key}.")

    for page in pages:
        if page.card_count > CARDS_PER_A4_PAGE:
            raise CsvValidationError(f"Page {page.number} contains more than 8 cards.")
        if not page.cards:
            raise CsvValidationError(f"Page {page.number} is empty.")
