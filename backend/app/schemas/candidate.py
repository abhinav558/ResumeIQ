from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    entity_type: str
    entity_id: str
    evidence_type: str
    source: str
    text: str
    strength: str = "weak"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    location: str | None = None
    relationship: str | None = None


class SkillProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    canonical_name: str
    category: str
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    strength: str = "none"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ProjectProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    title: str
    technologies: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    metrics: list[Any] = Field(default_factory=list)
    deployment: list[str] = Field(default_factory=list)
    engineering: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    quality: str = "basic"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExperienceProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    title: str
    company: str | None = None
    experience_type: str = "other"
    start_date: date | None = None
    end_date: date | None = None
    duration_months: int | None = Field(default=None, ge=0)
    is_current: bool = False
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    metrics: list[Any] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EducationProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    degree: str | None = None
    field_of_study: str | None = None
    institution: str | None = None
    education_level: str = "other"
    start_date: date | None = None
    end_date: date | None = None
    cgpa: float | None = Field(default=None, ge=0.0)
    percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    achievements: list[str] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class CertificationProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    name: str
    provider: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verified: bool = False


class AchievementProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    title: str
    achievement_type: str = "other"
    organization: str | None = None
    date: date | None = None
    description: str | None = None
    metrics: list[Any] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class MetricSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    value: float | str
    metric_type: str = "other"
    description: str | None = None
    source_text: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class CandidateProfileSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="ignore")

    candidate_id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None

    skills: list[SkillProfileSchema] = Field(default_factory=list)
    projects: list[ProjectProfileSchema] = Field(default_factory=list)
    experience: list[ExperienceProfileSchema] = Field(default_factory=list)
    education: list[EducationProfileSchema] = Field(default_factory=list)
    certifications: list[CertificationProfileSchema] = Field(default_factory=list)
    achievements: list[AchievementProfileSchema] = Field(default_factory=list)
    metrics: list[MetricSchema] = Field(default_factory=list)
    evidence: list[EvidenceSchema] = Field(default_factory=list)

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)