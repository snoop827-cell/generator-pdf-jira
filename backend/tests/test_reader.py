import pandas as pd
import pytest

from backend.core.exceptions import CsvValidationError
from backend.csv.reader import parse_jira_dataframe


def test_parse_jira_dataframe_cleans_and_maps_rows() -> None:
    dataframe = pd.DataFrame(
        [
            {
                " Issue Type ": " Story ",
                "Issue Key": " PROJ-1 ",
                "Summary": " My story ",
                "Story Points": " 5 ",
                "Parent Key": " FEAT-1 ",
                "Parent summary": " Feature summary ",
            },
            {
                " Issue Type ": "",
                "Issue Key": "",
                "Summary": "",
                "Story Points": "",
                "Parent Key": "",
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
                "Issue Type": "Story",
                "Issue Key": "PROJ-1",
                "Summary": "First",
                "Story Points": "3",
                "Parent Key": "FEAT-1",
                "Parent summary": "Feature",
            },
            {
                "Issue Type": "Story",
                "Issue Key": "PROJ-1",
                "Summary": "Second",
                "Story Points": "5",
                "Parent Key": "FEAT-1",
                "Parent summary": "Feature",
            },
        ]
    )

    with pytest.raises(CsvValidationError):
        parse_jira_dataframe(dataframe)


def test_parse_jira_dataframe_uses_unknown_feature_when_parent_is_missing() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "Issue Type": "Feature",
                "Issue Key": "FEAT-1",
                "Summary": "Feature row",
                "Story Points": "",
                "Parent Key": "",
                "Parent summary": "",
            },
            {
                "Issue Type": "Story",
                "Issue Key": "PROJ-1",
                "Summary": "Story row",
                "Story Points": "3",
                "Parent Key": "FEAT-1",
                "Parent summary": "Feature row",
            },
        ]
    )

    stories, _ = parse_jira_dataframe(dataframe)

    assert len(stories) == 2
    assert stories[0].key == "FEAT-1"
    assert stories[0].feature_key == "TSYCPROGRM-XXXX"
    assert stories[0].feature_summary == "Feature inconnue"
    assert stories[1].key == "PROJ-1"
