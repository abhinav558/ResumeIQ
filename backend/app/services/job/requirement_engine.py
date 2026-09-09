"""
ResumeIQ - Production Job Requirement Engine

Responsibilities
----------------
- Normalize job requirements
- Canonicalize aliases using the central keyword database
- Classify requirements
- Detect requirement priority from job-description context
- Assign deterministic requirement weights
- Remove semantic duplicates
- Extract overall experience requirements
- Extract technology-specific experience requirements
- Calculate weighted requirement coverage
- Calculate experience gaps

The central keyword database remains the single source of truth for:
- technical skills
- aliases
- categories
- engineering terminology
- networking terminology
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from ..keyword_db import (
    ENGINEERING,
    NETWORKING,
    ALL_TECHNOLOGIES,
    get_canonical_skill,
    normalize_keyword,
)


# ============================================================
# REQUIREMENT MODEL
# ============================================================

@dataclass(frozen=True)
class Requirement:
    skill: str
    priority: str
    weight: int
    category: str = "technical"


# ============================================================
# WEIGHTS
# ============================================================

MUST_HAVE_WEIGHT = 5
PREFERRED_WEIGHT = 3
SUPPORTING_WEIGHT = 1


# ============================================================
# PRIORITY TERMS
# ============================================================

MUST_HAVE_CONTEXT = (
    "required",
    "requirements",
    "requirement",
    "must have",
    "must-have",
    "must possess",
    "mandatory",
    "essential",
    "necessary",
    "minimum",
    "need to have",
    "should have",
    "should possess",
)

PREFERRED_CONTEXT = (
    "preferred",
    "prefer",
    "preferred qualification",
    "preferred qualifications",
    "desired",
    "desirable",
    "good to have",
    "good-to-have",
    "nice to have",
    "nice-to-have",
    "plus",
    "bonus",
    "advantage",
    "a plus",
)

SUPPORTING_CONTEXT = (
    "optional",
    "optionally",
    "familiarity",
    "exposure",
    "knowledge of",
    "understanding of",
)


# ============================================================
# HIGH-VALUE DEFAULT REQUIREMENTS
# ============================================================

MUST_HAVE_TERMS = {
    "python",
    "java",
    "c++",
    "javascript",
    "typescript",
    "c#",
    "sql",

    "machine learning",
    "deep learning",

    "fastapi",
    "django",
    "flask",
    "react",
    "nodejs",

    "spring",
    "spring boot",
    "spring mvc",

    "postgresql",
    "mysql",
    "mongodb",

    "aws",
    "azure",
    "gcp",

    "docker",
    "kubernetes",

    "networking",
    "network design",
    "networking systems",

    "distributed systems",
    "distributed applications",

    "software development",
    "software engineering",

    "testing",
    "unit testing",
}


# ============================================================
# PREFERRED DEFAULT REQUIREMENTS
# ============================================================

PREFERRED_TERMS = {
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",

    "redis",
    "graphql",
    "rest api",

    "ci/cd",
    "continuous integration",
    "continuous delivery",

    "jenkins",
    "github actions",
    "terraform",

    "orm",

    "html5",
    "css3",

    "wicket",
    "gwt",

    "automation",
    "test automation",

    "code review",
    "monitoring",
    "automated remediation",

    "documentation",
    "version control",
}


# ============================================================
# NORMALIZED TERM SETS
# ============================================================

def _normalize_terms(terms: Iterable[str]) -> set[str]:
    """
    Normalize a collection of terms using the central
    ResumeIQ keyword database.
    """
    result: set[str] = set()

    for term in terms:
        if not term:
            continue

        canonical = get_canonical_skill(term)

        if canonical:
            result.add(canonical)

    return result


TECHNICAL_TERMS = _normalize_terms(
    ALL_TECHNOLOGIES
)

ENGINEERING_TERMS = _normalize_terms(
    ENGINEERING
)

NETWORKING_TERMS = _normalize_terms(
    NETWORKING
)

NORMALIZED_MUST_HAVE_TERMS = _normalize_terms(
    MUST_HAVE_TERMS
)

NORMALIZED_PREFERRED_TERMS = _normalize_terms(
    PREFERRED_TERMS
)


# ============================================================
# CANONICAL OVERLAPS
# ============================================================

RELATED_REQUIREMENTS = {
    "spring": {
        "spring",
    },

    "spring mvc": {
        "spring mvc",
        "spring mvc framework",
    },

    "spring boot": {
        "spring boot",
        "springboot",
    },

    "nodejs": {
        "node",
        "nodejs",
        "node.js",
        "node js",
    },

    "react": {
        "react",
        "react.js",
        "react js",
    },

    "ci/cd": {
        "ci/cd",
        "ci cd",
        "ci-cd",
        "continuous integration",
        "continuous delivery",
    },

    "testing": {
        "testing",
        "unit testing",
        "integration testing",
        "test automation",
    },

    "distributed systems": {
        "distributed systems",
        "distributed applications",
    },

    "networking": {
        "network",
        "networking",
        "networking systems",
        "network design",
        "network architecture",
    },

    "software development": {
        "software development",
        "software engineering",
        "software development lifecycle",
        "sdlc",
    },
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill using the central ResumeIQ keyword database.

    Important technical identifiers such as:
        C++
        C#
        CI/CD
        .NET
    are preserved by the central normalization system.
    """
    if not skill:
        return ""

    return normalize_keyword(skill)


