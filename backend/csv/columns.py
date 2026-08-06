from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from backend.core.exceptions import CsvMappingError


@dataclass(frozen=True)
class JiraColumnMapping:
    issue_type: str
    issue_key: str
    summary: str
    story_points: str
    parent_key: str
    parent_summary: str


REQUIRED_FIELDS: tuple[str, ...] = (
    "issue_type",
    "issue_key",
    "summary",
    "story_points",
    "parent_key",
    "parent_summary",
)


ALIASES: dict[str, tuple[str, ...]] = {
    "issue_type": (
        "type",
        "type de ticket",
        "issue type",
        "issuetype",
        "ticket type",
    ),
    "issue_key": (
        "cle",
        "cle de ticket",
        "key",
        "issue key",
        "ticket key",
    ),
    "summary": (
        "resume",
        "summary",
        "titre",
        "title",
    ),
    "story_points": (
        "story points",
        "story point",
        "champs personnalises story points",
        "custom field story points",
        "customfield story points",
        "storypoints",
    ),
    "parent_key": (
        "cle parent",
        "parent key",
        "parent issue key",
    ),
    "parent_summary": (
        "parent summary",
        "resume parent",
        "parent resume",
        "parent title",
    ),
}


def normalize_column_name(value: str) -> str:
    without_accents = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    lowered = without_accents.casefold()
    without_brackets = re.sub(r"[\[\]\(\)]", " ", lowered)
    compacted = re.sub(r"[^a-z0-9]+", " ", without_brackets)
    return re.sub(r"\s+", " ", compacted).strip()


def detect_columns(columns: list[str]) -> JiraColumnMapping:
    normalized_by_original = {column: normalize_column_name(column) for column in columns}
    matches: dict[str, str] = {}

    for field_name, aliases in ALIASES.items():
        normalized_aliases = {normalize_column_name(alias) for alias in aliases}
        for original_column, normalized_column in normalized_by_original.items():
            if normalized_column in normalized_aliases:
                matches[field_name] = original_column
                break

    missing_fields = [field for field in REQUIRED_FIELDS if field not in matches]
    if missing_fields:
        missing_labels = ", ".join(missing_fields)
        raise CsvMappingError(f"Missing required Jira CSV columns: {missing_labels}")

    return JiraColumnMapping(**matches)
