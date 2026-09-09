"""
ResumeIQ - Resume API Schemas.

Typed request and response contracts used by the ResumeIQ API.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# Generic API
# =====================================================================

class HealthResponse(BaseModel):
    """Response returned by health endpoints."""

    model_config = ConfigDict(
        extra="forbid",
    )

    status: str
    service: str
    version: str


# =====================================================================
# Resume Analysis
# =====================================================================

class ResumeAnalysisResponse(BaseModel):
    """
    Complete ResumeIQ analysis response.
    """

    model_config = ConfigDict(
        extra="allow",
    )

    resume_text: str = Field(
        default="",
        description="Extracted plain-text content of the uploaded resume.",
    )

    resume_intelligence_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    rating: str = ""

    confidence: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    sections_detected: Dict[str, Any] = Field(
        default_factory=dict,
    )

    ats_analysis: Dict[str, Any] = Field(
        default_factory=dict,
    )

    skills_analysis: Dict[str, Any] = Field(
        default_factory=dict,
    )

    project_analysis: Dict[str, Any] = Field(
        default_factory=dict,
    )

    experience_analysis: Dict[str, Any] = Field(
        default_factory=dict,
    )

    certifications: Dict[str, Any] = Field(
        default_factory=dict,
    )

    education: Dict[str, Any] = Field(
        default_factory=dict,
    )

    achievement_analysis: Dict[str, Any] = Field(
        default_factory=dict,
    )

    recommendations: List[Any] = Field(
        default_factory=list,
    )


# =====================================================================
# Job Matching Request
# =====================================================================

class JobMatchRequest(BaseModel):
    """
    Request used for resume-to-job matching.

    This model is retained for compatibility with clients
    that send resume text directly.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    resume: str = Field(
        min_length=1,
        description="Plain-text resume content.",
    )

    job_description: str = Field(
        min_length=1,
        description="Target job description.",
    )


# =====================================================================
# Job Matching Response
# =====================================================================

class JobMatchResponse(BaseModel):
    """
    Production resume-to-job compatibility response.

    The schema explicitly represents the complete output of
    compare_resume_job().
    """

    model_config = ConfigDict(
        extra="allow",
    )

    # -----------------------------------------------------------------
    # Core Match
    # -----------------------------------------------------------------

    match_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Direct percentage of matched job requirements.",
    )

    match_level: str = Field(
        default="No Match",
        description="Human-readable match level.",
    )

    application_readiness: str = Field(
        default="Low Alignment",
        description="Overall readiness to apply for the role.",
    )

    # -----------------------------------------------------------------
    # Skills
    # -----------------------------------------------------------------

    matched_skills: List[str] = Field(
        default_factory=list,
        description="Requirements demonstrated by the resume.",
    )

    missing_skills: List[str] = Field(
        default_factory=list,
        description="Requirements not found in the resume.",
    )

    critical_missing_skills: List[str] = Field(
        default_factory=list,
        description="Missing must-have requirements.",
    )

    # -----------------------------------------------------------------
    # Category Intelligence
    # -----------------------------------------------------------------

    resume_categories: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Resume skills grouped by category.",
    )

    job_categories: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Job requirements grouped by category.",
    )

    category_coverage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Category-level requirement coverage.",
    )

    # -----------------------------------------------------------------
    # Requirement Intelligence
    # -----------------------------------------------------------------

    requirements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed requirement-level matching results.",
    )

    requirement_priorities: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Requirements grouped by priority.",
    )

    requirement_weights: Dict[str, int] = Field(
        default_factory=dict,
        description="Weight assigned to each requirement.",
    )

    requirement_priority_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Number of requirements per priority.",
    )

    requirement_coverage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Requirement coverage and weighted matching metrics.",
    )

    # -----------------------------------------------------------------
    # Experience Intelligence
    # -----------------------------------------------------------------

    experience_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Overall and technical experience analysis.",
    )

    resume_experience_years: float | None = Field(
        default=None,
        ge=0,
        description="Explicit overall experience found in the resume.",
    )

    experience_gap: Dict[str, Any] = Field(
        default_factory=dict,
        description="Experience requirement gap analysis.",
    )

    # -----------------------------------------------------------------
    # Recommendations
    # -----------------------------------------------------------------

    suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations.",
    )

    # -----------------------------------------------------------------
    # Backward Compatibility
    # -----------------------------------------------------------------

    suggestion: str = Field(
        default="",
        description="Primary recommendation retained for compatibility.",
    )


# =====================================================================
# Error Responses
# =====================================================================

class ErrorResponse(BaseModel):
    """
    Standard API error response.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    error: str
    message: str
    details: Dict[str, Any] = Field(
        default_factory=dict,
    )