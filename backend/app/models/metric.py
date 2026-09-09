from dataclasses import dataclass
from enum import Enum


class MetricType(str, Enum):
    """Normalized type of measurable result."""

    PERCENTAGE = "percentage"
    COUNT = "count"
    CURRENCY = "currency"
    TIME = "time"
    RATING = "rating"
    SCALE = "scale"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Metric:
    """
    Structured representation of a measurable resume result.

    The model stores the metric exactly as supported by resume evidence.
    It does not infer or manufacture business impact.
    """

    value: str
    metric_type: MetricType = MetricType.OTHER

    description: str | None = None
    source_text: str | None = None

    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("value must not be empty")

        self._validate_optional_string(
            self.description,
            "description",
        )
        self._validate_optional_string(
            self.source_text,
            "source_text",
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

    @property
    def has_description(self) -> bool:
        """Return whether contextual description is available."""
        return self.description is not None

    @property
    def has_source(self) -> bool:
        """Return whether the original supporting text is available."""
        return self.source_text is not None

    @property
    def is_high_confidence(self) -> bool:
        """Return whether ResumeIQ is highly confident in this metric."""
        return self.confidence >= 0.80