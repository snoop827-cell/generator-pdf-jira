from __future__ import annotations

from pydantic import BaseModel, Field

from backend.core.models import ColorMode


class AnalyzeResponse(BaseModel):
    ticket_count: int = Field(ge=0)
    feature_count: int = Field(ge=0)
    columns: dict[str, str]
    features: list[str]


class GenerateResponse(BaseModel):
    color_mode: ColorMode
    feature_count: int = Field(ge=0)
    user_story_count: int = Field(ge=0)
    card_count: int = Field(ge=0)
    page_count: int = Field(ge=0)
    pdf_count: int = Field(ge=0)

