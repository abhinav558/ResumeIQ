from dataclasses import dataclass, field
from enum import Enum

from app.models.evidence import Evidence, EvidenceStrength


class SkillCategory(str, Enum):
    """High-level classification for a candidate skill."""

    PROGRAMMING = "programming"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    AI_ML = "ai_ml"
    CLOUD = "cloud"
    DEVOPS = "devops"
    TOOLS = "tools"
    ENGINEERING = "engineering"
    NETWORKING = "networking"
    BLOCKCHAIN = "blockchain"
    MOBILE = "mobile"
    SECURITY = "security"
    PROFESSIONAL = "professional"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class SkillProfile:
    """
    Evidence-backed representation of a candidate skill.

    A SkillProfile describes what ResumeIQ knows about a skill.
    Evidence is the source of truth; confidence represents the
    system's confidence in its interpretation.
    """

    canonical_name: str
    category: SkillCategory
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    strength: EvidenceStrength = EvidenceStrength.NONE
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.canonical_name.strip():
            raise ValueError("canonical_name must not be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")

        for item in self.evidence:
            if not isinstance(item, Evidence):
                raise TypeError("every evidence item must be an Evidence instance")

    @property
    def evidence_count(self) -> int:
        """Return the number of evidence items supporting this skill."""
        return len(self.evidence)

    @property
    def is_demonstrated(self) -> bool:
        """Return whether the skill has demonstrated or verified evidence."""
        return any(
            item.evidence_type.value in {"demonstrated", "verified"}
            for item in self.evidence
        )

    @property
    def is_verified(self) -> bool:
        """Return whether the skill has verified evidence."""
        return any(
            item.evidence_type.value == "verified"
            for item in self.evidence
        )