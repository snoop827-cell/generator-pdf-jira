from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from backend.api.schemas import AnalyzeResponse
from backend.core.models import ColorMode, GenerationOptions, GenerationSummary
from backend.csv.reader import parse_jira_dataframe
from backend.layout.pagination import paginate_features
from backend.pdf.service import render_feature_pdfs
from backend.services.archive import create_zip_archive
from backend.services.grouping import group_stories_by_feature


def analyze_csv_bytes(content: bytes) -> AnalyzeResponse:
    dataframe = _read_dataframe(content)
    stories, mapping = parse_jira_dataframe(dataframe)
    features = group_stories_by_feature(stories)

    return AnalyzeResponse(
        ticket_count=len(stories),
        feature_count=len(features),
        columns={
            "issue_type": mapping.issue_type,
            "issue_key": mapping.issue_key,
            "summary": mapping.summary,
            "story_points": mapping.story_points,
            "parent_key": mapping.parent_key,
            "parent_summary": mapping.parent_summary,
        },
        features=[feature.label for feature in features],
    )


def generate_zip_from_csv_bytes(content: bytes, color_mode: ColorMode) -> tuple[bytes, GenerationSummary]:
    dataframe = _read_dataframe(content)
    stories, _ = parse_jira_dataframe(dataframe)
    features = group_stories_by_feature(stories)
    print_jobs = paginate_features(features)

    with TemporaryDirectory(prefix="jira-card-generator-") as temporary_directory:
        output_dir = Path(temporary_directory)
        pdf_paths, summary = render_feature_pdfs(
            print_jobs,
            output_dir / "pdf",
            GenerationOptions(color_mode=color_mode),
        )
        zip_path = create_zip_archive(pdf_paths, output_dir / "jira-cards.zip")
        return zip_path.read_bytes(), summary


def _read_dataframe(content: bytes) -> pd.DataFrame:
    return pd.read_csv(BytesIO(content), dtype=str, keep_default_na=False)