# ============================================================
# CANONICAL REQUIREMENT
# ============================================================

def _canonical_requirement(skill: str) -> str:
    """
    Convert requirement variants into one canonical form.

    Central aliases are resolved first, followed by
    ResumeIQ-specific semantic relationships.
    """
    normalized = normalize_skill(skill)

    if not normalized:
        return ""

    for canonical, variants in RELATED_REQUIREMENTS.items():

        normalized_variants = {
            normalize_skill(value)
            for value in variants
        }

        if normalized in normalized_variants:
            return canonical

    return normalized


# ============================================================
# CATEGORY
# ============================================================

def get_requirement_category(skill: str) -> str:
    """
    Determine requirement category.

    Priority:
        networking
        engineering
        technical
        other
    """
    normalized = _canonical_requirement(skill)

    if not normalized:
        return "other"

    if normalized in NETWORKING_TERMS:
        return "networking"

    if normalized in ENGINEERING_TERMS:
        return "engineering"

    if normalized in TECHNICAL_TERMS:
        return "technical"

    return "other"


# ============================================================
# CONTEXT UTILITIES
# ============================================================

def _normalize_context(text: str) -> str:
    """
    Normalize text used for contextual priority detection.
    """
    if not text:
        return ""

    text = str(text).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains_context(
    context: str,
    phrases: Iterable[str],
) -> bool:
    """
    Determine whether a context contains one of the
    supplied priority phrases.
    """
    if not context:
        return False

    normalized = _normalize_context(context)

    for phrase in phrases:

        phrase = _normalize_context(phrase)

        if not phrase:
            continue

        if phrase in normalized:
            return True

    return False


# ============================================================
# PRIORITY FROM CONTEXT
# ============================================================

def _priority_from_context(
    skill: str,
    context: str | None,
) -> str | None:
    """
    Determine requirement priority from surrounding JD context.

    Returns:
        must_have
        preferred
        supporting
        None

    None means there is not enough contextual evidence and
    the deterministic default classification should be used.
    """
    if not context:
        return None

    normalized_context = _normalize_context(context)

    if not normalized_context:
        return None

    # --------------------------------------------------------
    # Explicit optional/supporting language
    # --------------------------------------------------------

    if _contains_context(
        normalized_context,
        SUPPORTING_CONTEXT,
    ):
        return "supporting"

    # --------------------------------------------------------
    # Preferred / bonus language
    # --------------------------------------------------------

    if _contains_context(
        normalized_context,
        PREFERRED_CONTEXT,
    ):
        return "preferred"

    # --------------------------------------------------------
    # Explicit required language
    # --------------------------------------------------------

    if _contains_context(
        normalized_context,
        MUST_HAVE_CONTEXT,
    ):
        return "must_have"

    return None


# ============================================================
# PRIORITY
# ============================================================

