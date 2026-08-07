from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.core.exceptions import CsvValidationError
from backend.core.models import UserStory
from backend.csv.columns import JiraColumnMapping, detect_columns

UNKNOWN_FEATURE_KEY = "TSYCPROGRM-XXXX"
UNKNOWN_FEATURE_SUMMARY = "Feature inconnue"


def read_jira_csv(path: str | Path) -> tuple[list[UserStory], JiraColumnMapping]:
    dataframe = pd.read_csv(path, dtype=str, keep_default_na=False)
    return parse_jira_dataframe(dataframe)


def parse_jira_dataframe(dataframe: pd.DataFrame) -> tuple[list[UserStory], JiraColumnMapping]:
    cleaned = _clean_dataframe(dataframe)
    mapping = detect_columns(list(cleaned.columns))
    stories = _to_user_stories(cleaned, mapping)
    _validate_stories(stories)
    return stories, mapping


def _clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]
    cleaned = cleaned.map(lambda value: value.strip() if isinstance(value, str) else value)
    cleaned = cleaned.replace("", pd.NA)
    cleaned = cleaned.dropna(how="all")
    return cleaned.fillna("")


def _to_user_stories(dataframe: pd.DataFrame, mapping: JiraColumnMapping) -> list[UserStory]:
    stories: list[UserStory] = []
    for _, row in dataframe.iterrows():
        if not _has_required_ticket_fields(row, mapping):
            continue

        story_points = _parse_story_points(row[mapping.story_points])
        feature_key = str(row[mapping.parent_key]).strip() or UNKNOWN_FEATURE_KEY
        feature_summary = str(row[mapping.parent_summary]).strip() or UNKNOWN_FEATURE_SUMMARY
        stories.append(
            UserStory(
                issue_type=str(row[mapping.issue_type]).strip(),
                key=str(row[mapping.issue_key]).strip(),
                summary=str(row[mapping.summary]).strip(),
                story_points=story_points,
                feature_key=feature_key,
                feature_summary=feature_summary,
            )
        )
    return stories


def _has_required_ticket_fields(row: pd.Series, mapping: JiraColumnMapping) -> bool:
    return all(
        str(row[column]).strip()
        for column in (
            mapping.issue_key,
            mapping.summary,
        )
    )


def _parse_story_points(value: object) -> float | None:
    text_value = str(value).strip().replace(",", ".")
    if not text_value:
        return None
    return float(text_value)


def _validate_stories(stories: list[UserStory]) -> None:
    if not stories:
        raise CsvValidationError("The Jira CSV does not contain any usable ticket.")

    seen_keys: set[str] = set()
    duplicates: set[str] = set()
    for story in stories:
        if story.key in seen_keys:
            duplicates.add(story.key)
        seen_keys.add(story.key)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise CsvValidationError(f"Duplicate ticket keys found: {duplicate_list}")
