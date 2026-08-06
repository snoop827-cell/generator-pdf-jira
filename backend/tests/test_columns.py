import pytest

from backend.core.exceptions import CsvMappingError
from backend.csv.columns import detect_columns, normalize_column_name


def test_normalize_column_name_is_tolerant() -> None:
    assert normalize_column_name("  Clé de ticket ") == "cle de ticket"
    assert normalize_column_name("Champs personnalisés (Story Points)") == "champs personnalises story points"


def test_detect_columns_with_jira_variants() -> None:
    mapping = detect_columns(
        [
            "Type de ticket",
            "Clé de ticket",
            "Résumé",
            "Champs personnalisés (Story Points)",
            "Clé parent",
            "Parent summary",
        ]
    )

    assert mapping.issue_type == "Type de ticket"
    assert mapping.issue_key == "Clé de ticket"
    assert mapping.summary == "Résumé"
    assert mapping.story_points == "Champs personnalisés (Story Points)"
    assert mapping.parent_key == "Clé parent"
    assert mapping.parent_summary == "Parent summary"


def test_detect_columns_uses_parent_key_not_generic_parent_column() -> None:
    mapping = detect_columns(
        [
            "Type de ticket",
            "Clé de ticket",
            "Résumé",
            "Champs personnalisés (Story Points)",
            "Parent",
            "Clé parent",
            "Parent summary",
        ]
    )

    assert mapping.parent_key == "Clé parent"


def test_detect_columns_reports_missing_columns() -> None:
    with pytest.raises(CsvMappingError):
        detect_columns(["Clé de ticket"])


def test_detect_columns_rejects_generic_parent_without_parent_key() -> None:
    with pytest.raises(CsvMappingError):
        detect_columns(
            [
                "Type de ticket",
                "Clé de ticket",
                "Résumé",
                "Champs personnalisés (Story Points)",
                "Parent",
                "Parent summary",
            ]
        )
