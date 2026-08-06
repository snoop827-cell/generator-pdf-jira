from __future__ import annotations

from pathlib import Path

from backend.core.models import GenerationOptions, GenerationSummary
from backend.layout.pagination import FeaturePrintJob
from backend.pdf.renderer import render_feature_pdf


def render_feature_pdfs(
    print_jobs: list[FeaturePrintJob],
    output_directory: str | Path,
    options: GenerationOptions | None = None,
) -> tuple[list[Path], GenerationSummary]:
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = [
        render_feature_pdf(print_job, output_dir / f"{_safe_filename(print_job.feature.key)}.pdf", options)
        for print_job in print_jobs
    ]

    summary = GenerationSummary(
        feature_count=len(print_jobs),
        user_story_count=sum(len(print_job.feature.stories) for print_job in print_jobs),
        card_count=sum(print_job.card_count for print_job in print_jobs),
        page_count=sum(print_job.page_count for print_job in print_jobs),
        pdf_count=len(pdf_paths),
    )
    return pdf_paths, summary


def _safe_filename(value: str) -> str:
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in value)

