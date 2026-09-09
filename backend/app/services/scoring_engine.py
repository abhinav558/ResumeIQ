"""
ResumeIQ - Production Scoring Engine

Responsible for:
- Final resume intelligence score
- Rating generation
- Improvement recommendations

Designed for fresher resumes.
"""

from __future__ import annotations


# ======================================================
# Score Weights
# ======================================================

WEIGHTS = {
    "skills": 0.20,
    "projects": 0.30,
    "experience": 0.10,
    "ats": 0.20,
    "certifications": 0.05,
    "education": 0.10,
    "achievements": 0.05,
}


MIN_SCORE = 0.0
MAX_SCORE = 100.0
EXPERIENCE_KEY = "experience"


# ======================================================
# Rating
# ======================================================

def generate_rating(score: float) -> str:
    """Convert a numeric score into a resume rating."""

    if score >= 90:
        return "Excellent"

    if score >= 75:
        return "Very Good"

    if score >= 60:
        return "Good"

    if score >= 45:
        return "Average"

    return "Needs Improvement"


# ======================================================
# Score Normalization
# ======================================================

def _normalize_score(value: float | int | None) -> float:
    """Normalize an individual component score to 0-100."""

    if value is None:
        return 0.0

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(
        MIN_SCORE,
        min(MAX_SCORE, numeric_value),
    )


# ======================================================
# Weight Validation
# ======================================================

def _validate_weights() -> None:
    """Validate configured scoring weights."""

    if not WEIGHTS:
        raise ValueError("WEIGHTS cannot be empty.")

    if any(weight < 0 for weight in WEIGHTS.values()):
        raise ValueError(
            "WEIGHTS cannot contain negative values."
        )

    total = sum(WEIGHTS.values())

    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"WEIGHTS must sum to 1.0, got {total}."
        )


# ======================================================
# Effective Weights
# ======================================================

def _get_effective_weights(
    experience_score: float,
) -> dict[str, float]:
    """
    Calculate effective weights for the resume.

    If professional experience exists, normal weights
    are used.

    If professional experience is absent, the experience
    weight is redistributed proportionally across all
    remaining categories.

    Experience itself remains 0 and is never fabricated.
    """

    experience_score = _normalize_score(
        experience_score
    )

    # Candidate has professional experience.
    if experience_score > 0:
        return WEIGHTS.copy()

    # Candidate has no professional experience.
    experience_weight = WEIGHTS[EXPERIENCE_KEY]

    applicable_weights = {
        key: weight
        for key, weight in WEIGHTS.items()
        if key != EXPERIENCE_KEY
    }

    applicable_total = sum(
        applicable_weights.values()
    )

    if applicable_total <= 0:
        raise ValueError(
            "Cannot redistribute experience weight."
        )

    effective_weights = {
        key: (
            weight
            + experience_weight
            * (weight / applicable_total)
        )
        for key, weight in applicable_weights.items()
    }

    # Do not fabricate experience.
    effective_weights[EXPERIENCE_KEY] = 0.0

    return effective_weights


# ======================================================
# Calculate Final Score
# ======================================================

def calculate_score(
    skills,
    projects,
    experience,
    ats,
    certifications,
    education,
    achievements,
):
    """
    Calculate the final ResumeIQ intelligence score.

    For freshers with no professional experience,
    the experience weight is redistributed rather than
    automatically reducing the maximum possible score.
    """

    _validate_weights()

    scores = {
        "skills": _normalize_score(skills),
        "projects": _normalize_score(projects),
        "experience": _normalize_score(experience),
        "ats": _normalize_score(ats),
        "certifications": _normalize_score(certifications),
        "education": _normalize_score(education),
        "achievements": _normalize_score(achievements),
    }

    # Preserve actual component scores.
    breakdown = {
        key: round(value, 2)
        for key, value in scores.items()
    }

    effective_weights = _get_effective_weights(
        scores["experience"]
    )

    final_score = sum(
        scores[key] * effective_weights[key]
        for key in scores
    )

    final_score = max(
        MIN_SCORE,
        min(MAX_SCORE, final_score),
    )

    final_score = round(
        final_score,
        2,
    )

    return {
        "resume_intelligence_score": final_score,
        "rating": generate_rating(final_score),
        "score_breakdown": breakdown,
    }