def classify_requirement(
    skill: str,
    context: str | None = None,
) -> Requirement:
    """
    Assign priority and weight.

    If explicit job-description context is available,
    contextual priority takes precedence over the default
    skill classification.

    Without contextual evidence, ResumeIQ falls back to
    deterministic skill/category defaults.
    """
    normalized = _canonical_requirement(skill)

    if not normalized:
        return Requirement(
            skill="",
            priority="supporting",
            weight=SUPPORTING_WEIGHT,
            category="other",
        )

    category = get_requirement_category(
        normalized
    )

    contextual_priority = _priority_from_context(
        normalized,
        context,
    )

    if contextual_priority == "must_have":
        return Requirement(
            skill=normalized,
            priority="must_have",
            weight=MUST_HAVE_WEIGHT,
            category=category,
        )

    if contextual_priority == "preferred":
        return Requirement(
            skill=normalized,
            priority="preferred",
            weight=PREFERRED_WEIGHT,
            category=category,
        )

    if contextual_priority == "supporting":
        return Requirement(
            skill=normalized,
            priority="supporting",
            weight=SUPPORTING_WEIGHT,
            category=category,
        )

    # --------------------------------------------------------
    # Deterministic fallback
    # --------------------------------------------------------

    if normalized in NORMALIZED_MUST_HAVE_TERMS:
        return Requirement(
            skill=normalized,
            priority="must_have",
            weight=MUST_HAVE_WEIGHT,
            category=category,
        )

    if normalized in NORMALIZED_PREFERRED_TERMS:
        return Requirement(
            skill=normalized,
            priority="preferred",
            weight=PREFERRED_WEIGHT,
            category=category,
        )

    if category == "networking":
        return Requirement(
            skill=normalized,
            priority="must_have",
            weight=MUST_HAVE_WEIGHT,
            category=category,
        )

    if category == "engineering":
        return Requirement(
            skill=normalized,
            priority="preferred",
            weight=PREFERRED_WEIGHT,
            category=category,
        )

    return Requirement(
        skill=normalized,
        priority="supporting",
        weight=SUPPORTING_WEIGHT,
        category=category,
    )


# ============================================================
# BUILD REQUIREMENTS
# ============================================================

def build_requirements(
    skills: Iterable[str],
    contexts: dict[str, str] | None = None,
) -> list[Requirement]:
    """
    Convert detected skills into unique normalized requirements.

    `contexts` optionally maps a skill/canonical skill to
    surrounding job-description context.

    Existing callers that provide only `skills` remain
    fully backward compatible.
    """
    requirements: list[Requirement] = []
    seen: set[str] = set()

    contexts = contexts or {}

    for skill in skills:

        if not skill:
            continue

        normalized = normalize_skill(skill)

        if not normalized:
            continue

        canonical = _canonical_requirement(
            normalized
        )

        if not canonical:
            continue

        if canonical in seen:
            continue

        seen.add(canonical)

        context = (
            contexts.get(canonical)
            or contexts.get(normalized)
        )

        requirements.append(
            classify_requirement(
                canonical,
                context=context,
            )
        )

    return requirements


# ============================================================
# WEIGHTED MATCH
# ============================================================

def calculate_weighted_match(
    requirements: list[Requirement],
    matched_skills: Iterable[str],
) -> int:
    """
    Calculate weighted requirement coverage percentage.
    """
    if not requirements:
        return 0

    matched = {
        _canonical_requirement(skill)
        for skill in matched_skills
        if skill
    }

    total_weight = sum(
        requirement.weight
        for requirement in requirements
    )

    if total_weight <= 0:
        return 0

    matched_weight = sum(
        requirement.weight
        for requirement in requirements
        if _canonical_requirement(
            requirement.skill
        ) in matched
    )

    return round(
        (matched_weight / total_weight) * 100
    )


# ============================================================
# PRIORITY SPLIT
# ============================================================

def split_requirements(
    requirements: list[Requirement],
) -> dict[str, list[str]]:
    """
    Group requirements by priority.
    """
    result = {
        "must_have": [],
        "preferred": [],
        "supporting": [],
    }

    for requirement in requirements:

        result.setdefault(
            requirement.priority,
            [],
        )

        result[
            requirement.priority
        ].append(
            requirement.skill
        )

    return result


# ============================================================
# WEIGHT MAP
# ============================================================

def get_requirement_weights(
    requirements: list[Requirement],
) -> dict[str, int]:
    """
    Return requirement -> weight mapping.
    """
    return {
        requirement.skill: requirement.weight
        for requirement in requirements
    }


# ============================================================
# PRIORITY COUNTS
# ============================================================

def get_requirement_priority_counts(
    requirements: list[Requirement],
) -> dict[str, int]:
    """
    Return number of requirements in each priority level.
    """
    counts = {
        "must_have": 0,
        "preferred": 0,
        "supporting": 0,
    }

    for requirement in requirements:

        priority = requirement.priority

        counts.setdefault(
            priority,
            0,
        )

        counts[priority] += 1

    return counts


# Backward-compatible alias.
get_priority_counts = get_requirement_priority_counts


