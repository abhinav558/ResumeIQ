from dataclasses import dataclass, field

from app.models.achievement import AchievementProfile
from app.models.certification import CertificationProfile
from app.models.education import EducationProfile
from app.models.evidence import Evidence
from app.models.experience import ExperienceProfile
from app.models.metric import Metric
from app.models.project import ProjectProfile
from app.models.skill import SkillProfile


@dataclass(frozen=True, slots=True)
class CandidateProfile:
    """
    Central evidence-backed intelligence profile for a candidate.

    CandidateProfile is the domain object consumed by ResumeIQ's
    analysis, job matching, and future career intelligence services.
    Extraction and analysis are handled by dedicated services.
    """

    candidate_id: str

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None

    summary: str | None = None

    skills: tuple[SkillProfile, ...] = field(default_factory=tuple)
    projects: tuple[ProjectProfile, ...] = field(default_factory=tuple)
    experience: tuple[ExperienceProfile, ...] = field(default_factory=tuple)
    education: tuple[EducationProfile, ...] = field(default_factory=tuple)
    certifications: tuple[CertificationProfile, ...] = field(
        default_factory=tuple
    )
    achievements: tuple[AchievementProfile, ...] = field(
        default_factory=tuple
    )
    metrics: tuple[Metric, ...] = field(default_factory=tuple)

    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be empty")

        self._validate_optional_string(self.name, "name")
        self._validate_optional_string(self.email, "email")
        self._validate_optional_string(self.phone, "phone")
        self._validate_optional_string(self.linkedin, "linkedin")
        self._validate_optional_string(self.github, "github")
        self._validate_optional_string(self.summary, "summary")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        self._validate_model_collection(
            self.skills,
            SkillProfile,
            "skills",
        )
        self._validate_model_collection(
            self.projects,
            ProjectProfile,
            "projects",
        )
        self._validate_model_collection(
            self.experience,
            ExperienceProfile,
            "experience",
        )
        self._validate_model_collection(
            self.education,
            EducationProfile,
            "education",
        )
        self._validate_model_collection(
            self.certifications,
            CertificationProfile,
            "certifications",
        )
        self._validate_model_collection(
            self.achievements,
            AchievementProfile,
            "achievements",
        )
        self._validate_model_collection(
            self.metrics,
            Metric,
            "metrics",
        )
        self._validate_model_collection(
            self.evidence,
            Evidence,
            "evidence",
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
    def _validate_model_collection(
        values: tuple,
        expected_type: type,
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{field_name} must be a tuple")

        for item in values:
            if not isinstance(item, expected_type):
                raise TypeError(
                    f"every {field_name} item must be "
                    f"a {expected_type.__name__} instance"
                )

    @property
    def skill_count(self) -> int:
        """Return the number of candidate skills."""
        return len(self.skills)

    @property
    def project_count(self) -> int:
        """Return the number of projects."""
        return len(self.projects)

    @property
    def experience_count(self) -> int:
        """Return the number of experience entries."""
        return len(self.experience)

    @property
    def education_count(self) -> int:
        """Return the number of education entries."""
        return len(self.education)

    @property
    def certification_count(self) -> int:
        """Return the number of certifications."""
        return len(self.certifications)

    @property
    def achievement_count(self) -> int:
        """Return the number of achievements."""
        return len(self.achievements)

    @property
    def metric_count(self) -> int:
        """Return the number of measurable metrics."""
        return len(self.metrics)

    @property
    def evidence_count(self) -> int:
        """Return the total number of candidate evidence items."""
        return len(self.evidence)

    @property
    def has_contact_information(self) -> bool:
        """Return whether at least one contact method is available."""
        return any(
            value
            for value in (
                self.email,
                self.phone,
                self.linkedin,
                self.github,
            )
        )

    @property
    def has_professional_experience(self) -> bool:
        """Return whether professional experience is present."""
        return bool(self.experience)

    @property
    def has_projects(self) -> bool:
        """Return whether projects are present."""
        return bool(self.projects)

    @property
    def has_skills(self) -> bool:
        """Return whether skills are present."""
        return bool(self.skills)