# ======================================================
# Recommendation Helpers
# ======================================================

def _clean_recommendation_items(
    values,
) -> list[str]:
    """
    Clean recommendation-related lists.

    Supports strings and dictionaries without making
    assumptions about engine-specific schemas.
    """

    if not values:
        return []

    if isinstance(values, str):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    cleaned: list[str] = []

    for value in values:
        if isinstance(value, str):
            item = value.strip()

        elif isinstance(value, dict):
            item = (
                value.get("name")
                or value.get("keyword")
                or value.get("skill")
                or value.get("title")
                or value.get("text")
                or ""
            )

            if not isinstance(item, str):
                item = str(item)

            item = item.strip()

        else:
            item = str(value).strip()

        if item:
            cleaned.append(item)

    return cleaned


def _deduplicate_recommendations(
    recommendations: list[str],
) -> list[str]:
    """Remove duplicate recommendations while preserving order."""

    seen: set[str] = set()
    result: list[str] = []

    for recommendation in recommendations:
        key = recommendation.casefold().strip()

        if not key or key in seen:
            continue

        seen.add(key)
        result.append(recommendation)

    return result


def _format_keyword_list(
    keywords: list[str],
    limit: int = 5,
) -> str:
    """Format missing keywords for a readable recommendation."""

    cleaned = _clean_recommendation_items(keywords)

    unique: list[str] = []
    seen: set[str] = set()

    for keyword in cleaned:
        key = keyword.casefold()

        if key in seen:
            continue

        seen.add(key)
        unique.append(keyword)

    unique = unique[:limit]

    if not unique:
        return ""

    if len(unique) == 1:
        return unique[0]

    if len(unique) == 2:
        return f"{unique[0]} and {unique[1]}"

    return (
        ", ".join(unique[:-1])
        + f", and {unique[-1]}"
    )


def _get_missing_ats_keywords(
    scores: dict,
) -> list[str]:
    """
    Extract missing ATS keywords from common ATS schemas.

    Supports both the analyzer's canonical fields and
    legacy scoring-engine inputs.
    """

    ats_data = scores.get("ats_analysis")

    if ats_data is None:
        ats_data = scores.get("ats_details")

    if ats_data is None:
        ats_data = scores.get("ats")

    if not isinstance(ats_data, dict):
        return []

    candidates = (
        ats_data.get("missing_keywords"),
        ats_data.get("missing"),
        ats_data.get("keywords_missing"),
        ats_data.get("missing_keywords_list"),
        ats_data.get("not_found_keywords"),
    )

    for candidate in candidates:
        cleaned = _clean_recommendation_items(candidate)

        if cleaned:
            return cleaned

    return []


def _get_matched_ats_keywords(
    scores: dict,
) -> list[str]:
    """Extract matched ATS keywords when available."""

    ats_data = scores.get("ats_analysis")

    if ats_data is None:
        ats_data = scores.get("ats_details")

    if ats_data is None:
        ats_data = scores.get("ats")

    if not isinstance(ats_data, dict):
        return []

    candidates = (
        ats_data.get("matched_keywords"),
        ats_data.get("matched"),
        ats_data.get("found_keywords"),
        ats_data.get("keywords_found"),
    )

    for candidate in candidates:
        cleaned = _clean_recommendation_items(candidate)

        if cleaned:
            return cleaned

    return []