# ============================================================
# EXPERIENCE NUMBER PARSING
# ============================================================

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _parse_experience_number(
    value: str,
) -> int | None:
    """
    Parse numeric and common written-number
    experience values.
    """
    if not value:
        return None

    value = value.strip().lower()

    if value.isdigit():
        return int(value)

    return NUMBER_WORDS.get(value)


# ============================================================
# EXPERIENCE RANGE PARSING
# ============================================================

def _parse_experience_range(
    value: str,
) -> tuple[int | None, int | None]:
    """
    Parse experience values such as:

        3
        3+
        3-5
        3–5
        3 to 5
        three to five

    Returns:
        (minimum, maximum)

    For a single value:
        (value, value)
    """
    if not value:
        return None, None

    value = value.strip().lower()

    # Normalize dash variants.
    value = value.replace("–", "-")
    value = value.replace("—", "-")

    # Single value.
    single = _parse_experience_number(
        value.rstrip("+").strip()
    )

    if single is not None:
        return single, single

    # Numeric range.
    range_match = re.fullmatch(
        r"(\d+)\s*(?:-|to)\s*(\d+)",
        value,
    )

    if range_match:
        first = int(range_match.group(1))
        second = int(range_match.group(2))

        return (
            min(first, second),
            max(first, second),
        )

    # Written range.
    written_match = re.fullmatch(
        r"([a-z]+)\s*(?:-|to)\s*([a-z]+)",
        value,
    )

    if written_match:
        first = _parse_experience_number(
            written_match.group(1)
        )
        second = _parse_experience_number(
            written_match.group(2)
        )

        if first is not None and second is not None:
            return (
                min(first, second),
                max(first, second),
            )

    return None, None


# ============================================================
# EXPERIENCE EXTRACTION HELPERS
# ============================================================

def _extract_skill_candidates(
    text: str,
) -> list[str]:
    """
    Extract known technology names from a text fragment.

    Only technologies known to the central ResumeIQ database
    or explicit requirement dictionaries are considered.
    """
    if not text:
        return []

    normalized_text = str(text).lower()

    candidates: list[str] = []

    known_terms = {
        normalize_skill(skill)
        for skill in (
            set(ALL_TECHNOLOGIES)
            | set(MUST_HAVE_TERMS)
            | set(PREFERRED_TERMS)
        )
        if skill
    }

    ordered_terms = sorted(
        known_terms,
        key=len,
        reverse=True,
    )

    for skill in ordered_terms:

        if not skill:
            continue

        escaped = re.escape(skill)

        pattern = (
            rf"(?<![a-z0-9+#])"
            rf"{escaped}"
            rf"(?![a-z0-9+#])"
        )

        if not re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE,
        ):
            continue

        canonical = _canonical_requirement(
            skill
        )

        if (
            canonical
            and canonical not in candidates
        ):
            candidates.append(
                canonical
            )

    return candidates


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience_requirements(
    job_description: str,
) -> dict:
    """
    Detect overall and technology-specific experience.

    Supported examples:

        5 years of experience
        five years of experience
        5+ years of experience
        five or more years of experience
        minimum of 5 years
        at least 5 years
        3-5 years of experience
        3–5 years of experience
        3 to 5 years of experience

        7 years of experience with Java, Python, and C++
        3+ years with Python
        4 years experience in Java and Spring
        3 years of experience using Python
    """
    if not job_description:
        return {
            "overall_years": None,
            "technical_years": [],
        }

    text = str(job_description)

    overall_years: int | None = None

    technical_years: list[dict] = []

    number_atom = (
        r"(?:"
        r"\d+"
        r"|zero|one|two|three|four|five|six|seven|eight|nine|"
        r"ten|eleven|twelve|thirteen|fourteen|fifteen|"
        r"sixteen|seventeen|eighteen|nineteen|twenty"
        r")"
    )

    experience_value = (
        rf"(?:"
        rf"{number_atom}"
        rf"(?:\s*(?:-|–|—|to)\s*{number_atom})?"
        rf")"
    )

    # ========================================================
    # OVERALL EXPERIENCE
    # ========================================================

    overall_patterns = [

        # 3-5 years of experience
        rf"\b({experience_value})\s*"
        rf"(?:\+|or\s+more)?\s*"
        rf"years?\s+of\s+experience\b",

        # minimum of 3 years
        rf"\bminimum\s+of\s+({number_atom})\s*"
        rf"(?:\+|or\s+more)?\s*years?\b",

        # at least 3 years
        rf"\bat\s+least\s+({number_atom})\s*"
        rf"(?:\+|or\s+more)?\s*years?\b",

        # 3 years experience
        rf"\b({experience_value})\s*"
        rf"(?:\+|or\s+more)?\s*"
        rf"years?\s+experience\b",
    ]

    for pattern in overall_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        value = match.group(1)

        minimum, maximum = _parse_experience_range(
            value
        )

        if minimum is not None:
            # For matching purposes, the minimum requirement
            # is the safest interpretation.
            overall_years = minimum
            break

    # ========================================================
    # TECHNICAL EXPERIENCE
    # ========================================================

    technical_patterns = [

        # 3 years of experience with Python
        rf"\b({experience_value})\s*"
        rf"(?:\+|or\s+more)?\s*"
        rf"years?\s+of\s+experience\s+"
        rf"(?:with|in|using)\s+([^.;\n]+)",

        # 3 years with Python
        rf"\b({experience_value})\s*"
        rf"(?:\+|or\s+more)?\s*"
        rf"years?\s+"
        rf"(?:of\s+experience\s+)?"
        rf"(?:with|in|using)\s+([^.;\n]+)",

        # 3 years experience with Python
        rf"\b({experience_value})\s*"
        rf"(?:\+|or\s+more)?\s*"
        rf"years?\s+experience\s+"
        rf"(?:with|in|using)\s+([^.;\n]+)",
    ]

    seen_technical: set[str] = set()

    for pattern in technical_patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            value = match.group(1)

            minimum, _maximum = _parse_experience_range(
                value
            )

            if minimum is None:
                continue

            skill_fragment = match.group(2)

            skills = _extract_skill_candidates(
                skill_fragment
            )

            for skill in skills:

                if skill in seen_technical:
                    continue

                seen_technical.add(skill)

                technical_years.append(
                    {
                        "skill": skill,
                        "required_years": minimum,
                    }
                )

    return {
        "overall_years": overall_years,
        "technical_years": technical_years,
    }


