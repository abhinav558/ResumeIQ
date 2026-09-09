from dataclasses import dataclass
from enum import Enum


class EvidenceType(str, Enum):
    """How strongly the candidate's claim is supported."""

    DECLARED = "declared"
    DEMONSTRATED = "demonstrated"
    VERIFIED = "verified"


class EvidenceStrength(str, Enum):
    """Strength of the evidence supporting an entity."""

    NONE = "none"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERIFIED = "verified"


class EvidenceSource(str, Enum):
    """Where the evidence was extracted from."""

    RESUME = "resume"
    SKILL_SECTION = "skill_section"
    PROJECT = "project"
    EXPERIENCE = "experience"
    INTERNSHIP = "internship"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    ACHIEVEMENT = "achievement"


@dataclass(frozen=True, slots=True)
class Evidence:
    """
    Immutable evidence supporting an extracted candidate intelligence item.

    Confidence represents ResumeIQ's confidence that the evidence was
    correctly interpreted. It is intentionally separate from strength,
    which represents how strongly the evidence supports the candidate claim.
    """

    entity_type: str
    entity_id: str
    evidence_type: EvidenceType
    source: EvidenceSource
    text: str
    strength: EvidenceStrength = EvidenceStrength.WEAK
    confidence: float = 0.0
    location: str | None = None
    relationship: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_type.strip():
            raise ValueError("entity_type must not be empty")

        if not self.entity_id.strip():
            raise ValueError("entity_id must not be empty")

        if not self.text.strip():
            raise ValueError("text must not be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if self.location is not None and not self.location.strip():
            raise ValueError("location must be non-empty when provided")

        if self.relationship is not None and not self.relationship.strip():
            raise ValueError("relationship must be non-empty when provided")