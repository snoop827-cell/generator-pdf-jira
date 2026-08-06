import pandas as pd
import pytest

from backend.core.exceptions import CsvValidationError
from backend.csv.reader import parse_jira_dataframe


def test_parse_jira_dataframe_cleans_and_maps_rows() -> None:
    dataframe = pd.DataFrame(
        [
            {
                " Type de ticket ": " Story ",
                "Clé de ticket": " PROJ-1 ",
                "Résumé": " My story ",
                "Champs personnalisés (Story Points)": " 5 ",
                "Clé parent": " FEAT-1 ",
                "Parent summary": " Feature summary ",
            },
            {
                " Type de ticket ": "",
                "Clé de ticket": "",
                "Résumé": "",
                "Champs personnalisés (Story Points)": "",
                "Clé parent": "",
                "Parent summary": "",
            },
        ]
    )

    stories, _ = parse_jira_dataframe(dataframe)

    assert len(stories) == 1
    assert stories[0].key == "PROJ-1"
    assert stories[0].summary == "My story"
    assert stories[0].story_points == 5
    assert stories[0].feature_key == "FEAT-1"


def test_parse_jira_dataframe_rejects_duplicate_ticket_keys() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "Type de ticket": "Story",
                "Clé de ticket": "PROJ-1",
                "Résumé": "First",
                "Champs personnalisés (Story Points)": "3",
                "Clé parent": "FEAT-1",
                "Parent summary": "Feature",
            },
            {
                "Type de ticket": "Story",
                "Clé de ticket": "PROJ-1",
                "Résumé": "Second",
                "Champs personnalisés (Story Points)": "5",
                "Clé parent": "FEAT-1",
                "Parent summary": "Feature",
            },
        ]
    )

    with pytest.raises(CsvValidationError):
        parse_jira_dataframe(dataframe)

