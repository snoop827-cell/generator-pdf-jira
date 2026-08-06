from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ColorMode(StrEnum):
    BLACK_AND_WHITE = "black_and_white"
    COLOR = "color"


class GenerationOptions(BaseModel):
    color_mode: ColorMode = ColorMode.BLACK_AND_WHITE


class GenerationSummary(BaseModel):
    feature_count: int = Field(ge=0)
    user_story_count: int = Field(ge=0)
    card_count: int = Field(ge=0)
    page_count: int = Field(ge=0)
    pdf_count: int = Field(ge=0)


class UserStory(BaseModel):
    model_config = ConfigDict(frozen=True)

    issue_type: str = Field(min_length=1)
    key: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    story_points: float | None = None
    feature_key: str = Field(min_length=1)
    feature_summary: str = Field(min_length=1)


class Feature(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    stories: tuple[UserStory, ...] = Field(default_factory=tuple)

    @property
    def label(self) -> str:
        return f"{self.key} - {self.summary}"
