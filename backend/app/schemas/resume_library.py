"""
ResumeIQ - Resume Library Schemas.

Typed request and response contracts for persistent, user-owned resumes.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# RESUME CREATE
# ============================================================================

class ResumeCreateRequest(BaseModel):
    """Request used to save a newly analyzed resume."""

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Display name for the saved resume.",
    )

    resume_text: str = Field(
        min_length=1,
        description="Plain-text resume content.",
    )

    analysis_json: str = Field(
        min_length=1,
        description="Serialized ResumeIQ analysis result.",
    )


# ============================================================================
# RESUME RESPONSE
# ============================================================================

class ResumeResponse(BaseModel):
    """Response representing a saved resume."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: str
    user_id: str
    name: str
    resume_text: str
    analysis_json: str
    created_at: datetime
    updated_at: datetime


# ============================================================================
# RESUME SUMMARY
# ============================================================================

class ResumeSummaryResponse(BaseModel):
    """Lightweight resume representation for the Resume Library."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: str
    name: str
    created_at: datetime
    updated_at: datetime


# ============================================================================
# RESUME UPDATE
# ============================================================================

class ResumeUpdateRequest(BaseModel):
    """Request used to update a saved resume."""

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated display name.",
    )

    resume_text: str | None = Field(
        default=None,
        min_length=1,
        description="Updated plain-text resume content.",
    )

    analysis_json: str | None = Field(
        default=None,
        min_length=1,
        description="Updated serialized analysis result.",
    )