"""
ResumeIQ - Resume Intelligence API Routes.

Production API endpoints for:

POST /resume/analyze
    Upload a resume and generate complete resume intelligence.

POST /resume/match
    Compare resume text against a target job description.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.config import settings
from app.schemas.resume import (
    ErrorResponse,
    JobMatchResponse,
    ResumeAnalysisResponse,
)
from app.services.analyzer import analyze_resume
from app.services.job_matcher import compare_resume_job
from app.services.parser import extract_text


router = APIRouter(
    tags=["Resume Intelligence"],
)


# =====================================================================
# Helpers
# =====================================================================


def _get_file_extension(filename: str) -> str:
    """Return a normalized file extension."""

    if not filename or "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[1].lower()


def _validate_job_description(
    job_description: str | None,
) -> str:
    """
    Validate and normalize a job description.

    Empty or whitespace-only descriptions are treated as
    invalid client input and return HTTP 400.
    """

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required.",
        )

    normalized = job_description.strip()

    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required.",
        )

    return normalized


async def _read_resume_file(
    file: UploadFile,
) -> tuple[str, str]:
    """
    Validate, read and extract text from an uploaded resume.

    Returns:
        tuple[resume_text, filename]
    """

    # -----------------------------------------------------------------
    # Filename validation
    # -----------------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A resume filename is required.",
        )

    filename = file.filename.strip()

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A resume filename is required.",
        )

    # -----------------------------------------------------------------
    # Extension validation
    # -----------------------------------------------------------------

    extension = _get_file_extension(filename)

    allowed_extensions = {
        extension.lower()
        for extension in settings.allowed_extensions
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. "
                f"Allowed types: "
                f"{', '.join(settings.allowed_extensions)}"
            ),
        )

    # -----------------------------------------------------------------
    # File size protection
    # -----------------------------------------------------------------

    max_bytes = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    contents = await file.read(max_bytes + 1)

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Uploaded file exceeds the maximum "
                f"allowed size of "
                f"{settings.max_upload_size_mb} MB."
            ),
        )

    # -----------------------------------------------------------------
    # Empty file validation
    # -----------------------------------------------------------------

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded resume is empty.",
        )

    # -----------------------------------------------------------------
    # Text extraction
    # -----------------------------------------------------------------

    try:
        resume_text = extract_text(
            contents,
            filename,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Unable to extract text from the "
                "uploaded resume."
            ),
        ) from exc

    # -----------------------------------------------------------------
    # Extracted text validation
    # -----------------------------------------------------------------

    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No readable text could be extracted "
                "from the uploaded resume."
            ),
        )

    return resume_text.strip(), filename


# =====================================================================
# Resume Analysis
# =====================================================================


@router.post(
    "/resume/analyze",
    response_model=ResumeAnalysisResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid resume upload.",
        },
        413: {
            "model": ErrorResponse,
            "description": "Uploaded file is too large.",
        },
        422: {
            "model": ErrorResponse,
            "description": "Resume could not be processed.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Resume analysis failed.",
        },
    },
    status_code=status.HTTP_200_OK,
)
async def analyze_resume_file(
    file: UploadFile = File(...),
) -> ResumeAnalysisResponse:
    """
    Analyze an uploaded resume.
    """

    resume_text, _ = await _read_resume_file(file)

    try:
        result = analyze_resume(resume_text)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume analysis failed unexpectedly.",
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume analysis returned an invalid result.",
        )

    result = {
        **result,
        "resume_text": resume_text,
    }

    try:
        return ResumeAnalysisResponse.model_validate(result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Resume analysis returned an invalid "
                "response format."
            ),
        ) from exc


# =====================================================================
# Resume → Job Matching
# =====================================================================


@router.post(
    "/resume/match",
    response_model=JobMatchResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid matching request.",
        },
        413: {
            "model": ErrorResponse,
            "description": "Uploaded resume is too large.",
        },
        422: {
            "model": ErrorResponse,
            "description": (
                "Resume or job description could not be processed."
            ),
        },
        500: {
            "model": ErrorResponse,
            "description": "Job matching failed.",
        },
    },
    status_code=status.HTTP_200_OK,
)
async def match_resume_to_job(
    file: UploadFile = File(...),
    job_description: str | None = Form(None),
) -> JobMatchResponse:
    """
    Compare an uploaded resume against a job description.

    Request:
        multipart/form-data

        file = resume PDF/DOCX/TXT
        job_description = target job description
    """

    # -----------------------------------------------------------------
    # Validate job description explicitly.
    #
    # Form(None) allows the endpoint to control the API contract and
    # return a consistent HTTP 400 for missing/empty input.
    # -----------------------------------------------------------------

    normalized_job_description = _validate_job_description(
        job_description
    )

    # -----------------------------------------------------------------
    # Read and extract resume
    # -----------------------------------------------------------------

    resume_text, _ = await _read_resume_file(file)

    # -----------------------------------------------------------------
    # Compare resume against job
    # -----------------------------------------------------------------

    try:
        result = compare_resume_job(
            resume_text,
            normalized_job_description,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume-job matching failed unexpectedly.",
        ) from exc

    # -----------------------------------------------------------------
    # Validate response contract
    # -----------------------------------------------------------------

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job matching returned an invalid result.",
        )

    try:
        return JobMatchResponse.model_validate(result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Job matching returned an invalid "
                "response format."
            ),
        ) from exc