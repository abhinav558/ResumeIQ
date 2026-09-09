"""
ResumeIQ - Production Job Matcher

Compares resume text against a job description and produces
structured job-match intelligence.

Design goals
------------

- Deterministic scoring
- Alias-safe skill matching
- C++ / C# safe normalization
- Singular/plural-safe matching
- Canonical requirement matching
- Evidence-aware requirement matching
- Weighted requirements
- Requirement priorities
- Category coverage
- Experience-aware matching
- Honest uncertainty handling
- Actionable recommendations
- Backward-compatible response structure
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from .job.requirement_engine import (
    Requirement,
    build_requirements,
    calculate_experience_gap,
    calculate_technical_experience_gaps,
    calculate_weighted_match,
    extract_experience_requirements,
    get_requirement_priority_counts,
    get_requirement_weights,
    normalize_skill,
    split_requirements,
    _canonical_requirement,
)


# ============================================================
# MATCH THRESHOLDS
# ============================================================

EXCELLENT_MATCH_THRESHOLD = 85
STRONG_MATCH_THRESHOLD = 70
MODERATE_MATCH_THRESHOLD = 50

HIGH_READINESS_THRESHOLD = 75
MODERATE_READINESS_THRESHOLD = 55


# ============================================================
# CATEGORY WEIGHTS
# ============================================================

CATEGORY_WEIGHTS = {
    "Programming": 1.0,
    "Backend": 1.0,
    "Frontend": 0.9,
    "Database": 1.0,
    "DevOps": 0.9,
    "Cloud": 0.9,
    "AI/ML": 1.0,
    "Engineering": 0.9,
    "Networking": 1.0,
    "Tools": 0.7,
    "Blockchain": 0.8,
    "Other": 0.5,
}


# ============================================================
# TEXT UTILITIES
# ============================================================

def _safe_text(value: Any) -> str:
    """
    Convert arbitrary input into safe text.
    """
    if value is None:
        return ""

    return str(value).strip()


def _normalize_text(value: Any) -> str:
    """
    Normalize text for deterministic matching.

    Keeps technical punctuation such as:

        C++
        C#
        CI/CD
        Node.js
        .NET

    while normalizing whitespace and common dash variants.
    """
    text = _safe_text(value).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("\u2011", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SKILL ALIASES
# ============================================================

# These aliases represent the same skill or a safe textual
# representation of the same skill.
#
# IMPORTANT:
# Do not put merely "related" technologies here.
#
# Examples:
#   FastAPI != Flask
#   AWS != Azure
#   Docker != Kubernetes
#   SQL != PostgreSQL
#
# Conceptual relationships such as:
#
#   Git -> version control
#   REST API -> API
#
# are intentionally NOT represented as ordinary aliases.
# They are handled separately below.

_SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "c++": (
        "c++",
        "c plus plus",
        "cpp",
    ),
    "c#": (
        "c#",
        "c sharp",
        "c-sharp",
    ),
    "nodejs": (
        "nodejs",
        "node.js",
        "node js",
    ),
    "react": (
        "react",
        "react.js",
        "react js",
    ),
    "nextjs": (
        "nextjs",
        "next.js",
        "next js",
    ),
    "ci/cd": (
        "ci/cd",
        "ci cd",
        "ci-cd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
    ),
    "rest api": (
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
    ),
    "api": (
        "api",
        "apis",
    ),
    "orm": (
        "orm",
        "object relational mapping",
        "object-relational mapping",
    ),
    "machine learning": (
        "machine learning",
        "machine-learning",
    ),
    "deep learning": (
        "deep learning",
        "deep-learning",
    ),
    "neural network": (
        "neural network",
        "neural networks",
        "neural-network",
        "neural-networks",
    ),
    "neural networks": (
        "neural network",
        "neural networks",
        "neural-network",
        "neural-networks",
    ),
    "computer vision": (
        "computer vision",
        "computer-vision",
    ),
    "artificial intelligence": (
        "artificial intelligence",
        "artificial-intelligence",
    ),
    "ai": (
        "ai",
        "a.i.",
        "artificial intelligence",
    ),
    "ml": (
        "ml",
        "m.l.",
        "machine learning",
    ),
    "tensorflow": (
        "tensorflow",
        "tensorflow.js",
        "tensorflow js",
    ),
    "scikit-learn": (
        "scikit-learn",
        "scikit learn",
        "sklearn",
    ),
    "github": (
        "github",
        "github.com",
    ),
    "git": (
        "git",
    ),
    "postgresql": (
        "postgresql",
        "postgres",
        "postgres db",
        "postgres database",
    ),
    "mongodb": (
        "mongodb",
        "mongo db",
        "mongo",
    ),
    "mysql": (
        "mysql",
        "my sql",
    ),
    "visual studio code": (
        "visual studio code",
        "visual studio",
        "vs code",
        "vscode",
    ),
    "aws": (
        "aws",
        "amazon web services",
    ),
    "gcp": (
        "gcp",
        "google cloud",
        "google cloud platform",
    ),
    "azure": (
        "azure",
        "microsoft azure",
    ),
    "kubernetes": (
        "kubernetes",
        "k8s",
    ),
    "docker": (
        "docker",
    ),
    "fastapi": (
        "fastapi",
        "fast api",
    ),
    "flask": (
        "flask",
    ),
}


# ============================================================
# EVIDENCE RELATIONSHIPS
# ============================================================

# These are NOT aliases.
#
# They describe one-way evidence relationships.
#
# Example:
#   Git is evidence of version control.
#
# But:
#   version control is NOT evidence of Git.
#
# Likewise:
#   REST API is evidence of API.
#
# But:
#   API is NOT evidence of REST API.
#
# Concrete databases are evidence of the generic database
# concept, but generic database is not evidence of a specific
# database technology.

_EVIDENCE_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "version control": (
        "git",
    ),
    "api": (
        "rest api",
    ),
    "database": (
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
    ),
}


# ============================================================
# GENERIC / NON-SKILL REQUIREMENTS
# ============================================================

# These phrases are often extracted from broad prose even
# though they are not useful standalone skill requirements.
#
# They should not become critical missing skills merely because
# the JD contains language such as "software development".
#
# Concrete requirements such as:
#   testing
#   debugging
#   code review
#   deployment
#
# remain valid requirements.

_GENERIC_REQUIREMENT_SKILLS = {
    "software development",
    "software engineering",
    "technical implementation",
    "practical software applications",
    "engineering environment",
    "technical skills",
    "technical knowledge",
    "programming skills",
}


# ============================================================
# MATCH CANONICALIZATION
# ============================================================

def _canonical_match_key(skill: str) -> str:
    """
    Return the canonical matching family for a skill.

    Important distinction:

    This function canonicalizes true equivalents only.

    Examples:

        neural network -> neural network
        neural networks -> neural network

        AI -> artificial intelligence
        artificial intelligence -> artificial intelligence

        ML -> machine learning
        machine learning -> machine learning

    Git remains Git.

    GitHub remains GitHub.

    Version control remains version control.

    This is intentional.

    Git -> version control is an evidence relationship, not
    an alias.

    Keeping the original skill intact prevents the resume
    skill profile from incorrectly displaying "version control"
    instead of "Git".
    """
    normalized = normalize_skill(skill)

    if not normalized:
        return ""

    normalized = _normalize_text(normalized)

    explicit_families = {
        "neural network": "neural network",
        "neural networks": "neural network",
        "artificial intelligence": "artificial intelligence",
        "ai": "artificial intelligence",
        "machine learning": "machine learning",
        "ml": "machine learning",
    }

    if normalized in explicit_families:
        return explicit_families[normalized]

    return _canonical_requirement(normalized)


# ============================================================
# SAFE TOKEN / PHRASE MATCHING
# ============================================================

def _candidate_variants(skill: str) -> tuple[str, ...]:
    """
    Return deterministic textual variants for a skill.

    The canonical skill is always included.
    """
    normalized = normalize_skill(skill)

    if not normalized:
        return ()

    aliases = _SKILL_ALIASES.get(normalized)

    if aliases:
        return tuple(
            dict.fromkeys(
                _normalize_text(alias)
                for alias in aliases
                if _normalize_text(alias)
            )
        )

    return (normalized,)


def _phrase_matches(
    phrase: str,
    text: str,
) -> bool:
    """
    Match a phrase safely against normalized text.

    Handles punctuation-heavy identifiers while avoiding
    accidental substring matches.

    Examples:

        git matches "git"

        git does not match "github"

        ai matches "AI"

        ai does not match "mail"

        c++ matches "C++"

        c# matches "C#"
    """
    phrase = _normalize_text(phrase)
    text = _normalize_text(text)

    if not phrase or not text:
        return False

    escaped = re.escape(phrase)

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{escaped}"
        rf"(?![a-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )


def _plural_safe_match(
    skill: str,
    text: str,
) -> bool:
    """
    Match simple singular/plural technical phrases safely.

    This primarily handles cases such as:

        neural network
        neural networks

    without applying aggressive stemming.
    """
    normalized_skill = normalize_skill(skill)

    if not normalized_skill:
        return False

    variants = list(
        _candidate_variants(normalized_skill)
    )

    words = normalized_skill.split()

    if words:
        last = words[-1]

        if (
            len(last) > 2
            and last.isalpha()
            and not last.endswith("s")
        ):
            plural_last = last + "s"

            plural_phrase = " ".join(
                words[:-1] + [plural_last]
            )

            variants.append(plural_phrase)

    for variant in dict.fromkeys(variants):
        if _phrase_matches(
            variant,
            text,
        ):
            return True

    return False


# ============================================================
# SKILL OCCURRENCE MATCHING
# ============================================================

def _skill_in_text(
    skill: str,
    text: str,
) -> bool:
    """
    Safely determine whether a skill appears in text.

    Matching is:

        1. alias-aware
        2. punctuation-safe
        3. conservative plural-safe

    It deliberately does NOT perform broad semantic matching.

    Therefore:

        Flask != FastAPI
        AWS != Azure
        Docker != Kubernetes
        SQL != PostgreSQL
        database != PostgreSQL

    while:

        neural network == neural networks
        sklearn == scikit-learn
        k8s == kubernetes
        node.js == nodejs
    """
    normalized_skill = normalize_skill(skill)

    if not normalized_skill:
        return False

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return False

    return _plural_safe_match(
        normalized_skill,
        normalized_text,
    )


# ============================================================
# CANONICAL SKILL MATCHING
# ============================================================

def _canonical_skill_set(
    skills: Iterable[str],
) -> set[str]:
    """
    Convert skills into a normalized canonical set.

    Only true equivalents are collapsed.

    Git, GitHub and version control remain distinct here so
    that evidence relationships can be evaluated explicitly.
    """
    result: set[str] = set()

    for skill in skills:
        canonical = _canonical_match_key(skill)

        if canonical:
            result.add(canonical)

    return result


def _has_direct_or_related_evidence(
    requirement_skill: str,
    detected_skills: Iterable[str],
) -> bool:
    """
    Determine whether detected skills provide direct or
    explicitly permitted one-way evidence for a requirement.

    Examples:

        Git -> version control       True
        REST API -> API              True
        API -> REST API              False
        version control -> Git       False
        database -> PostgreSQL       False
        SQL -> PostgreSQL             False

    Only explicitly declared relationships are accepted.
    """
    requirement = _canonical_match_key(
        requirement_skill
    )

    if not requirement:
        return False

    detected = _canonical_skill_set(
        detected_skills
    )

    # Direct equivalent.
    if requirement in detected:
        return True

    evidence_sources = _EVIDENCE_RELATIONSHIPS.get(
        requirement,
        (),
    )

    if not evidence_sources:
        return False

    evidence_canonicals = {
        _canonical_match_key(source)
        for source in evidence_sources
    }

    return bool(
        evidence_canonicals.intersection(
            detected
        )
    )


def _skill_equivalent(
    requirement_skill: str,
    detected_skills: Iterable[str],
) -> bool:
    """
    Determine whether a requirement is represented by
    already-detected resume skills.

    Supported one-way evidence:

        Git -> version control
        REST API -> API
        SQL -> database
        MySQL -> database
        PostgreSQL -> database
        MongoDB -> database

    It does NOT support reverse or overly broad equivalence:

        version control -> Git      False
        API -> REST API             False
        database -> PostgreSQL      False
        SQL -> PostgreSQL           False
        Flask -> FastAPI            False
        AWS -> Azure                False
    """
    return _has_direct_or_related_evidence(
        requirement_skill,
        detected_skills,
    )


# ============================================================
# REQUIREMENT DEDUPLICATION / CLEANUP
# ============================================================

def _normalize_priority(value: Any) -> str:
    """
    Normalize requirement priority values.

    Supports values such as:

        must_have
        must have
        Must Have
        preferred
        Preferred
        supporting
        Supporting
    """
    text = _safe_text(value).lower()

    text = re.sub(
        r"[\s\-]+",
        "_",
        text,
    )

    return text


def _requirement_strength(
    requirement: Requirement,
) -> tuple[int, int]:
    """
    Return a deterministic strength ranking.

    Stronger priorities are preserved when two extracted
    requirements represent the same conceptual requirement.
    """
    priority_rank = {
        "must_have": 3,
        "preferred": 2,
        "supporting": 1,
    }

    priority = _normalize_priority(
        getattr(
            requirement,
            "priority",
            "",
        )
    )

    try:
        weight = int(
            getattr(
                requirement,
                "weight",
                0,
            )
            or 0
        )
    except (TypeError, ValueError):
        weight = 0

    return (
        priority_rank.get(
            priority,
            0,
        ),
        weight,
    )


def _clean_requirements(
    requirements: Iterable[Requirement],
) -> list[Requirement]:
    """
    Clean and deduplicate extracted job requirements.

    Examples:

        neural network
        neural networks

    become one requirement.

        AI
        artificial intelligence

    become one requirement.

        ML
        machine learning

    become one requirement.

    Distinct requirements remain distinct:

        Git
        GitHub
        version control

        API
        REST API

        database
        SQL
        PostgreSQL
        MongoDB

        Flask
        FastAPI

        AWS
        Azure
        GCP

    Generic prose such as "software development" is removed
    when it appears only as a broad standalone requirement.

    The strongest priority/weight is retained when duplicate
    conceptual requirements occur.
    """
    selected: dict[str, Requirement] = {}
    order: list[str] = []

    for requirement in requirements:
        skill = _safe_text(
            getattr(
                requirement,
                "skill",
                "",
            )
        )

        if not skill:
            continue

        canonical = _canonical_match_key(
            skill
        )

        if not canonical:
            continue

        if canonical in _GENERIC_REQUIREMENT_SKILLS:
            continue

        existing = selected.get(canonical)

        if existing is None:
            selected[canonical] = requirement
            order.append(canonical)
            continue

        if _requirement_strength(
            requirement
        ) > _requirement_strength(
            existing
        ):
            selected[canonical] = requirement

    return [
        selected[canonical]
        for canonical in order
    ]


# ============================================================
# SKILL MATCHING
# ============================================================

def _match_requirements(
    resume_text: str,
    requirements: list[Requirement],
) -> tuple[
    list[str],
    list[str],
    list[dict],
]:
    """
    Determine matched and missing requirements.

    Matching uses both:

        - direct resume text evidence
        - known resume skill evidence
        - explicit one-way evidence relationships

    Requirement results contain one entry per cleaned
    conceptual requirement.
    """
    matched_skills: list[str] = []
    missing_skills: list[str] = []

    requirement_results: list[dict] = []

    seen_matched: set[str] = set()
    seen_missing: set[str] = set()

    resume_skills = _extract_resume_skills(
        resume_text
    )

    for requirement in requirements:
        skill = requirement.skill

        matched_from_text = _skill_in_text(
            skill,
            resume_text,
        )

        matched_from_skills = _skill_equivalent(
            skill,
            resume_skills,
        )

        matched = (
            matched_from_text
            or matched_from_skills
        )

        result = {
            "skill": skill,
            "priority": requirement.priority,
            "weight": requirement.weight,
            "category": requirement.category,
            "matched": matched,
        }

        requirement_results.append(
            result
        )

        canonical_skill = _canonical_match_key(
            skill
        )

        if not canonical_skill:
            continue

        if matched:
            if canonical_skill not in seen_matched:
                matched_skills.append(
                    canonical_skill
                )
                seen_matched.add(
                    canonical_skill
                )
        else:
            if canonical_skill not in seen_missing:
                missing_skills.append(
                    canonical_skill
                )
                seen_missing.add(
                    canonical_skill
                )

    return (
        matched_skills,
        missing_skills,
        requirement_results,
    )


# ============================================================
# RESUME SKILL EXTRACTION
# ============================================================

def _extract_resume_skills(
    resume_text: str,
) -> list[str]:
    """
    Extract known skills from the resume text using the
    requirement database.

    This remains intentionally conservative.

    A skill is returned only when it has explicit textual
    evidence in the resume.

    Original concrete skills are preserved where possible.

    Examples:

        Git -> Git
        GitHub -> GitHub
        Visual Studio Code -> Visual Studio Code

    True equivalents such as:

        AI / artificial intelligence
        ML / machine learning
        neural network / neural networks

    are collapsed into one canonical family.
    """
    from .keyword_db import (
        ALL_TECHNOLOGIES,
        ENGINEERING,
        NETWORKING,
    )

    candidates = (
        list(ALL_TECHNOLOGIES)
        + list(ENGINEERING)
        + list(NETWORKING)
    )

    normalized_candidates = sorted(
        {
            _canonical_requirement(skill)
            for skill in candidates
            if skill
        },
        key=len,
        reverse=True,
    )

    detected: list[str] = []
    seen: set[str] = set()

    for skill in normalized_candidates:
        if not skill:
            continue

        if not _skill_in_text(
            skill,
            resume_text,
        ):
            continue

        canonical = _canonical_match_key(
            skill
        )

        if not canonical:
            continue

        # Only collapse genuine equivalents.
        #
        # Do NOT collapse:
        #
        #   Git + GitHub -> version control
        #
        # because the resume skill profile should retain the
        # concrete technologies.
        if canonical not in seen:
            detected.append(
                canonical
            )
            seen.add(
                canonical
            )

    return detected


# ============================================================
# BACKWARD-COMPATIBILITY HELPERS
# ============================================================

def extract_keywords(
    text: str,
) -> list[str]:
    """
    Backward-compatible public wrapper.

    Historically, ResumeIQ exposed extract_keywords().
    """
    return _extract_resume_skills(
        _safe_text(text)
    )


def categorize_keywords(
    keywords: Iterable[str],
) -> dict[str, list[str]]:
    """
    Backward-compatible public wrapper.

    Historically, ResumeIQ exposed categorize_keywords().
    """
    return _categorize_skills(
        keywords
    )


# ============================================================
# JOB SKILL EXTRACTION
# ============================================================

def _extract_job_skills(
    job_description: str,
) -> list[str]:
    """
    Extract known skills from the job description.

    Only skills explicitly represented in the keyword database
    are considered.
    """
    from .keyword_db import (
        ALL_TECHNOLOGIES,
        ENGINEERING,
        NETWORKING,
    )

    candidates = (
        list(ALL_TECHNOLOGIES)
        + list(ENGINEERING)
        + list(NETWORKING)
    )

    detected: list[str] = []
    seen: set[str] = set()

    for skill in sorted(
        candidates,
        key=len,
        reverse=True,
    ):
        if not skill:
            continue

        canonical = _canonical_requirement(
            skill
        )

        if not canonical:
            continue

        if canonical in seen:
            continue

        if _skill_in_text(
            canonical,
            job_description,
        ):
            detected.append(
                canonical
            )
            seen.add(
                canonical
            )

    return detected


# ============================================================
# CATEGORY BUILDING
# ============================================================

def _categorize_skills(
    skills: Iterable[str],
) -> dict[str, list[str]]:
    """
    Categorize skills using the keyword database.

    Concrete resume skills are preserved.

    Conceptual matching is handled elsewhere.
    """
    from .keyword_db import (
        CATEGORY_MAP,
        ENGINEERING,
        NETWORKING,
    )

    categories: dict[str, list[str]] = {}

    engineering = {
        _canonical_match_key(skill)
        for skill in ENGINEERING
        if skill
    }

    networking = {
        _canonical_match_key(skill)
        for skill in NETWORKING
        if skill
    }

    normalized_category_map = {
        category_name: {
            _canonical_match_key(item)
            for item in category_skills
            if item
        }
        for category_name, category_skills
        in CATEGORY_MAP.items()
    }

    for raw_skill in skills:
        skill = _canonical_match_key(
            raw_skill
        )

        if not skill:
            continue

        category = None

        for (
            category_name,
            category_skills,
        ) in normalized_category_map.items():
            if skill in category_skills:
                category = category_name
                break

        if (
            category is None
            and skill in networking
        ):
            category = "Networking"
        elif (
            category is None
            and skill in engineering
        ):
            category = "Engineering"

        if category is None:
            category = "Other"

        categories.setdefault(
            category,
            [],
        )

        if skill not in categories[category]:
            categories[category].append(
                skill
            )

    return categories


# ============================================================
# CATEGORY COVERAGE
# ============================================================

def _calculate_category_coverage(
    resume_categories: dict[str, list[str]],
    job_categories: dict[str, list[str]],
) -> dict[str, int]:
    """
    Calculate category-level coverage.

    Only categories actually requested by the job
    are included.

    Matching follows the same evidence rules as requirement
    matching rather than broad category similarity.
    """
    coverage: dict[str, int] = {}

    resume_all_skills = [
        skill
        for skills in resume_categories.values()
        for skill in skills
    ]

    for category, job_skills in job_categories.items():
        if not job_skills:
            coverage[category] = 0
            continue

        matched = 0

        for skill in job_skills:
            if _skill_equivalent(
                skill,
                resume_all_skills,
            ):
                matched += 1

        coverage[category] = round(
            (
                matched
                / len(job_skills)
            )
            * 100
        )

    return coverage


# ============================================================
# EXPERIENCE HELPERS
# ============================================================

def _estimate_resume_experience_years(
    resume_text: str,
) -> float | None:
    """
    Conservatively estimate overall resume experience.

    Returns None when there is no reliable explicit evidence.

    We deliberately do not infer experience from:

        - graduation dates
        - project duration
        - vague wording
        - number of projects
    """
    if not resume_text:
        return None

    text = _normalize_text(
        resume_text
    )

    patterns = [
        r"\b(\d+(?:\.\d+)?)\+?\s+years?\s+of\s+experience\b",
        r"\b(\d+(?:\.\d+)?)\+?\s+years?\s+experience\b",
        r"\bexperience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s+years?\b",
    ]

    values: list[float] = []

    for pattern in patterns:
        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            try:
                values.append(
                    float(
                        match.group(1)
                    )
                )
            except ValueError:
                continue

    if not values:
        return None

    return max(values)


def _extract_resume_technical_experience(
    resume_text: str,
    skills: Iterable[str],
) -> dict[str, float]:
    """
    Extract explicit technology-specific experience.

    Example:

        "3 years of Python experience"

    becomes:

        {"python": 3}

    No experience is inferred merely because a skill is
    mentioned.
    """
    if not resume_text:
        return {}

    text = _normalize_text(
        resume_text
    )

    result: dict[str, float] = {}

    for skill in skills:
        canonical = _canonical_match_key(
            skill
        )

        if not canonical:
            continue

        variants = _candidate_variants(
            canonical
        )

        for variant in variants:
            escaped = re.escape(
                variant
            )

            patterns = [
                (
                    rf"\b(\d+(?:\.\d+)?)\+?\s+years?\s+"
                    rf"(?:of\s+)?experience\s+"
                    rf"(?:with|in|using)\s+"
                    rf"{escaped}\b"
                ),
                (
                    rf"\b(\d+(?:\.\d+)?)\+?\s+years?\s+"
                    rf"{escaped}\s+experience\b"
                ),
                (
                    rf"\b{escaped}\s*[:\-]?\s*"
                    rf"(\d+(?:\.\d+)?)\+?\s+years?\b"
                ),
            ]

            for pattern in patterns:
                match = re.search(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )

                if not match:
                    continue

                try:
                    years = float(
                        match.group(1)
                    )
                except ValueError:
                    continue

                result[canonical] = max(
                    result.get(
                        canonical,
                        0,
                    ),
                    years,
                )

                break

            if canonical in result:
                break

    return result


# ============================================================
# EXPERIENCE INTELLIGENCE
# ============================================================

def _build_experience_analysis(
    resume_text: str,
    experience_requirements: dict,
    resume_skills: Iterable[str],
) -> tuple[
    dict,
    float,
    list[str],
]:
    """
    Build overall and technical experience intelligence.

    Returns:

        experience_analysis
        experience_factor
        experience_warnings
    """
    overall_required = (
        experience_requirements.get(
            "overall_years"
        )
    )

    technical_required = (
        experience_requirements.get(
            "technical_years",
            [],
        )
    )

    resume_years = (
        _estimate_resume_experience_years(
            resume_text
        )
    )

    technical_resume_years = (
        _extract_resume_technical_experience(
            resume_text,
            resume_skills,
        )
    )

    if overall_required is None:
        overall_result = calculate_experience_gap(
            None,
            resume_years,
        )
    else:
        overall_result = calculate_experience_gap(
            overall_required,
            resume_years,
        )

    technical_results = (
        calculate_technical_experience_gaps(
            technical_required,
            technical_resume_years,
        )
    )

    warnings: list[str] = []

    if (
        overall_result["status"]
        == "unknown"
        and overall_required is not None
    ):
        warnings.append(
            "Overall experience could not be verified "
            "from the resume."
        )

    unknown_technical = [
        item["skill"]
        for item in technical_results
        if item["status"] == "unknown"
    ]

    if unknown_technical:
        warnings.append(
            "Technical experience could not be verified "
            "for: "
            + ", ".join(
                unknown_technical[:5]
            )
            + "."
        )

    # --------------------------------------------------------
    # Experience factor
    # --------------------------------------------------------

    factor = 1.0

    if overall_required is not None:
        if (
            overall_result["status"]
            == "meets_requirement"
        ):
            factor *= 1.0

        elif (
            overall_result["status"]
            == "below_requirement"
        ):
            required = overall_result[
                "required_years"
            ]

            actual = (
                overall_result[
                    "resume_years"
                ]
                or 0
            )

            if required and required > 0:
                ratio = actual / required

                factor *= max(
                    0.50,
                    min(
                        1.0,
                        ratio,
                    ),
                )

        else:
            factor *= 0.85

    if technical_results:
        known_results = [
            item
            for item in technical_results
            if item["status"] != "unknown"
        ]

        if known_results:
            satisfied = sum(
                1
                for item in known_results
                if item["status"]
                == "meets_requirement"
            )

            technical_factor = (
                satisfied
                / len(known_results)
            )

            factor *= (
                0.75
                + (
                    0.25
                    * technical_factor
                )
            )

        else:
            factor *= 0.90

    factor = max(
        0.50,
        min(
            1.0,
            factor,
        ),
    )

    experience_analysis = {
        "overall_years": {
            "required": overall_result.get(
                "required_years"
            ),
            "evidence_found": overall_result.get(
                "resume_years"
            ),
            "status": (
                "not_detected"
                if overall_required is None
                else (
                    "meets_requirement"
                    if overall_result["status"]
                    == "meets_requirement"
                    else (
                        "below_requirement"
                        if overall_result["status"]
                        == "below_requirement"
                        else "unknown"
                    )
                )
            ),
        },
        "technical_years": {
            "required": technical_results,
        },
    }

    return (
        experience_analysis,
        factor,
        warnings,
    )


# ============================================================
# ENTRY-LEVEL / FRESHER DETECTION
# ============================================================

def _job_encourages_entry_level(
    job_description: str,
) -> bool:
    """
    Detect explicit entry-level/fresher language in a job
    description.

    This does not infer candidate experience.

    It only prevents misleading recommendations when the
    employer explicitly welcomes early-career candidates.
    """
    text = _normalize_text(
        job_description
    )

    if not text:
        return False

    patterns = [
        r"\bfresh\s+graduates?\s+(?:are\s+)?encouraged\b",
        r"\brecent\s+graduates?\s+(?:are\s+)?encouraged\b",
        r"\bgraduates?\s+(?:are\s+)?encouraged\b",
        r"\bentry[- ]level\b",
        r"\bjunior\b",
        r"\b0\s*[-–]\s*2\s+years?\b",
        r"\b0\s+to\s+2\s+years?\b",
        r"\b0\s*[-–]\s*1\s+years?\b",
        r"\b0\s+to\s+1\s+years?\b",
        r"\b1\s*[-–]\s*2\s+years?\b",
        r"\b1\s+to\s+2\s+years?\b",
    ]

    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        for pattern in patterns
    )


# ============================================================
# SCORE LEVEL
# ============================================================

def _get_match_level(
    score: int,
) -> str:
    """
    Convert numeric score to user-facing match level.
    """
    if score >= EXCELLENT_MATCH_THRESHOLD:
        return "Excellent"

    if score >= STRONG_MATCH_THRESHOLD:
        return "Strong"

    if score >= MODERATE_MATCH_THRESHOLD:
        return "Moderate"

    if score > 0:
        return "Weak"

    return "No Match"


# ============================================================
# APPLICATION READINESS
# ============================================================

def _get_application_readiness(
    score: int,
    requirements: list[Requirement],
    missing_skills: list[str],
    experience_analysis: dict,
) -> str:
    """
    Determine application readiness.

    This is deliberately more conservative than the raw score.
    """
    missing_set = {
        _canonical_match_key(skill)
        for skill in missing_skills
    }

    missing_must_have = {
        _canonical_match_key(
            requirement.skill
        )
        for requirement in requirements
        if (
            _normalize_priority(
                requirement.priority
            )
            == "must_have"
        )
        and _canonical_match_key(
            requirement.skill
        ) in missing_set
    }

    if (
        len(missing_must_have) >= 3
        and score < STRONG_MATCH_THRESHOLD
    ):
        return "Low Alignment"

    overall_status = (
        experience_analysis
        .get("overall_years", {})
        .get("status")
    )

    if (
        overall_status
        == "below_requirement"
    ):
        return "Needs Experience"

    if score >= HIGH_READINESS_THRESHOLD:
        return "High Readiness"

    if score >= MODERATE_READINESS_THRESHOLD:
        return "Moderate Readiness"

    return "Low Alignment"


# ============================================================
# SUGGESTIONS
# ============================================================

def _build_suggestions(
    requirements: list[Requirement],
    missing_skills: list[str],
    experience_analysis: dict,
    score: int,
    job_description: str = "",
) -> list[str]:
    """
    Build actionable, evidence-safe recommendations.

    Entry-level/fresher jobs do not receive a misleading
    "job requires prior experience" recommendation when the JD
    explicitly welcomes early-career candidates.
    """
    suggestions: list[str] = []

    missing_set = {
        _canonical_match_key(skill)
        for skill in missing_skills
    }

    high_impact: list[str] = []

    for requirement in requirements:
        canonical = _canonical_match_key(
            requirement.skill
        )

        if (
            canonical in missing_set
            and _normalize_priority(
                requirement.priority
            )
            == "must_have"
        ):
            if requirement.skill not in high_impact:
                high_impact.append(
                    requirement.skill
                )

    if high_impact:
        suggestions.append(
            "Prioritize these high-impact missing "
            "requirements: "
            + ", ".join(
                high_impact[:5]
            )
            + "."
        )

    overall = experience_analysis.get(
        "overall_years",
        {},
    )

    entry_level_role = _job_encourages_entry_level(
        job_description
    )

    if (
        overall.get("status")
        == "below_requirement"
    ):
        required = overall.get(
            "required"
        )

        actual = overall.get(
            "evidence_found"
        )

        if entry_level_role:
            suggestions.append(
                "The role appears to be entry-level or "
                "open to early-career candidates; the resume "
                "does not show explicit years of professional "
                "experience, so emphasize projects and other "
                "practical evidence."
            )
        else:
            suggestions.append(
                f"The role requests {required} years "
                f"of experience, while the resume shows "
                f"{actual} years of explicit evidence."
            )

    elif (
        overall.get("status")
        == "unknown"
    ):
        if (
            overall.get("required") is not None
            and not entry_level_role
        ):
            suggestions.append(
                "The job has an experience expectation, "
                "but the resume does not provide enough "
                "explicit evidence to verify the candidate's "
                "professional experience."
            )

    if score < MODERATE_MATCH_THRESHOLD:
        suggestions.append(
            "The role has limited technical overlap "
            "with the resume. Consider targeting roles "
            "with stronger alignment."
        )

    suggestions.append(
        "Only add technologies or experience to the "
        "resume when you genuinely have relevant evidence."
    )

    return suggestions


# ============================================================
# MAIN MATCH FUNCTION
# ============================================================

def compare_resume_job(
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:
    """
    Compare a resume against a job description.

    Returns a production-oriented structured response.

    Backward compatibility:

    - Empty resume returns a zero-score result.
    - Empty job description returns a zero-score result.
    - match_score remains the direct requirement coverage
      percentage expected by the existing API/tests.
    """
    resume_text = _safe_text(
        resume_text
    )

    job_description = _safe_text(
        job_description
    )

    # ========================================================
    # EMPTY JOB DESCRIPTION
    # ========================================================

    if not job_description:
        return {
            "match_score": 0,
            "match_level": "No Match",
            "application_readiness": "Low Alignment",
            "matched_skills": [],
            "missing_skills": [],
            "critical_missing_skills": [],
            "resume_categories": {},
            "job_categories": {},
            "category_coverage": {},
            "requirements": [],
            "requirement_priorities": {},
            "requirement_weights": {},
            "requirement_priority_counts": {},
            "requirement_coverage": {
                "matched": 0,
                "total": 0,
                "percentage": 0,
                "weighted_score": 0,
            },
            "experience_requirements": {
                "overall_years": {
                    "required": None,
                    "evidence_found": None,
                    "status": "not_detected",
                },
                "technical_years": {
                    "required": [],
                },
            },
            "resume_experience_years": None,
            "experience_gap": (
                calculate_experience_gap(
                    None,
                    None,
                )
            ),
            "suggestions": [
                "Provide a job description to "
                "calculate job matching."
            ],
            "suggestion": (
                "Provide a job description to "
                "calculate job matching."
            ),
        }

    # ========================================================
    # EMPTY RESUME
    # ========================================================

    if not resume_text:
        job_skills = _extract_job_skills(
            job_description
        )

        requirements = _clean_requirements(
            build_requirements(
                job_skills
            )
        )

        missing_skills: list[str] = []
        seen_missing: set[str] = set()

        for requirement in requirements:
            canonical = _canonical_match_key(
                requirement.skill
            )

            if not canonical:
                continue

            if canonical not in seen_missing:
                missing_skills.append(
                    canonical
                )
                seen_missing.add(
                    canonical
                )

        job_categories = _categorize_skills(
            job_skills
        )

        requirement_results = [
            {
                "skill": requirement.skill,
                "priority": requirement.priority,
                "weight": requirement.weight,
                "category": requirement.category,
                "matched": False,
            }
            for requirement in requirements
        ]

        requirement_priorities = (
            split_requirements(
                requirements
            )
        )

        requirement_weights = (
            get_requirement_weights(
                requirements
            )
        )

        requirement_priority_counts = (
            get_requirement_priority_counts(
                requirements
            )
        )

        extracted_experience = (
            extract_experience_requirements(
                job_description
            )
        )

        (
            experience_analysis,
            _experience_factor,
            experience_warnings,
        ) = _build_experience_analysis(
            "",
            extracted_experience,
            [],
        )

        suggestions = [
            "Upload or provide resume text to "
            "calculate job matching."
        ]

        suggestions.extend(
            experience_warnings
        )

        suggestions = list(
            dict.fromkeys(
                suggestions
            )
        )

        critical_missing = []
        seen_critical: set[str] = set()

        for requirement in requirements:
            if (
                _normalize_priority(
                    requirement.priority
                )
                != "must_have"
            ):
                continue

            canonical = _canonical_match_key(
                requirement.skill
            )

            if not canonical:
                continue

            if canonical in seen_critical:
                continue

            critical_missing.append(
                canonical
            )

            seen_critical.add(
                canonical
            )

        return {
            "match_score": 0,
            "match_level": "No Match",
            "application_readiness": "Low Alignment",
            "matched_skills": [],
            "missing_skills": missing_skills,
            "critical_missing_skills": critical_missing,
            "resume_categories": {},
            "job_categories": job_categories,
            "category_coverage": {
                category: 0
                for category in job_categories
            },
            "requirements": requirement_results,
            "requirement_priorities": (
                requirement_priorities
            ),
            "requirement_weights": (
                requirement_weights
            ),
            "requirement_priority_counts": (
                requirement_priority_counts
            ),
            "requirement_coverage": {
                "matched": 0,
                "total": len(requirements),
                "percentage": 0,
                "weighted_score": 0,
            },
            "experience_requirements": (
                experience_analysis
            ),
            "resume_experience_years": None,
            "experience_gap": (
                calculate_experience_gap(
                    experience_analysis
                    .get("overall_years", {})
                    .get("required"),
                    None,
                )
            ),
            "suggestions": suggestions,
            "suggestion": suggestions[0],
        }

    # ========================================================
    # EXTRACT SKILLS
    # ========================================================

    resume_skills = _extract_resume_skills(
        resume_text
    )

    job_skills = _extract_job_skills(
        job_description
    )

    # ========================================================
    # BUILD + CLEAN REQUIREMENTS
    # ========================================================

    requirements = _clean_requirements(
        build_requirements(
            job_skills
        )
    )

    # ========================================================
    # MATCH REQUIREMENTS
    # ========================================================

    (
        matched_skills,
        missing_skills,
        requirement_results,
    ) = _match_requirements(
        resume_text,
        requirements,
    )

    # ========================================================
    # REQUIREMENT COVERAGE
    # ========================================================

    weighted_score = calculate_weighted_match(
        requirements,
        matched_skills,
    )

    # Count directly from the requirement results.
    #
    # This is important because requirement matching can use
    # one-way evidence relationships that are not represented
    # by simply comparing two canonical skill lists.

    matched_count = sum(
        1
        for item in requirement_results
        if item.get("matched") is True
    )

    total_count = len(
        requirements
    )

    percentage = (
        round(
            (
                matched_count
                / total_count
            )
            * 100
        )
        if total_count
        else 0
    )

    # ========================================================
    # CATEGORIES
    # ========================================================

    resume_categories = _categorize_skills(
        resume_skills
    )

    job_categories = _categorize_skills(
        job_skills
    )

    category_coverage = (
        _calculate_category_coverage(
            resume_categories,
            job_categories,
        )
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    extracted_experience = (
        extract_experience_requirements(
            job_description
        )
    )

    (
        experience_analysis,
        _experience_factor,
        experience_warnings,
    ) = _build_experience_analysis(
        resume_text,
        extracted_experience,
        resume_skills,
    )

    # ========================================================
    # FINAL SCORE
    #
    # IMPORTANT:
    #
    # Public match_score remains the direct percentage
    # of matched cleaned job requirements.
    #
    # weighted_score remains available separately.
    # ========================================================

    final_score = round(
        percentage
    )

    final_score = max(
        0,
        min(
            100,
            final_score,
        ),
    )

    # ========================================================
    # CRITICAL MISSING
    # ========================================================

    missing_set = {
        _canonical_match_key(skill)
        for skill in missing_skills
    }

    critical_missing: list[str] = []
    seen_critical: set[str] = set()

    for requirement in requirements:
        canonical = _canonical_match_key(
            requirement.skill
        )

        if not canonical:
            continue

        if (
            canonical in missing_set
            and _normalize_priority(
                requirement.priority
            )
            == "must_have"
            and canonical not in seen_critical
        ):
            critical_missing.append(
                canonical
            )

            seen_critical.add(
                canonical
            )

    # ========================================================
    # PRIORITIES / WEIGHTS
    # ========================================================

    requirement_priorities = (
        split_requirements(
            requirements
        )
    )

    requirement_weights = (
        get_requirement_weights(
            requirements
        )
    )

    requirement_priority_counts = (
        get_requirement_priority_counts(
            requirements
        )
    )

    # ========================================================
    # READINESS
    # ========================================================

    application_readiness = (
        _get_application_readiness(
            final_score,
            requirements,
            missing_skills,
            experience_analysis,
        )
    )

    # ========================================================
    # SUGGESTIONS
    # ========================================================

    suggestions = _build_suggestions(
        requirements,
        missing_skills,
        experience_analysis,
        final_score,
        job_description,
    )

    suggestions.extend(
        experience_warnings
    )

    suggestions = list(
        dict.fromkeys(
            suggestions
        )
    )

    suggestion = (
        suggestions[0]
        if suggestions
        else "No major improvements identified."
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        # ----------------------------------------------------
        # Core score
        # ----------------------------------------------------

        "match_score": final_score,

        "match_level": _get_match_level(
            final_score
        ),

        "application_readiness": (
            application_readiness
        ),

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "critical_missing_skills": (
            critical_missing
        ),

        # ----------------------------------------------------
        # Categories
        # ----------------------------------------------------

        "resume_categories": (
            resume_categories
        ),

        "job_categories": (
            job_categories
        ),

        "category_coverage": (
            category_coverage
        ),

        # ----------------------------------------------------
        # Requirement details
        # ----------------------------------------------------

        "requirements": (
            requirement_results
        ),

        "requirement_priorities": (
            requirement_priorities
        ),

        "requirement_weights": (
            requirement_weights
        ),

        "requirement_priority_counts": (
            requirement_priority_counts
        ),

        "requirement_coverage": {
            "matched": matched_count,
            "total": total_count,
            "percentage": percentage,
            "weighted_score": weighted_score,
        },

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        "experience_requirements": (
            experience_analysis
        ),

        "resume_experience_years": (
            experience_analysis
            .get("overall_years", {})
            .get("evidence_found")
        ),

        "experience_gap": (
            calculate_experience_gap(
                experience_analysis
                .get("overall_years", {})
                .get("required"),
                experience_analysis
                .get("overall_years", {})
                .get("evidence_found"),
            )
        ),

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        "suggestions": suggestions,

        "suggestion": suggestion,
    }