from zipfile import ZipFile
from io import BytesIO

from fastapi.testclient import TestClient

from backend.api.main import app


client = TestClient(app)


CSV_CONTENT = """Type de ticket,Clé de ticket,Résumé,Champs personnalisés (Story Points),Clé parent,Parent summary
Story,PROJ-1,First story,3,FEAT-1,First feature
Story,PROJ-2,Second story,5,FEAT-1,First feature
Story,PROJ-3,Third story,8,FEAT-2,Second feature
"""


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_csv_returns_counts_and_detected_columns() -> None:
    response = client.post(
        "/api/csv/analyze",
        files={"file": ("jira.csv", CSV_CONTENT, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["ticket_count"] == 3
    assert response.json()["feature_count"] == 2
    assert response.json()["color_variant"] == 0
    assert response.json()["columns"]["parent_key"] == "Clé parent"
    assert response.json()["features"] == ["FEAT-1 - First feature", "FEAT-2 - Second feature"]
    assert response.json()["feature_details"] == [
        {
            "key": "FEAT-1",
            "summary": "First feature",
            "label": "FEAT-1 - First feature",
            "color": "#0072B2",
            "user_story_count": 2,
            "page_count": 1,
        },
        {
            "key": "FEAT-2",
            "summary": "Second feature",
            "label": "FEAT-2 - Second feature",
            "color": "#E69F00",
            "user_story_count": 1,
            "page_count": 1,
        },
    ]


def test_analyze_csv_accepts_semicolon_windows_export() -> None:
    csv_content = (
        "Type de ticket;Clé de ticket;Résumé;Champs personnalisés (Story Points);Clé parent;Parent summary\n"
        "Story;PROJ-1;Première story;3;FEAT-1;Première feature\n"
    ).encode("cp1252")

    response = client.post(
        "/api/csv/analyze",
        files={"file": ("jira.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["ticket_count"] == 1
    assert response.json()["columns"]["issue_key"] == "Clé de ticket"


def test_analyze_csv_accepts_color_variant() -> None:
    response = client.post(
        "/api/csv/analyze",
        files={"file": ("jira.csv", CSV_CONTENT, "text/csv")},
        data={"color_variant": "1"},
    )

    assert response.status_code == 200
    assert response.json()["color_variant"] == 1
    assert response.json()["feature_details"][0]["color"] == "#E69F00"


def test_analyze_csv_assigns_unique_colors_per_generation() -> None:
    response = client.post(
        "/api/csv/analyze",
        files={"file": ("jira.csv", CSV_CONTENT, "text/csv")},
    )

    colors = [feature["color"] for feature in response.json()["feature_details"]]

    assert response.status_code == 200
    assert len(colors) == len(set(colors))


def test_generate_summary_returns_generation_counts() -> None:
    response = client.post(
        "/api/generate/summary",
        files={"file": ("jira.csv", CSV_CONTENT, "text/csv")},
        data={"color_mode": "color"},
    )

    assert response.status_code == 200
    assert response.json()["color_mode"] == "color"
    assert response.json()["feature_count"] == 2
    assert response.json()["user_story_count"] == 3
    assert response.json()["card_count"] == 5
    assert response.json()["pdf_count"] == 2


def test_generate_returns_zip_with_one_pdf_per_feature() -> None:
    response = client.post(
        "/api/generate",
        files={"file": ("jira.csv", CSV_CONTENT, "text/csv")},
        data={"color_mode": "black_and_white"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["x-pdf-count"] == "2"

    with ZipFile(BytesIO(response.content)) as archive:
        assert archive.namelist() == ["FEAT-1.pdf", "FEAT-2.pdf"]


def test_analyze_csv_rejects_empty_file() -> None:
    response = client.post(
        "/api/csv/analyze",
        files={"file": ("jira.csv", "", "text/csv")},
    )

    assert response.status_code == 400