def _get_project_metrics(
    scores: dict,
) -> list:
    """Extract project metrics from project-analysis context."""

    project_data = scores.get("project_analysis")

    if project_data is None:
        project_data = scores.get("projects_analysis")

    if project_data is None:
        project_data = scores.get("projects_details")

    if not isinstance(project_data, dict):
        return []

    projects = (
        project_data.get("projects")
        or project_data.get("items")
        or project_data.get("entries")
        or []
    )

    if not isinstance(projects, list):
        return []

    metrics_found = []

    for project in projects:
        if not isinstance(project, dict):
            continue

        metrics = (
            project.get("metrics")
            or project.get("outcomes")
            or project.get("measurements")
            or []
        )

        if metrics:
            metrics_found.extend(
                _clean_recommendation_items(metrics)
            )

    return metrics_found


def _has_deployment_evidence(
    scores: dict,
) -> bool:
    """Determine whether project deployment evidence exists."""

    project_data = scores.get("project_analysis")

    if project_data is None:
        project_data = scores.get("projects_analysis")

    if not isinstance(project_data, dict):
        return False

    projects = (
        project_data.get("projects")
        or project_data.get("items")
        or project_data.get("entries")
        or []
    )

    if not isinstance(projects, list):
        return False

    deployment_terms = {
        "deployment",
        "deployed",
        "hosting",
        "hosted",
        "api",
        "flask",
        "fastapi",
        "streamlit",
        "docker",
        "aws",
        "azure",
        "gcp",
    }

    for project in projects:
        if not isinstance(project, dict):
            continue

        deployment = project.get("deployment")

        if isinstance(deployment, str):
            if deployment.strip():
                return True

        elif isinstance(deployment, (list, tuple, set)):
            if deployment:
                return True

        text_parts = [
            project.get("technologies"),
            project.get("technology"),
            project.get("engineering"),
            project.get("tools"),
        ]

        for part in text_parts:
            for item in _clean_recommendation_items(part):
                if item.casefold() in deployment_terms:
                    return True

    return False


def _has_experience_evidence(
    scores: dict,
) -> bool:
    """Check for actual experience/internship evidence."""

    experience_data = scores.get("experience_analysis")

    if experience_data is None:
        experience_data = scores.get("experience_details")

    if isinstance(experience_data, dict):
        entries = (
            experience_data.get("experience")
            or experience_data.get("entries")
            or experience_data.get("items")
            or []
        )

        if isinstance(entries, list) and entries:
            return True

        if experience_data.get("experience_found") is True:
            return True

    experience = scores.get("experience")

    if isinstance(experience, (list, tuple, set)):
        return bool(experience)

    if isinstance(experience, dict):
        return bool(experience)

    return _normalize_score(experience) > 0


def _has_achievements_evidence(
    scores: dict,
) -> bool:
    """Check for actual achievement evidence."""

    achievement_data = scores.get("achievement_analysis")

    if achievement_data is None:
        achievement_data = scores.get("achievements_analysis")

    if isinstance(achievement_data, dict):
        entries = (
            achievement_data.get("achievements")
            or achievement_data.get("entries")
            or achievement_data.get("items")
            or []
        )

        if isinstance(entries, list) and entries:
            return True

        if achievement_data.get("achievements_found") is True:
            return True

    achievements = scores.get("achievements")

    if isinstance(achievements, (list, tuple, set)):
        return bool(achievements)

    if isinstance(achievements, dict):
        return bool(achievements)

    return _normalize_score(achievements) > 0


# ======================================================
# Recommendations
# ======================================================

