"""
ResumeIQ - Resume Library API.

Authenticated CRUD endpoints for persistent, user-owned resumes.
"""

from __future__ import annotations

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.repositories.resume_repository import (
    create_resume,
    delete_resume,
    get_resume_by_id,
    get_resumes_by_user,
    update_resume,
)
from app.schemas.resume_library import (
    ResumeCreateRequest,
    ResumeResponse,
    ResumeSummaryResponse,
    ResumeUpdateRequest,
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Library"],
)


# ============================================================================
# CREATE
# ============================================================================


@router.post(
    "",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_resume(
    payload: ResumeCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Save an analyzed resume for the authenticated user.
    """

    # Validate that the stored analysis is valid JSON before persisting it.
    try:
        json.loads(payload.analysis_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis JSON.",
        ) from exc

    resume = create_resume(
        db,
        resume_id=str(uuid4()),
        user_id=current_user.id,
        name=payload.name,
        resume_text=payload.resume_text,
        analysis_json=payload.analysis_json,
    )

    return ResumeResponse.model_validate(resume)


# ============================================================================
# LIST
# ============================================================================


@router.get(
    "",
    response_model=list[ResumeSummaryResponse],
)
async def list_resumes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeSummaryResponse]:
    """
    Return all resumes belonging to the authenticated user.
    """

    resumes = get_resumes_by_user(
        db,
        user_id=current_user.id,
    )

    return [
        ResumeSummaryResponse.model_validate(resume)
        for resume in resumes
    ]


# ============================================================================
# GET
# ============================================================================


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
)
async def get_saved_resume(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Return one resume belonging to the authenticated user.
    """

    resume = get_resume_by_id(
        db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    return ResumeResponse.model_validate(resume)


# ============================================================================
# UPDATE
# ============================================================================


@router.put(
    "/{resume_id}",
    response_model=ResumeResponse,
)
async def update_saved_resume(
    resume_id: str,
    payload: ResumeUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Update a resume belonging to the authenticated user.
    """

    resume = get_resume_by_id(
        db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    if (
        payload.name is None
        and payload.resume_text is None
        and payload.analysis_json is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update.",
        )

    if payload.analysis_json is not None:
        try:
            json.loads(payload.analysis_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid analysis JSON.",
            ) from exc

    updated_resume = update_resume(
        db,
        resume=resume,
        name=payload.name,
        resume_text=payload.resume_text,
        analysis_json=payload.analysis_json,
    )

    return ResumeResponse.model_validate(updated_resume)


# ============================================================================
# DELETE
# ============================================================================


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_saved_resume(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a resume belonging to the authenticated user.
    """

    resume = get_resume_by_id(
        db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    delete_resume(
        db,
        resume=resume,
    )