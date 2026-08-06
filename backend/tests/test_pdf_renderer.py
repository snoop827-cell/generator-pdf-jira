from pathlib import Path

from pypdf import PdfReader

from backend.core.models import ColorMode, Feature, GenerationOptions, UserStory
from backend.layout.pagination import paginate_feature, paginate_features
from backend.pdf.constants import CARD_HEIGHT, CARD_WIDTH
from backend.pdf.renderer import render_feature_pdf, _wrap_text
from backend.pdf.service import render_feature_pdfs


def make_story(index: int, feature_key: str = "FEAT-1") -> UserStory:
    return UserStory(
        issue_type="Story",
        key=f"PROJ-{index}",
        summary=f"Story {index}",
        story_points=index,
        feature_key=feature_key,
        feature_summary=f"Feature {feature_key}",
    )


def make_feature(story_count: int, feature_key: str = "FEAT-1") -> Feature:
    return Feature(
        key=feature_key,
        summary=f"Feature {feature_key}",
        stories=tuple(make_story(index, feature_key) for index in range(1, story_count + 1)),
    )


def test_render_feature_pdf_creates_one_page_per_print_page(tmp_path: Path) -> None:
    print_job = paginate_feature(make_feature(8))
    output_path = render_feature_pdf(print_job, tmp_path / "feature.pdf")

    reader = PdfReader(output_path)

    assert output_path.exists()
    assert len(reader.pages) == 2


def test_render_feature_pdf_contains_expected_text(tmp_path: Path) -> None:
    print_job = paginate_feature(make_feature(1))
    output_path = render_feature_pdf(
        print_job,
        tmp_path / "feature-color.pdf",
        GenerationOptions(color_mode=ColorMode.COLOR),
    )

    text = "\n".join(page.extract_text() or "" for page in PdfReader(output_path).pages)

    assert "FEATURE" in text
    assert "Story PROJ-1" in text
    assert "FEAT-1" in text
    assert "PROJ-1" in text


def test_render_feature_pdf_accepts_long_realistic_text(tmp_path: Path) -> None:
    feature = Feature(
        key="TSYCPROGRM-233",
        summary="Portail YC - Comment fournir une vue synthétique des filtres",
        stories=(
            UserStory(
                issue_type="Story",
                key="YFPYC-419",
                summary="Déplacer les filtres dans une sidebar",
                story_points=3,
                feature_key="TSYCPROGRM-233",
                feature_summary="Portail YC - Comment fournir une vue synthétique des filtres",
            ),
            UserStory(
                issue_type="Story",
                key="YFPYC-400",
                summary="Ecran Activités - Afficher les activités Azure",
                story_points=5,
                feature_key="TSYCPROGRM-233",
                feature_summary="Portail YC - Comment fournir une vue synthétique des filtres",
            ),
        ),
    )

    output_path = render_feature_pdf(paginate_feature(feature), tmp_path / "long-text.pdf")

    assert output_path.exists()
    assert len(PdfReader(output_path).pages) == 1


def test_render_feature_pdfs_returns_paths_and_summary(tmp_path: Path) -> None:
    print_jobs = paginate_features([make_feature(1, "FEAT-1"), make_feature(2, "FEAT-2")])
    pdf_paths, summary = render_feature_pdfs(print_jobs, tmp_path)

    assert [path.name for path in pdf_paths] == ["FEAT-1.pdf", "FEAT-2.pdf"]
    assert all(path.exists() for path in pdf_paths)
    assert summary.feature_count == 2
    assert summary.user_story_count == 3
    assert summary.card_count == 5
    assert summary.page_count == 2
    assert summary.pdf_count == 2


def test_card_dimensions_are_nine_by_six_centimeters() -> None:
    assert round(CARD_WIDTH, 2) == 255.12
    assert round(CARD_HEIGHT, 2) == 170.08


def test_wrap_text_does_not_add_ellipsis_when_single_line_fits() -> None:
    assert _wrap_text("Story YFPYC-419", 500, "Helvetica-Bold", 15, 1) == ["Story YFPYC-419"]
    assert _wrap_text("FEATURE TSYCPROGRM-233", 500, "Helvetica-Bold", 15, 1) == [
        "FEATURE TSYCPROGRM-233"
    ]
