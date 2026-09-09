from dataclasses import dataclass, field
from enum import Enum

from app.models.evidence import Evidence


class AchievementType(str, Enum):
    """Normalized type of candidate achievement."""

    AWARD = "award"
    COMPETITION = "competition"
    PUBLICATION = "publication"
    LEADERSHIP = "leadership"
    OPEN_SOURCE = "open_source"
    HACKATHON = "hackathon"
    ACADEMIC = "academic"
    RECOGNITION = "recognition"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class AchievementProfile:
    """
    Evidence-backed representation of a candidate achievement.

    This model stores structured achievement intelligence. Detection,
    classification, and scoring remain responsibilities of services.
    """

    title: str
    achievement_type: AchievementType = AchievementType.OTHER

    organization: str | None = None
    date: str | None = None
    description: str | None = None

    metrics: tuple[str, ...] = field(default_factory=tuple)
    skills: tuple[str, ...] = field(default_factory=tuple)

    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

        self._validate_optional_string(
            self.organization,
            "organization",
        )
        self._validate_optional_string(
            self.date,
            "date",
        )
        self._validate_optional_string(
            self.description,
            "description",
        )

        self._validate_string_collection(
            self.metrics,
            "metrics",
        )
        self._validate_string_collection(
            self.skills,
            "skills",
        )

        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")

        for item in self.evidence:
            if not isinstance(item, Evidence):
                raise TypeError(
                    "every evidence item must be an Evidence instance"
                )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

    @staticmethod
    def _validate_optional_string(
        value: str | None,
        field_name: str,
    ) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must be a string or None"
                )

            if not value.strip():
                raise ValueError(
                    f"{field_name} must be non-empty when provided"
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
                raise TypeError(
                    f"every {field_name} item must be a string"
                )

            if not value.strip():
                raise ValueError(
                    f"{field_name} must not contain empty strings"
                )

    @property
    def evidence_count(self) -> int:
        """Return the number of supporting evidence items."""
        return len(self.evidence)

    @property
    def metric_count(self) -> int:
        """Return the number of measurable achievement details."""
        return len(self.metrics)

    @property
    def skill_count(self) -> int:
        """Return the number of skills associated with the achievement."""
        return len(self.skills)

    @property
    def has_metrics(self) -> bool:
        """Return whether measurable results were detected."""
        return bool(self.metrics)

    @property
    def has_organization(self) -> bool:
        """Return whether an organization is associated with the achievement."""
        return self.organization is not None