from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from backend.core.exceptions import JiraCardGeneratorError


def create_zip_archive(pdf_paths: list[Path], output_path: str | Path) -> Path:
    """Create a deterministic ZIP archive containing the generated PDFs."""
    if not pdf_paths:
        raise JiraCardGeneratorError("Cannot create a ZIP archive without PDF files.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    missing_files = [str(path) for path in pdf_paths if not path.exists()]
    if missing_files:
        raise JiraCardGeneratorError(f"Missing PDF files: {', '.join(missing_files)}")

    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as archive:
        for pdf_path in sorted(pdf_paths, key=lambda path: path.name):
            archive.write(pdf_path, arcname=pdf_path.name)

    return output

