from dataclasses import dataclass, field
from enum import Enum

from app.models.evidence import Evidence, EvidenceStrength


class ProjectQuality(str, Enum):
    """Qualitative classification of overall project quality."""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BASIC = "basic"


@dataclass(frozen=True, slots=True)
class ProjectProfile:
    """
    Evidence-backed representation of a resume project.

    This model represents structured project intelligence produced from
    existing project analysis. It does not perform project detection or
    scoring itself.
    """

    title: str
    technologies: tuple[str, ...] = field(default_factory=tuple)
    actions: tuple[str, ...] = field(default_factory=tuple)
    metrics: tuple[str, ...] = field(default_factory=tuple)
    deployment: tuple[str, ...] = field(default_factory=tuple)
    engineering: tuple[str, ...] = field(default_factory=tuple)
    strengths: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    score: float = 0.0
    quality: ProjectQuality = ProjectQuality.BASIC
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not 0.0 <= self.score <= 100.0:
            raise ValueError("score must be between 0.0 and 100.0")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        self._validate_string_collection(self.technologies, "technologies")
        self._validate_string_collection(self.actions, "actions")
        self._validate_string_collection(self.metrics, "metrics")
        self._validate_string_collection(self.deployment, "deployment")
        self._validate_string_collection(self.engineering, "engineering")
        self._validate_string_collection(self.strengths, "strengths")

        for item in self.evidence:
            if not isinstance(item, Evidence):
                raise TypeError(
                    "every evidence item must be an Evidence instance"
                )

    @staticmethod
    def _validate_string_collection(
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{field_name} must be a tuple")

        for value in values:
            if not isinstance(value, str):
                raise TypeError(f"every {field_name} item must be a string")

            if not value.strip():
                raise ValueError(
                    f"{field_name} must not contain empty strings"
                )

    @property
    def evidence_count(self) -> int:
        """Return the number of evidence items supporting this project."""
        return len(self.evidence)

    @property
    def technology_count(self) -> int:
        """Return the number of technologies associated with the project."""
        return len(self.technologies)

    @property
    def has_metrics(self) -> bool:
        """Return whether the project contains measurable outcomes."""
        return bool(self.metrics)

    @property
    def has_deployment(self) -> bool:
        """Return whether deployment information was detected."""
        return bool(self.deployment)

    @property
    def has_strong_evidence(self) -> bool:
        """Return whether at least one strong or verified evidence item exists."""
        return any(
            item.strength
            in {
                EvidenceStrength.STRONG,
                EvidenceStrength.VERIFIED,
            }
            for item in self.evidence
        )