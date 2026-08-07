from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import ValidationError

from backend.api.schemas import AnalyzeResponse, GenerateResponse
from backend.api.services import analyze_csv_bytes, generate_zip_from_csv_bytes
from backend.core.exceptions import JiraCardGeneratorError
from backend.core.models import ColorMode


app = FastAPI(title="Jira Card Generator", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/csv/analyze", response_model=AnalyzeResponse)
async def analyze_csv(file: UploadFile = File(...)) -> AnalyzeResponse:
    try:
        return analyze_csv_bytes(await _read_upload(file))
    except (JiraCardGeneratorError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/generate", response_class=Response)
async def generate_cards_zip(
    file: UploadFile = File(...),
    color_mode: ColorMode = Form(ColorMode.BLACK_AND_WHITE),
) -> Response:
    try:
        zip_content, summary = generate_zip_from_csv_bytes(await _read_upload(file), color_mode)
    except (JiraCardGeneratorError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    headers = {
        "Content-Disposition": 'attachment; filename="jira-cards.zip"',
        "X-Feature-Count": str(summary.feature_count),
        "X-User-Story-Count": str(summary.user_story_count),
        "X-Card-Count": str(summary.card_count),
        "X-Page-Count": str(summary.page_count),
        "X-Pdf-Count": str(summary.pdf_count),
    }
    return Response(content=zip_content, media_type="application/zip", headers=headers)


@app.post("/api/generate/summary", response_model=GenerateResponse)
async def generate_cards_summary(
    file: UploadFile = File(...),
    color_mode: ColorMode = Form(ColorMode.BLACK_AND_WHITE),
) -> GenerateResponse:
    try:
        _, summary = generate_zip_from_csv_bytes(await _read_upload(file), color_mode)
        return GenerateResponse(color_mode=color_mode, **summary.model_dump())
    except (JiraCardGeneratorError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


async def _read_upload(file: UploadFile) -> bytes:
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
        return content
    except HTTPException:
        raise
    except (JiraCardGeneratorError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
