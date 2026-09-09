"""
ResumeIQ - Candidate Profile Builder.

Transforms analyzer output into validated, evidence-backed domain models.

Design principles:
- Never invent resume facts.
- Ignore malformed analyzer items safely.
- Preserve structured evidence.
- Support both current and legacy analyzer output shapes.
- Keep domain-model construction aligned with the actual model schemas.
"""

from __future__ import annotations

from typing import Any, Iterable

from app.models.achievement import AchievementProfile, AchievementType
from app.models.candidate import CandidateProfile
from app.models.certification import CertificationProfile
from app.models.education import EducationLevel, EducationProfile
from app.models.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceStrength,
    EvidenceType,
)
from app.models.experience import ExperienceProfile, ExperienceType
from app.models.metric import Metric, MetricType
from app.models.project import ProjectProfile, ProjectQuality
from app.models.skill import SkillCategory, SkillProfile


class CandidateProfileBuilder:
    """Build validated CandidateProfile objects from analyzer output."""

    # ================================================================
    # Generic helpers
    # ================================================================

    @staticmethod
    def _safe_string(value: Any) -> str | None:
        """Return a cleaned string or None."""
        if isinstance(value, str):
            value = value.strip()
            return value or None

        return None

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        """Safely convert a value to a float in [0, 1]."""
        if value is None or isinstance(value, bool):
            return default

        try:
            number = float(value)

            if number > 1.0:
                number /= 100.0

            return max(0.0, min(1.0, number))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_score(value: Any, default: float = 0.0) -> float:
        """Safely convert a value to a score in [0, 100]."""
        if value is None or isinstance(value, bool):
            return default

        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_bool(value: Any, default: bool = False) -> bool:
        """Safely normalize boolean-like values."""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {
                "true",
                "yes",
                "1",
                "verified",
                "current",
            }:
                return True

            if normalized in {
                "false",
                "no",
                "0",
                "unverified",
            }:
                return False

        if isinstance(value, (int, float)):
            return bool(value)

        return default

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """Normalize supported collection types into a list."""
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        if isinstance(value, set):
            return list(value)

        if isinstance(value, str):
            return [value]

        return []

    @classmethod
    def _unique_strings(cls, values: Any) -> tuple[str, ...]:
        """Normalize and deduplicate strings while preserving order."""
        result: list[str] = []
        seen: set[str] = set()

        for value in cls._as_list(values):
            text = cls._safe_string(value)

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(text)

        return tuple(result)

    @classmethod
    def _clamp_confidence(cls, value: Any) -> float:
        """Normalize confidence into [0, 1]."""
        return cls._safe_float(value)

    @classmethod
    def _profile_item_confidence(
        cls,
        item: dict[str, Any],
        default: float = 0.70,
    ) -> float:
        """
        Normalize profile-level confidence.

        An explicitly supplied confidence is authoritative, including
        an explicit 0.0 value. When confidence is absent, use the
        established 70% default rather than treating missing data as
        zero-confidence data.
        """
        if "confidence" not in item:
            return default

        return cls._clamp_confidence(item.get("confidence"))

    @staticmethod
    def _enum_value(value: Any) -> str | None:
        """Extract a normalized enum/string value."""
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip().lower()
            return value or None

        enum_value = getattr(value, "value", None)

        if isinstance(enum_value, str):
            enum_value = enum_value.strip().lower()
            return enum_value or None

        return None

    # ================================================================
    # Enum normalization
    # ================================================================

    @classmethod
    def _skill_category(cls, value: Any) -> SkillCategory:
        normalized = cls._enum_value(value)

        mapping = {
            "programming": SkillCategory.PROGRAMMING,
            "frontend": SkillCategory.FRONTEND,
            "front_end": SkillCategory.FRONTEND,
            "backend": SkillCategory.BACKEND,
            "back_end": SkillCategory.BACKEND,
            "database": SkillCategory.DATABASE,
            "databases": SkillCategory.DATABASE,
            "ai_ml": SkillCategory.AI_ML,
            "ai/ml": SkillCategory.AI_ML,
            "ai-ml": SkillCategory.AI_ML,
            "ai": SkillCategory.AI_ML,
            "ml": SkillCategory.AI_ML,
            "machine_learning": SkillCategory.AI_ML,
            "machine learning": SkillCategory.AI_ML,
            "cloud": SkillCategory.CLOUD,
            "devops": SkillCategory.DEVOPS,
            "tools": SkillCategory.TOOLS,
            "engineering": SkillCategory.ENGINEERING,
            "networking": SkillCategory.NETWORKING,
            "blockchain": SkillCategory.BLOCKCHAIN,
            "mobile": SkillCategory.MOBILE,
            "security": SkillCategory.SECURITY,
            "professional": SkillCategory.PROFESSIONAL,
            "other": SkillCategory.OTHER,
        }

        return mapping.get(
            normalized or "",
            SkillCategory.OTHER,
        )

    @classmethod
    def _project_quality(cls, value: Any) -> ProjectQuality:
        normalized = cls._enum_value(value)

        mapping = {
            "excellent": ProjectQuality.EXCELLENT,
            "good": ProjectQuality.GOOD,
            "average": ProjectQuality.AVERAGE,
            "basic": ProjectQuality.BASIC,
        }

        return mapping.get(
            normalized or "",
            ProjectQuality.BASIC,
        )

    @classmethod
    def _experience_type(cls, value: Any) -> ExperienceType:
        normalized = cls._enum_value(value)

        mapping = {
            "full_time": ExperienceType.FULL_TIME,
            "full-time": ExperienceType.FULL_TIME,
            "fulltime": ExperienceType.FULL_TIME,
            "part_time": ExperienceType.PART_TIME,
            "part-time": ExperienceType.PART_TIME,
            "parttime": ExperienceType.PART_TIME,
            "internship": ExperienceType.INTERNSHIP,
            "intern": ExperienceType.INTERNSHIP,
            "contract": ExperienceType.CONTRACT,
            "freelance": ExperienceType.FREELANCE,
            "volunteer": ExperienceType.VOLUNTEER,
            "other": ExperienceType.OTHER,
        }

        return mapping.get(
            normalized or "",
            ExperienceType.OTHER,
        )

    @classmethod
    def _education_level(cls, value: Any) -> EducationLevel:
        normalized = cls._enum_value(value)

        mapping = {
            "high_school": EducationLevel.HIGH_SCHOOL,
            "high-school": EducationLevel.HIGH_SCHOOL,
            "high school": EducationLevel.HIGH_SCHOOL,
            "school": EducationLevel.HIGH_SCHOOL,
            "diploma": EducationLevel.DIPLOMA,
            "bachelors": EducationLevel.BACHELORS,
            "bachelor": EducationLevel.BACHELORS,
            "b.tech": EducationLevel.BACHELORS,
            "btech": EducationLevel.BACHELORS,
            "b.e": EducationLevel.BACHELORS,
            "be": EducationLevel.BACHELORS,
            "undergraduate": EducationLevel.BACHELORS,
            "masters": EducationLevel.MASTERS,
            "master": EducationLevel.MASTERS,
            "m.tech": EducationLevel.MASTERS,
            "mtech": EducationLevel.MASTERS,
            "m.e": EducationLevel.MASTERS,
            "me": EducationLevel.MASTERS,
            "postgraduate": EducationLevel.MASTERS,
            "doctorate": EducationLevel.DOCTORATE,
            "phd": EducationLevel.DOCTORATE,
            "ph.d": EducationLevel.DOCTORATE,
            "other": EducationLevel.OTHER,
        }

        return mapping.get(
            normalized or "",
            EducationLevel.OTHER,
        )

    @classmethod
    def _metric_type(cls, value: Any) -> MetricType:
        normalized = cls._enum_value(value)

        mapping = {
            "percentage": MetricType.PERCENTAGE,
            "percent": MetricType.PERCENTAGE,
            "count": MetricType.COUNT,
            "currency": MetricType.CURRENCY,
            "money": MetricType.CURRENCY,
            "time": MetricType.TIME,
            "rating": MetricType.RATING,
            "scale": MetricType.SCALE,
            "other": MetricType.OTHER,
        }

        return mapping.get(
            normalized or "",
            MetricType.OTHER,
        )

    @classmethod
    def _achievement_type(cls, value: Any) -> AchievementType:
        normalized = cls._enum_value(value)

        mapping = {
            "award": AchievementType.AWARD,
            "competition": AchievementType.COMPETITION,
            "publication": AchievementType.PUBLICATION,
            "leadership": AchievementType.LEADERSHIP,
            "open_source": AchievementType.OPEN_SOURCE,
            "open-source": AchievementType.OPEN_SOURCE,
            "opensource": AchievementType.OPEN_SOURCE,
            "hackathon": AchievementType.HACKATHON,
            "academic": AchievementType.ACADEMIC,
            "recognition": AchievementType.RECOGNITION,
            "other": AchievementType.OTHER,
        }

        return mapping.get(
            normalized or "",
            AchievementType.OTHER,
        )

    # ================================================================
    # Timeline
    # ================================================================

    @classmethod
    def _preserve_date_value(cls, value: Any) -> str | None:
        """Preserve an existing date representation."""
        return cls._safe_string(value)

    @classmethod
    def _parse_timeline(
        cls,
        data: dict[str, Any],
    ) -> tuple[str | None, str | None]:
        """Extract start/end values from common analyzer shapes."""
        start_date = cls._preserve_date_value(
            data.get("start_date")
            or data.get("start")
            or data.get("from")
        )

        end_date = cls._preserve_date_value(
            data.get("end_date")
            or data.get("end")
            or data.get("to")
        )

        return start_date, end_date

    # ================================================================
    # Evidence
    # ================================================================

    @classmethod
    def _evidence_type(cls, value: Any) -> EvidenceType:
        normalized = cls._enum_value(value)

        mapping = {
            "declared": EvidenceType.DECLARED,
            "demonstrated": EvidenceType.DEMONSTRATED,
            "verified": EvidenceType.VERIFIED,
        }

        return mapping.get(
            normalized or "",
            EvidenceType.DECLARED,
        )

    @classmethod
    def _evidence_strength(cls, value: Any) -> EvidenceStrength:
        normalized = cls._enum_value(value)

        mapping = {
            "none": EvidenceStrength.NONE,
            "weak": EvidenceStrength.WEAK,
            "moderate": EvidenceStrength.MODERATE,
            "strong": EvidenceStrength.STRONG,
            "verified": EvidenceStrength.VERIFIED,
        }

        return mapping.get(
            normalized or "",
            EvidenceStrength.NONE,
        )

    @classmethod
    def _evidence_source(cls, value: Any) -> EvidenceSource:
        """
        Normalize an EvidenceSource.

        EvidenceSource intentionally has no SKILL member.
        """
        normalized = cls._enum_value(value)

        mapping = {
            "resume": EvidenceSource.RESUME,
            "skill_section": EvidenceSource.SKILL_SECTION,
            "project": EvidenceSource.PROJECT,
            "experience": EvidenceSource.EXPERIENCE,
            "internship": EvidenceSource.INTERNSHIP,
            "education": EvidenceSource.EDUCATION,
            "certification": EvidenceSource.CERTIFICATION,
            "achievement": EvidenceSource.ACHIEVEMENT,
        }

        return mapping.get(
            normalized or "",
            EvidenceSource.RESUME,
        )

    @classmethod
    def _build_evidence(
        cls,
        raw_evidence: Any,
        *,
        default_source: EvidenceSource = EvidenceSource.RESUME,
        default_type: EvidenceType = EvidenceType.DECLARED,
        default_strength: EvidenceStrength = EvidenceStrength.WEAK,
        default_entity_type: str = "resume",
        default_entity_id: str = "resume",
        default_confidence: float = 0.70,
    ) -> tuple[Evidence, ...]:
        """
        Convert analyzer evidence into validated Evidence objects.

        Strings use the supplied defaults.
        Dictionaries preserve their structured evidence values.
        Invalid entries are safely ignored.
        """
        if isinstance(raw_evidence, Evidence):
            return (raw_evidence,)

        result: list[Evidence] = []

        for item in cls._as_list(raw_evidence):
            if isinstance(item, Evidence):
                result.append(item)
                continue

            text: str | None = None
            entity_type = default_entity_type
            entity_id = default_entity_id
            evidence_type = default_type
            source = default_source
            strength = default_strength
            confidence = default_confidence
            location: str | None = None
            relationship: str | None = None

            if isinstance(item, str):
                text = cls._safe_string(item)

            elif isinstance(item, dict):
                text = cls._safe_string(
                    item.get("text")
                    or item.get("evidence")
                    or item.get("source_text")
                )

                entity_type = (
                    cls._safe_string(
                        item.get("entity_type")
                    )
                    or default_entity_type
                )

                entity_id = (
                    cls._safe_string(
                        item.get("entity_id")
                    )
                    or default_entity_id
                )

                if item.get("evidence_type") is not None:
                    evidence_type = cls._evidence_type(
                        item.get("evidence_type")
                    )

                if item.get("source") is not None:
                    source = cls._evidence_source(
                        item.get("source")
                    )

                if item.get("strength") is not None:
                    strength = cls._evidence_strength(
                        item.get("strength")
                    )

                if "confidence" in item:
                    confidence = cls._clamp_confidence(
                        item.get("confidence")
                    )

                location = cls._safe_string(
                    item.get("location")
                )

                relationship = cls._safe_string(
                    item.get("relationship")
                )

            else:
                continue

            if not text:
                continue

            if not entity_type:
                entity_type = default_entity_type

            if not entity_id:
                entity_id = default_entity_id

            try:
                result.append(
                    Evidence(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        evidence_type=evidence_type,
                        source=source,
                        text=text,
                        strength=strength,
                        confidence=confidence,
                        location=location,
                        relationship=relationship,
                    )
                )
            except (TypeError, ValueError):
                continue

        return cls._deduplicate_evidence(result)

    @staticmethod
    def _deduplicate_evidence(
        evidence: Iterable[Evidence],
    ) -> tuple[Evidence, ...]:
        """Deduplicate evidence while preserving order."""
        result: list[Evidence] = []
        seen: set[tuple[Any, ...]] = set()

        for item in evidence:
            if not isinstance(item, Evidence):
                continue

            key = (
                item.entity_type,
                item.entity_id,
                item.evidence_type,
                item.source,
                item.text,
                item.location,
                item.relationship,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return tuple(result)

    # ================================================================
    # Metrics
    # ================================================================

    @classmethod
    def _metric_strings(cls, value: Any) -> tuple[str, ...]:
        """Extract metric values as strings."""
        result: list[str] = []

        for item in cls._as_list(value):
            if isinstance(item, Metric):
                text = cls._safe_string(item.value)

            elif isinstance(item, dict):
                text = cls._safe_string(
                    item.get("value")
                    or item.get("metric")
                    or item.get("name")
                )

            else:
                text = cls._safe_string(item)

            if text:
                result.append(text)

        return cls._unique_strings(result)

    @classmethod
    def _build_metrics(
        cls,
        raw_metrics: Any,
    ) -> tuple[Metric, ...]:
        """Build CandidateProfile-level Metric objects."""
        result: list[Metric] = []

        for item in cls._as_list(raw_metrics):
            if isinstance(item, Metric):
                result.append(item)
                continue

            if isinstance(item, str):
                value = cls._safe_string(item)

                if not value:
                    continue

                try:
                    result.append(
                        Metric(
                            value=value,
                            metric_type=MetricType.OTHER,
                            confidence=0.70,
                        )
                    )
                except (TypeError, ValueError):
                    continue

                continue

            if not isinstance(item, dict):
                continue

            value = cls._safe_string(
                item.get("value")
                or item.get("metric")
                or item.get("name")
            )

            if not value:
                continue

            metric_type = cls._metric_type(
                item.get("metric_type")
            )

            description = cls._safe_string(
                item.get("description")
            )

            source_text = cls._safe_string(
                item.get("source_text")
                or item.get("evidence")
            )

            confidence = (
                cls._clamp_confidence(
                    item.get("confidence")
                )
                if "confidence" in item
                else 0.70
            )

            try:
                result.append(
                    Metric(
                        value=value,
                        metric_type=metric_type,
                        description=description,
                        source_text=source_text,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        unique: list[Metric] = []
        seen: set[tuple[str, str | None]] = set()

        for metric in result:
            key = (
                metric.value.casefold(),
                (
                    metric.source_text.casefold()
                    if metric.source_text
                    else None
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(metric)

        return tuple(unique)

    # ================================================================
    # Skills
    # ================================================================

    @classmethod
    def _build_skills(
        cls,
        analysis: Any,
    ) -> tuple[SkillProfile, ...]:
        """Build SkillProfile objects from skills analysis."""
        if not isinstance(analysis, dict):
            return ()

        result: list[SkillProfile] = []

        raw_details = analysis.get("skill_details")

        if raw_details is None:
            raw_details = []

        for item in cls._as_list(raw_details):
            if not isinstance(item, dict):
                continue

            canonical_name = cls._safe_string(
                item.get("canonical_name")
                or item.get("name")
                or item.get("skill")
            )

            if not canonical_name:
                continue

            # Bare string evidence is treated as:
            # - demonstrated
            # - resume sourced
            # - moderately strong
            # - 70% interpretation confidence
            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.RESUME,
                default_type=EvidenceType.DEMONSTRATED,
                default_strength=EvidenceStrength.MODERATE,
                default_entity_type="skill",
                default_entity_id=canonical_name,
            )

            # Current analyzer output contains:
            #   confidence       -> "Strong" / "Moderate" / "Weak"
            #   confidence_score -> numeric value such as 0.89 / 0.78
            #
            # Use confidence_score when it is available because it is
            # the actual numeric confidence value. Fall back to the
            # legacy confidence field for older analyzer output.
            if "confidence_score" in item:
                confidence = cls._clamp_confidence(
                    item.get("confidence_score")
                )
            else:
                confidence = cls._profile_item_confidence(item)

            strength = cls._evidence_strength(
                item.get("strength")
            )

            try:
                result.append(
                    SkillProfile(
                        canonical_name=canonical_name,
                        category=cls._skill_category(
                            item.get("category")
                        ),
                        evidence=evidence,
                        strength=strength,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        # ------------------------------------------------------------
        # Fallback skills_found
        # ------------------------------------------------------------

        existing = {
            skill.canonical_name.casefold()
            for skill in result
        }

        for raw_skill in cls._as_list(
            analysis.get("skills_found")
        ):
            if isinstance(raw_skill, dict):
                name = cls._safe_string(
                    raw_skill.get("canonical_name")
                    or raw_skill.get("name")
                    or raw_skill.get("skill")
                )
            else:
                name = cls._safe_string(raw_skill)

            if not name:
                continue

            if name.casefold() in existing:
                continue

            try:
                confidence = (
                    cls._profile_item_confidence(raw_skill)
                    if isinstance(raw_skill, dict)
                    else 0.70
                )

                result.append(
                    SkillProfile(
                        canonical_name=name,
                        category=SkillCategory.OTHER,
                        evidence=(),
                        strength=EvidenceStrength.NONE,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

            existing.add(name.casefold())

        # ------------------------------------------------------------
        # confidence_summary
        # ------------------------------------------------------------

        confidence_summary = analysis.get(
            "confidence_summary"
        )

        if isinstance(confidence_summary, dict):
            strong = {
                str(value).casefold()
                for value in cls._as_list(
                    confidence_summary.get("strong")
                )
            }

            moderate = {
                str(value).casefold()
                for value in cls._as_list(
                    confidence_summary.get("moderate")
                )
            }

            weak = {
                str(value).casefold()
                for value in cls._as_list(
                    confidence_summary.get("weak")
                )
            }

            updated: list[SkillProfile] = []

            for skill in result:
                key = skill.canonical_name.casefold()

                if skill.confidence > 0.0:
                    updated.append(skill)
                    continue

                if key in strong:
                    confidence = 0.90
                    strength = EvidenceStrength.STRONG
                elif key in moderate:
                    confidence = 0.70
                    strength = EvidenceStrength.MODERATE
                elif key in weak:
                    confidence = 0.40
                    strength = EvidenceStrength.WEAK
                else:
                    updated.append(skill)
                    continue

                try:
                    updated.append(
                        SkillProfile(
                            canonical_name=skill.canonical_name,
                            category=skill.category,
                            evidence=skill.evidence,
                            strength=strength,
                            confidence=confidence,
                        )
                    )
                except (TypeError, ValueError):
                    updated.append(skill)

            result = updated

        return tuple(result)

    # ================================================================
    # Projects
    # ================================================================

    @classmethod
    def _build_projects(
        cls,
        analysis: Any,
    ) -> tuple[ProjectProfile, ...]:
        """Build ProjectProfile objects."""
        result: list[ProjectProfile] = []

        for item in cls._as_list(analysis):
            if isinstance(item, ProjectProfile):
                result.append(item)
                continue

            if not isinstance(item, dict):
                continue

            title = cls._safe_string(
                item.get("title")
                or item.get("name")
                or item.get("project")
            )

            if not title:
                continue

            technologies = cls._unique_strings(
                item.get("technologies")
                or item.get("tech_stack")
                or item.get("tools")
            )

            actions = cls._unique_strings(
                item.get("actions")
                or item.get("action_verbs")
            )

            metrics = cls._metric_strings(
                item.get("metrics")
                or item.get("metrics_found")
            )

            deployment = cls._unique_strings(
                item.get("deployment")
                or item.get("deployment_features")
            )

            engineering = cls._unique_strings(
                item.get("engineering")
                or item.get("engineering_features")
            )

            strengths = cls._unique_strings(
                item.get("strengths")
            )

            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.PROJECT,
                default_type=EvidenceType.DEMONSTRATED,
                default_entity_type="project",
                default_entity_id=title,
            )

            score = cls._safe_score(
                item.get("score")
            )

            if item.get("quality") is not None:
                quality = cls._project_quality(
                    item.get("quality")
                )
            elif score >= 85:
                quality = ProjectQuality.EXCELLENT
            elif score >= 70:
                quality = ProjectQuality.GOOD
            elif score >= 50:
                quality = ProjectQuality.AVERAGE
            else:
                quality = ProjectQuality.BASIC

            confidence = cls._profile_item_confidence(item)

            try:
                result.append(
                    ProjectProfile(
                        title=title,
                        technologies=technologies,
                        actions=actions,
                        metrics=metrics,
                        deployment=deployment,
                        engineering=engineering,
                        strengths=strengths,
                        evidence=evidence,
                        score=score,
                        quality=quality,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        return tuple(result)

    # ================================================================
    # Experience
    # ================================================================

    @classmethod
    def _build_experience(
        cls,
        analysis: Any,
    ) -> tuple[ExperienceProfile, ...]:
        """Build ExperienceProfile objects."""
        result: list[ExperienceProfile] = []

        for item in cls._as_list(analysis):
            if isinstance(item, ExperienceProfile):
                result.append(item)
                continue

            if not isinstance(item, dict):
                continue

            title = cls._safe_string(
                item.get("title")
                or item.get("role")
                or item.get("position")
            )

            if not title:
                continue

            company = cls._safe_string(
                item.get("company")
                or item.get("organization")
            )

            start_date, end_date = cls._parse_timeline(item)

            duration_months = item.get(
                "duration_months"
            )

            if duration_months is not None:
                if isinstance(duration_months, bool):
                    duration_months = None
                else:
                    try:
                        duration_months = int(
                            duration_months
                        )

                        if duration_months < 0:
                            duration_months = None
                    except (TypeError, ValueError):
                        duration_months = None

            technologies = cls._unique_strings(
                item.get("technologies")
                or item.get("skills")
                or item.get("tools")
            )

            achievements = cls._unique_strings(
                item.get("achievements")
                or item.get("responsibilities")
            )

            metrics = cls._metric_strings(
                item.get("metrics")
                or item.get("metrics_found")
            )

            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.EXPERIENCE,
                default_type=EvidenceType.DEMONSTRATED,
                default_entity_type="experience",
                default_entity_id=title,
            )

            confidence = cls._profile_item_confidence(item)

            try:
                result.append(
                    ExperienceProfile(
                        title=title,
                        company=company,
                        experience_type=cls._experience_type(
                            item.get("experience_type")
                            or item.get("type")
                        ),
                        start_date=start_date,
                        end_date=end_date,
                        duration_months=duration_months,
                        is_current=cls._safe_bool(
                            item.get("is_current")
                        ),
                        technologies=technologies,
                        achievements=achievements,
                        metrics=metrics,
                        evidence=evidence,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        return tuple(result)

    # ================================================================
    # Education
    # ================================================================

    @classmethod
    def _build_education(
        cls,
        analysis: Any,
    ) -> tuple[EducationProfile, ...]:
        """Build all EducationProfile objects."""
        result: list[EducationProfile] = []

        for item in cls._as_list(analysis):
            if isinstance(item, EducationProfile):
                result.append(item)
                continue

            if not isinstance(item, dict):
                continue

            degree = cls._safe_string(
                item.get("degree")
                or item.get("qualification")
                or item.get("program")
            )

            if not degree:
                continue

            field_of_study = cls._safe_string(
                item.get("field_of_study")
                or item.get("field")
                or item.get("specialization")
            )

            institution = cls._safe_string(
                item.get("institution")
                or item.get("university")
                or item.get("college")
            )

            start_date, end_date = cls._parse_timeline(item)

            cgpa = item.get("cgpa")

            if cgpa is not None:
                try:
                    cgpa = float(cgpa)

                    if cgpa < 0:
                        cgpa = None
                except (TypeError, ValueError):
                    cgpa = None

            percentage = item.get("percentage")

            if percentage is not None:
                try:
                    percentage = float(percentage)

                    if percentage < 0 or percentage > 100:
                        percentage = None
                except (TypeError, ValueError):
                    percentage = None

            achievements = cls._unique_strings(
                item.get("achievements")
            )

            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.EDUCATION,
                default_type=EvidenceType.DECLARED,
                default_entity_type="education",
                default_entity_id=degree,
            )

            confidence = cls._profile_item_confidence(item)

            try:
                result.append(
                    EducationProfile(
                        degree=degree,
                        field_of_study=field_of_study,
                        institution=institution,
                        education_level=cls._education_level(
                            item.get("education_level")
                            or item.get("level")
                        ),
                        start_date=start_date,
                        end_date=end_date,
                        cgpa=cgpa,
                        percentage=percentage,
                        achievements=achievements,
                        evidence=evidence,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        return tuple(result)

    # ================================================================
    # Certifications
    # ================================================================

    @classmethod
    def _build_certifications(
        cls,
        analysis: Any,
    ) -> tuple[CertificationProfile, ...]:
        """Build CertificationProfile objects."""
        result: list[CertificationProfile] = []

        for item in cls._as_list(analysis):
            if isinstance(item, CertificationProfile):
                result.append(item)
                continue

            if not isinstance(item, dict):
                continue

            name = cls._safe_string(
                item.get("name")
                or item.get("title")
                or item.get("certification")
            )

            if not name:
                continue

            provider = cls._safe_string(
                item.get("provider")
                or item.get("issuer")
                or item.get("organization")
            )

            issue_date = cls._preserve_date_value(
                item.get("issue_date")
                or item.get("issued_date")
                or item.get("date")
            )

            expiry_date = cls._preserve_date_value(
                item.get("expiry_date")
                or item.get("expiration_date")
            )

            credential_id = cls._safe_string(
                item.get("credential_id")
                or item.get("credential")
            )

            credential_url = cls._safe_string(
                item.get("credential_url")
                or item.get("url")
            )

            skills = cls._unique_strings(
                item.get("skills")
            )

            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.CERTIFICATION,
                default_type=EvidenceType.VERIFIED,
                default_entity_type="certification",
                default_entity_id=name,
            )

            confidence = cls._profile_item_confidence(item)

            try:
                result.append(
                    CertificationProfile(
                        name=name,
                        provider=provider,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        credential_id=credential_id,
                        credential_url=credential_url,
                        skills=skills,
                        evidence=evidence,
                        confidence=confidence,
                        verified=cls._safe_bool(
                            item.get("verified")
                        ),
                    )
                )
            except (TypeError, ValueError):
                continue

        return tuple(result)

    # ================================================================
    # Achievements
    # ================================================================

    @classmethod
    def _build_achievements(
        cls,
        analysis: Any,
    ) -> tuple[AchievementProfile, ...]:
        """Build AchievementProfile objects."""
        result: list[AchievementProfile] = []

        for item in cls._as_list(analysis):
            if isinstance(item, AchievementProfile):
                result.append(item)
                continue

            if not isinstance(item, dict):
                continue

            title = cls._safe_string(
                item.get("title")
                or item.get("name")
                or item.get("achievement")
            )

            if not title:
                continue

            organization = cls._safe_string(
                item.get("organization")
                or item.get("issuer")
                or item.get("institution")
            )

            date = cls._preserve_date_value(
                item.get("date")
            )

            description = cls._safe_string(
                item.get("description")
            )

            metrics = cls._metric_strings(
                item.get("metrics")
                or item.get("metrics_found")
            )

            skills = cls._unique_strings(
                item.get("skills")
            )

            evidence = cls._build_evidence(
                item.get("evidence"),
                default_source=EvidenceSource.ACHIEVEMENT,
                default_type=EvidenceType.DEMONSTRATED,
                default_entity_type="achievement",
                default_entity_id=title,
            )

            confidence = cls._profile_item_confidence(item)

            try:
                result.append(
                    AchievementProfile(
                        title=title,
                        achievement_type=cls._achievement_type(
                            item.get("achievement_type")
                            or item.get("type")
                        ),
                        organization=organization,
                        date=date,
                        description=description,
                        metrics=metrics,
                        skills=skills,
                        evidence=evidence,
                        confidence=confidence,
                    )
                )
            except (TypeError, ValueError):
                continue

        return tuple(result)

    # ================================================================
    # Confidence
    # ================================================================

    @staticmethod
    def _profile_confidence(
        profiles: Iterable[Any],
    ) -> list[float]:
        """Extract valid confidence values from profile objects."""
        values: list[float] = []

        for profile in profiles:
            confidence = getattr(
                profile,
                "confidence",
                None,
            )

            if isinstance(
                confidence,
                (int, float),
            ) and not isinstance(
                confidence,
                bool,
            ):
                if 0.0 <= float(confidence) <= 1.0:
                    values.append(float(confidence))

        return values

    @classmethod
    def _overall_confidence(
        cls,
        *,
        skills: tuple[SkillProfile, ...],
        projects: tuple[ProjectProfile, ...],
        experience: tuple[ExperienceProfile, ...],
        education: tuple[EducationProfile, ...],
        certifications: tuple[CertificationProfile, ...],
        achievements: tuple[AchievementProfile, ...],
        metrics: tuple[Metric, ...],
    ) -> float:
        """Calculate confidence from populated profile objects."""
        values: list[float] = []

        for collection in (
            skills,
            projects,
            experience,
            education,
            certifications,
            achievements,
            metrics,
        ):
            values.extend(
                cls._profile_confidence(collection)
            )

        if not values:
            return 0.0

        return sum(values) / len(values)

    # ================================================================
    # Main builder
    # ================================================================

    def build(
        self,
        analysis: dict[str, Any],
        candidate_id: str,
    ) -> CandidateProfile:
        """
        Build a validated CandidateProfile.

        Raises:
            TypeError: If analysis is not a dictionary.
            ValueError: If candidate_id is empty.
        """
        if not isinstance(analysis, dict):
            raise TypeError(
                "analysis must be a dictionary"
            )

        normalized_candidate_id = self._safe_string(
            candidate_id
        )

        if not normalized_candidate_id:
            raise ValueError(
                "candidate_id must not be empty"
            )

        # ============================================================
        # Contact / metadata
        # ============================================================

        contact = analysis.get("contact")

        if not isinstance(contact, dict):
            contact = {}

        metadata = analysis.get("metadata")

        if not isinstance(metadata, dict):
            metadata = {}

        candidate_data = analysis.get("candidate")

        if not isinstance(candidate_data, dict):
            candidate_data = {}

        def get_contact_value(*keys: str) -> Any:
            """
            Contact object has highest priority.

            Priority:
                contact -> candidate -> metadata -> top-level
            """
            for key in keys:
                if key in contact:
                    return contact.get(key)

            for key in keys:
                if key in candidate_data:
                    return candidate_data.get(key)

            for key in keys:
                if key in metadata:
                    return metadata.get(key)

            for key in keys:
                if key in analysis:
                    return analysis.get(key)

            return None

        name = self._safe_string(
            get_contact_value(
                "name",
                "candidate_name",
            )
        )

        email = self._safe_string(
            get_contact_value(
                "email",
            )
        )

        phone = self._safe_string(
            get_contact_value(
                "phone",
                "mobile",
                "phone_number",
            )
        )

        linkedin = self._safe_string(
            get_contact_value(
                "linkedin",
                "linkedin_url",
            )
        )

        github = self._safe_string(
            get_contact_value(
                "github",
                "github_url",
            )
        )

        summary = self._safe_string(
            get_contact_value(
                "summary",
                "profile_summary",
                "professional_summary",
            )
        )

        # ============================================================
        # Analysis sections
        # ============================================================

        skills_analysis = analysis.get(
            "skills_analysis",
            {},
        )

        projects_analysis = analysis.get(
            "projects_analysis",
            [],
        )

        experience_analysis = analysis.get(
            "experience_analysis",
            [],
        )

        education_analysis = analysis.get(
            "education_analysis",
            [],
        )

        certifications_analysis = analysis.get(
            "certifications_analysis",
            [],
        )

        achievements_analysis = analysis.get(
            "achievements_analysis"
        )

        if achievements_analysis is None:
            achievements_analysis = analysis.get(
                "achievements",
                [],
            )

        skills = self._build_skills(
            skills_analysis
        )

        projects = self._build_projects(
            projects_analysis
        )

        experience = self._build_experience(
            experience_analysis
        )

        education = self._build_education(
            education_analysis
        )

        certifications = self._build_certifications(
            certifications_analysis
        )

        achievements = self._build_achievements(
            achievements_analysis
        )

        # ============================================================
        # Metrics
        # ============================================================

        raw_metrics = analysis.get("metrics")

        if raw_metrics is None:
            raw_metrics = analysis.get(
                "metrics_found"
            )

        if raw_metrics is None:
            ats_analysis = analysis.get(
                "ats_analysis"
            )

            if isinstance(ats_analysis, dict):
                raw_metrics = ats_analysis.get(
                    "metrics_found"
                )

        metrics = self._build_metrics(
            raw_metrics
        )

        # ============================================================
        # Candidate evidence
        # ============================================================

        candidate_evidence = self._build_evidence(
            analysis.get("evidence"),
            default_source=EvidenceSource.RESUME,
            default_type=EvidenceType.DECLARED,
            default_entity_type="resume",
            default_entity_id=normalized_candidate_id,
        )

        all_evidence: list[Evidence] = list(
            candidate_evidence
        )

        for collection in (
            skills,
            projects,
            experience,
            education,
            certifications,
            achievements,
        ):
            for profile in collection:
                all_evidence.extend(
                    getattr(
                        profile,
                        "evidence",
                        (),
                    )
                )

        candidate_evidence = self._deduplicate_evidence(
            all_evidence
        )

        # ============================================================
        # Overall confidence
        # ============================================================

        confidence = self._overall_confidence(
            skills=skills,
            projects=projects,
            experience=experience,
            education=education,
            certifications=certifications,
            achievements=achievements,
            metrics=metrics,
        )

        if confidence == 0.0:
            explicit_confidence = analysis.get(
                "candidate_profile_confidence"
            )

            if explicit_confidence is None:
                explicit_confidence = analysis.get(
                    "confidence"
                )

            confidence = self._clamp_confidence(
                explicit_confidence
            )

        # ============================================================
        # Final CandidateProfile
        # ============================================================

        return CandidateProfile(
            candidate_id=normalized_candidate_id,
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            summary=summary,
            skills=skills,
            projects=projects,
            experience=experience,
            education=education,
            certifications=certifications,
            achievements=achievements,
            metrics=metrics,
            evidence=candidate_evidence,
            confidence=confidence,
        )