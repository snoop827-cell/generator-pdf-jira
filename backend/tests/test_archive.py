from pathlib import Path
from zipfile import ZipFile

import pytest

from backend.core.exceptions import JiraCardGeneratorError
from backend.services.archive import create_zip_archive


def test_create_zip_archive_contains_pdfs_sorted_by_name(tmp_path: Path) -> None:
    second_pdf = tmp_path / "FEAT-2.pdf"
    first_pdf = tmp_path / "FEAT-1.pdf"
    second_pdf.write_bytes(b"second")
    first_pdf.write_bytes(b"first")

    output_path = create_zip_archive([second_pdf, first_pdf], tmp_path / "cards.zip")

    with ZipFile(output_path) as archive:
        assert archive.namelist() == ["FEAT-1.pdf", "FEAT-2.pdf"]
        assert archive.read("FEAT-1.pdf") == b"first"
        assert archive.read("FEAT-2.pdf") == b"second"


def test_create_zip_archive_rejects_empty_pdf_list(tmp_path: Path) -> None:
    with pytest.raises(JiraCardGeneratorError):
        create_zip_archive([], tmp_path / "cards.zip")


def test_create_zip_archive_rejects_missing_pdf(tmp_path: Path) -> None:
    with pytest.raises(JiraCardGeneratorError):
        create_zip_archive([tmp_path / "missing.pdf"], tmp_path / "cards.zip")

