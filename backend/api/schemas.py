from __future__ import annotations

from pydantic import BaseModel, Field

from backend.core.models import ColorMode


class FeatureAnalysis(BaseModel):
    key: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    label: str = Field(min_length=1)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    user_story_count: int = Field(ge=0)
    page_count: int = Field(ge=0)


class AnalyzeResponse(BaseModel):
    ticket_count: int = Field(ge=0)
    feature_count: int = Field(ge=0)
    columns: dict[str, str]
    features: list[str]
    feature_details: list[FeatureAnalysis]


class GenerateResponse(BaseModel):
    color_mode: ColorMode
    feature_count: int = Field(ge=0)
    user_story_count: int = Field(ge=0)
    card_count: int = Field(ge=0)
    page_count: int = Field(ge=0)
    pdf_count: int = Field(ge=0)