# ============================================================
# EXPERIENCE GAP
# ============================================================

def calculate_experience_gap(
    required_years: int | None,
    resume_years: float | None,
) -> dict:
    """
    Calculate an experience gap without inventing experience.
    """
    if required_years is None:
        return {
            "required_years": None,
            "resume_years": resume_years,
            "gap_years": 0,
            "status": "not_required",
        }

    if resume_years is None:
        return {
            "required_years": required_years,
            "resume_years": None,
            "gap_years": None,
            "status": "unknown",
        }

    gap = max(
        0,
        required_years - resume_years,
    )

    return {
        "required_years": required_years,
        "resume_years": resume_years,
        "gap_years": gap,
        "status": (
            "meets_requirement"
            if gap == 0
            else "below_requirement"
        ),
    }


# ============================================================
# TECHNICAL EXPERIENCE GAPS
# ============================================================

def calculate_technical_experience_gaps(
    technical_requirements: list[dict],
    resume_experience: dict[str, float] | None,
) -> list[dict]:
    """
    Compare technical experience requirements against
    resume-supported experience.

    Unknown resume experience remains unknown.
    ResumeIQ never invents experience.
    """
    if not technical_requirements:
        return []

    resume_experience = (
        resume_experience or {}
    )

    normalized_resume: dict[str, float] = {}

    for skill, years in resume_experience.items():

        if not skill or years is None:
            continue

        canonical = _canonical_requirement(
            skill
        )

        if not canonical:
            continue

        normalized_resume[canonical] = float(years)

    results: list[dict] = []

    seen: set[str] = set()

    for requirement in technical_requirements:

        skill = _canonical_requirement(
            requirement.get(
                "skill",
                "",
            )
        )

        required_years = requirement.get(
            "required_years"
        )

        if (
            not skill
            or required_years is None
            or skill in seen
        ):
            continue

        seen.add(skill)

        resume_years = normalized_resume.get(
            skill
        )

        if resume_years is None:

            results.append(
                {
                    "skill": skill,
                    "required_years": required_years,
                    "resume_years": None,
                    "gap_years": None,
                    "status": "unknown",
                }
            )

            continue

        gap = max(
            0,
            required_years - resume_years,
        )

        results.append(
            {
                "skill": skill,
                "required_years": required_years,
                "resume_years": resume_years,
                "gap_years": gap,
                "status": (
                    "meets_requirement"
                    if gap == 0
                    else "below_requirement"
                ),
            }
        )

    return results