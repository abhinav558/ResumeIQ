from dataclasses import dataclass, field
from enum import Enum

from app.models.evidence import Evidence


class EducationLevel(str, Enum):
    """Normalized education level."""

    HIGH_SCHOOL = "high_school"
    DIPLOMA = "diploma"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class EducationProfile:
    """
    Structured representation of a candidate's education.

    Parsing and extraction remain responsibilities of dedicated services.
    This model only represents validated education intelligence.
    """

    degree: str
    field_of_study: str | None = None
    institution: str | None = None
    education_level: EducationLevel = EducationLevel.OTHER

    start_date: str | None = None
    end_date: str | None = None

    cgpa: float | None = None
    percentage: float | None = None

    achievements: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.degree.strip():
            raise ValueError("degree must not be empty")

        self._validate_optional_string(
            self.field_of_study,
            "field_of_study",
        )
        self._validate_optional_string(
            self.institution,
            "institution",
        )
        self._validate_optional_string(
            self.start_date,
            "start_date",
        )
        self._validate_optional_string(
            self.end_date,
            "end_date",
        )

        if self.cgpa is not None:
            self._validate_number(
                self.cgpa,
                "cgpa",
                minimum=0.0,
            )

        if self.percentage is not None:
            self._validate_number(
                self.percentage,
                "percentage",
                minimum=0.0,
                maximum=100.0,
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        self._validate_string_collection(
            self.achievements,
            "achievements",
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
                raise TypeError(
                    f"{field_name} must be a string or None"
                )

            if not value.strip():
                raise ValueError(
                    f"{field_name} must be non-empty when provided"
                )

    @staticmethod
    def _validate_number(
        value: float,
        field_name: str,
        minimum: float,
        maximum: float | None = None,
    ) -> None:
        if isinstance(value, bool):
            raise TypeError(f"{field_name} must be a number")

        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number")

        if value < minimum:
            raise ValueError(
                f"{field_name} must be at least {minimum}"
            )

        if maximum is not None and value > maximum:
            raise ValueError(
                f"{field_name} must be at most {maximum}"
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
    def achievement_count(self) -> int:
        """Return the number of education achievements."""
        return len(self.achievements)

    @property
    def has_cgpa(self) -> bool:
        """Return whether CGPA information is available."""
        return self.cgpa is not None

    @property
    def has_percentage(self) -> bool:
        """Return whether percentage information is available."""
        return self.percentage is not None

    @property
    def has_academic_metric(self) -> bool:
        """Return whether any academic performance metric exists."""
        return self.has_cgpa or self.has_percentage