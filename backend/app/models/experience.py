from dataclasses import dataclass, field
from enum import Enum

from app.models.evidence import Evidence


class ExperienceType(str, Enum):
    """Type of professional experience."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    VOLUNTEER = "volunteer"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class ExperienceProfile:
    """
    Evidence-backed representation of a candidate's work experience.

    This model stores structured experience intelligence. Detection,
    parsing, duration calculation, and scoring remain responsibilities
    of dedicated services.
    """

    title: str
    company: str | None = None
    experience_type: ExperienceType = ExperienceType.OTHER

    start_date: str | None = None
    end_date: str | None = None
    duration_months: int | None = None
    is_current: bool = False

    technologies: tuple[str, ...] = field(default_factory=tuple)
    achievements: tuple[str, ...] = field(default_factory=tuple)
    metrics: tuple[str, ...] = field(default_factory=tuple)

    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

        self._validate_optional_string(self.company, "company")
        self._validate_optional_string(self.start_date, "start_date")
        self._validate_optional_string(self.end_date, "end_date")

        if self.duration_months is not None:
            if isinstance(self.duration_months, bool):
                raise TypeError("duration_months must be an integer")

            if not isinstance(self.duration_months, int):
                raise TypeError("duration_months must be an integer")

            if self.duration_months < 0:
                raise ValueError("duration_months must not be negative")

        if not isinstance(self.is_current, bool):
            raise TypeError("is_current must be a boolean")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        self._validate_string_collection(
            self.technologies,
            "technologies",
        )
        self._validate_string_collection(
            self.achievements,
            "achievements",
        )
        self._validate_string_collection(
            self.metrics,
            "metrics",
        )

        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")

        for item in self.evidence:
            if not isinstance(item, Evidence):
                raise TypeError(
                    "every evidence item must be an Evidence instance"
                )

    @staticmethod
    def _validate_optional_string(
        value: str | None,
        field_name: str,
    ) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string or None")

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
        """Return the number of evidence items."""
        return len(self.evidence)

    @property
    def technology_count(self) -> int:
        """Return the number of technologies."""
        return len(self.technologies)

    @property
    def achievement_count(self) -> int:
        """Return the number of documented achievements."""
        return len(self.achievements)

    @property
    def metric_count(self) -> int:
        """Return the number of measurable outcomes."""
        return len(self.metrics)

    @property
    def has_metrics(self) -> bool:
        """Return whether measurable outcomes were detected."""
        return bool(self.metrics)

    @property
    def has_achievements(self) -> bool:
        """Return whether achievements were detected."""
        return bool(self.achievements)

    @property
    def is_internship(self) -> bool:
        """Return whether this experience is an internship."""
        return self.experience_type == ExperienceType.INTERNSHIP