from dataclasses import dataclass, field

from app.models.evidence import Evidence


@dataclass(frozen=True, slots=True)
class CertificationProfile:
    """
    Structured representation of a professional certification.

    Verification, provider trust, and certification relevance are handled
    by dedicated services. This model stores validated certification data.
    """

    name: str
    provider: str | None = None

    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None

    skills: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

    confidence: float = 0.0
    verified: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        self._validate_optional_string(self.provider, "provider")
        self._validate_optional_string(self.issue_date, "issue_date")
        self._validate_optional_string(self.expiry_date, "expiry_date")
        self._validate_optional_string(
            self.credential_id,
            "credential_id",
        )
        self._validate_optional_string(
            self.credential_url,
            "credential_url",
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

        if not isinstance(self.verified, bool):
            raise TypeError("verified must be a boolean")

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
    def skill_count(self) -> int:
        """Return the number of skills associated with the certification."""
        return len(self.skills)

    @property
    def has_provider(self) -> bool:
        """Return whether a certification provider is available."""
        return self.provider is not None

    @property
    def has_credential(self) -> bool:
        """Return whether credential information is available."""
        return bool(
            self.credential_id or self.credential_url
        )