def generate_recommendations(
    scores: dict,
) -> list[str]:
    """
    Generate actionable, context-aware resume recommendations.

    The function accepts the original compact score dictionary,
    but also understands richer analyzer output when available.

    Recommendations never invent experience, metrics, skills,
    certifications, or achievements.
    """

    if not isinstance(scores, dict):
        scores = {}

    recommendations: list[str] = []

    # --------------------------------------------------
    # Extract component scores
    # --------------------------------------------------

    project_score = _normalize_score(
        scores.get("projects", 0)
    )

    skill_score = _normalize_score(
        scores.get("skills", 0)
    )

    ats_score = _normalize_score(
        scores.get("ats", 0)
    )

    experience_score = _normalize_score(
        scores.get("experience", 0)
    )

    achievement_score = _normalize_score(
        scores.get("achievements", 0)
    )

    # --------------------------------------------------
    # 1. ATS / Missing Keywords
    # --------------------------------------------------

    missing_keywords = _get_missing_ats_keywords(
        scores
    )

    if ats_score < 70:
        if missing_keywords:
            formatted_keywords = _format_keyword_list(
                missing_keywords,
                limit=6,
            )

            recommendations.append(
                "Improve ATS alignment by adding relevant "
                f"target-job keywords such as {formatted_keywords} "
                "when they genuinely match your skills or experience"
            )
        else:
            recommendations.append(
                "Improve ATS optimization by tailoring "
                "technical keywords to each target job description"
            )

    elif missing_keywords:
        formatted_keywords = _format_keyword_list(
            missing_keywords,
            limit=5,
        )

        if formatted_keywords:
            recommendations.append(
                "Consider adding relevant missing ATS keywords "
                f"such as {formatted_keywords} when they accurately "
                "represent your skills or project experience"
            )

    # --------------------------------------------------
    # 2. Projects
    # --------------------------------------------------

    project_metrics = _get_project_metrics(
        scores
    )

    if project_score < 70:
        if not project_metrics:
            recommendations.append(
                "Strengthen project descriptions by adding "
                "measurable outcomes such as accuracy, users, "
                "performance improvements, dataset size, or "
                "response time where those values are actually available"
            )

        if not _has_deployment_evidence(scores):
            recommendations.append(
                "Strengthen projects with real deployment or "
                "engineering evidence such as an API, cloud deployment, "
                "containerization, CI/CD, or production-style testing "
                "when applicable"
            )

    # --------------------------------------------------
    # 3. Skills
    # --------------------------------------------------

    if skill_score < 70:
        recommendations.append(
            "Improve technical-skill alignment by prioritizing "
            "skills directly relevant to your target software or "
            "AI/ML roles instead of listing unrelated technologies"
        )

    # --------------------------------------------------
    # 4. Experience / Internship
    # --------------------------------------------------

    has_experience = _has_experience_evidence(
        scores
    )

    if experience_score < 50 and not has_experience:
        recommendations.append(
            "Add genuine internship, freelance, open-source, "
            "or relevant practical experience if available, "
            "with 2-3 impact-focused bullet points for each role"
        )

    # --------------------------------------------------
    # 5. Achievements
    # --------------------------------------------------

    has_achievements = _has_achievements_evidence(
        scores
    )

    if achievement_score < 50 and not has_achievements:
        recommendations.append(
            "Add relevant achievements such as coding-contest "
            "results, hackathons, awards, leadership, publications, "
            "or other verifiable accomplishments with measurable outcomes"
        )

    # --------------------------------------------------
    # 6. Strong ATS score but project weakness
    # --------------------------------------------------

    if (
        ats_score >= 70
        and project_score < 60
    ):
        recommendations.append(
            "Your ATS alignment is relatively stronger than your "
            "project evidence; prioritize deeper project impact, "
            "implementation details, and measurable results"
        )

    # --------------------------------------------------
    # 7. Strong skills but weak ATS
    # --------------------------------------------------

    if (
        skill_score >= 70
        and ats_score < 70
    ):
        recommendations.append(
            "Your technical-skill coverage is stronger than your ATS "
            "score; tailor the wording of your skills and project bullets "
            "to the terminology used in your target job descriptions"
        )

    # --------------------------------------------------
    # 8. Fresher-specific project strategy
    # --------------------------------------------------

    if (
        experience_score == 0
        and project_score < 70
    ):
        recommendations.append(
            "As a fresher, use your projects as your primary evidence "
            "of engineering ability by clearly showing your role, "
            "technical decisions, implementation, and outcomes"
        )

    # --------------------------------------------------
    # 9. Fallback
    # --------------------------------------------------

    recommendations = _deduplicate_recommendations(
        recommendations
    )

    if not recommendations:
        recommendations.append(
            "Resume is well optimized"
        )

    return recommendations