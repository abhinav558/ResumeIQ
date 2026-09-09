"""
ResumeIQ - ATS Intelligence Engine

Production-ready ATS analysis engine.

Responsibilities:
- Role-aware keyword matching
- Keyword priority classification
- Weighted keyword scoring
- ATS section analysis
- Action verb detection
- Quantified achievement detection
- Resume readability
- Technical context
- Application-serving detection
- Production-deployment detection
- ATS strengths and issues
- ATS recommendations
- Backwards-compatible output

Design principles:
- Never fabricate resume evidence.
- Never treat education percentages/CGPAs as achievement metrics.
- Keep matched/missing keyword lists internally consistent.
- Avoid noisy keyword-stuffing recommendations.
- Preserve backwards-compatible output fields.
- Keep all ATS score components mathematically consistent.
- Treat the central keyword database as authoritative.
- Distinguish application serving from actual production deployment.
"""

from __future__ import annotations

from collections import Counter
import re
from typing import Any, Dict, Iterable, List, Tuple

from .keyword_db import (
    ROLE_PROFILES,
    ROLE_KEYWORD_WEIGHTS,
    ACTION_VERBS,
    ALL_TECHNOLOGIES,
)

from .utils import (
    normalize_text,
    find_keywords,
    extract_metrics,
    unique,
    word_count,
    clamp,
)


# ============================================================
# DEFAULT ROLE
# ============================================================

DEFAULT_ROLE = "machine_learning_engineer"


# ============================================================
# ATS SECTIONS
# ============================================================

# Experience is intentionally optional because ResumeIQ
# supports fresh graduates.
REQUIRED_SECTIONS = [
    "summary",
    "education",
    "skills",
    "projects",
    "certifications",
]

OPTIONAL_SECTIONS = [
    "experience",
]


# ============================================================
# SECTION WEIGHTS
# ============================================================

SECTION_WEIGHT = {
    "summary": 3,
    "education": 3,
    "skills": 5,
    "projects": 6,
    "certifications": 2,
}

SECTION_MAX_SCORE = sum(
    SECTION_WEIGHT.values()
)


# ============================================================
# ATS COMPONENT WEIGHTS
# ============================================================

ATS_WEIGHTS = {
    "keywords": 0.35,
    "sections": 0.20,
    "metrics": 0.15,
    "readability": 0.15,
    "technical": 0.15,
}


# ============================================================
# PRIORITY ORDER
# ============================================================

PRIORITY_ORDER = (
    "critical",
    "high",
    "important",
    "supporting",
    "optional",
)


# ============================================================
# APPLICATION SERVING / DEPLOYMENT
# ============================================================

# These technologies indicate that the candidate built or used
# something capable of serving an application, API, dashboard,
# or web interface.
#
# IMPORTANT:
# Finding one of these technologies alone does NOT mean that the
# application was deployed to production.
APPLICATION_SERVING_TECHNOLOGIES = {
    "flask": "Flask",
    "fastapi": "FastAPI",
    "streamlit": "Streamlit",
    "django": "Django",
    "express": "Express",
    "node.js": "Node.js",
    "node": "Node.js",
    "spring boot": "Spring Boot",
    "gradio": "Gradio",
}


# Cloud/hosting platforms are useful deployment evidence only
# when the resume explicitly connects them to deployment,
# hosting, production, live, publishing, etc.
#
# Mentioning "AWS" in a Skills section must NOT automatically
# become production-deployment evidence.
DEPLOYMENT_PLATFORMS = {
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "Google Cloud",
    "render": "Render",
    "railway": "Railway",
    "heroku": "Heroku",
    "vercel": "Vercel",
    "netlify": "Netlify",
}


# Production/application server technologies provide stronger
# deployment evidence, but they still require meaningful context.
PRODUCTION_SERVER_TECHNOLOGIES = {
    "gunicorn": "Gunicorn",
    "uwsgi": "uWSGI",
    "waitress": "Waitress",
}


# These terms represent explicit deployment/hosting/production
# context. They are intentionally separated from serving
# technologies.
DEPLOYMENT_CONTEXT_TERMS = (
    "deploy",
    "deployed",
    "deployment",
    "host",
    "hosted",
    "hosting",
    "production",
    "live",
    "published",
    "publish",
    "go live",
    "cloud deployment",
    "served in production",
)


# Docker/containerization alone is not production deployment.
# It becomes deployment evidence only when explicit deployment
# context is also present.
CONTAINERIZATION_TERMS = (
    "docker",
    "dockerized",
    "dockerised",
    "containerized",
    "containerised",
)


# Maximum character distance used when determining whether a
# deployment term is actually connected to an application,
# server, platform, or container.
DEPLOYMENT_CONTEXT_WINDOW = 100


# ============================================================
# TECHNICAL TERM FILTERING
# ============================================================

# Some keyword databases intentionally contain broader terms
# that are useful for role matching but are not technologies.
# They should not inflate technology-context scoring.
#
# This list is deliberately conservative. It does not remove
# legitimate technical concepts such as machine learning,
# computer vision, federated learning, or blockchain.
NON_TECHNICAL_TERMS = {
    "communication",
    "communications",
    "adaptability",
    "teamwork",
    "problem solving",
    "problem-solving",
    "leadership",
    "collaboration",
    "time management",
    "critical thinking",
    "creativity",
    "analytical thinking",
    "interpersonal skills",
    "presentation",
    "presentation skills",
    "soft skills",
}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    """
    Safely convert a value into text.
    """

    if isinstance(value, str):
        return value

    if value is None:
        return ""

    try:
        return str(value)
    except Exception:
        return ""


def _safe_list(value: Any) -> List[Any]:
    """
    Safely convert common iterable containers into a list.
    """

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    return []


def _dedupe_strings(
    values: Any,
) -> List[str]:
    """
    Deduplicate string values while preserving order.
    """

    result: List[str] = []
    seen = set()

    for value in _safe_list(values):

        if not isinstance(value, str):
            continue

        cleaned = " ".join(
            value.strip().split()
        )

        if not cleaned:
            continue

        key = cleaned.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(cleaned)

    return result


def _normalize_keyword_key(
    value: Any,
) -> str:
    """
    Normalize a keyword for comparison.

    Matching and weight lookup use this canonical form.
    """

    text = _safe_text(value)

    text = " ".join(
        text.strip().split()
    )

    return text.casefold()


def _iter_keywords(
    value: Any,
) -> List[str]:
    """
    Normalize a keyword collection.

    Supported forms:
    - list
    - tuple
    - set
    - dictionary keys
    - single string
    """

    if isinstance(value, str):
        return _dedupe_strings(
            [value]
        )

    if isinstance(value, dict):
        return _dedupe_strings(
            list(value.keys())
        )

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return _dedupe_strings(
            value
        )

    return []


def _normalize_weight_map(
    value: Any,
) -> Dict[str, int]:
    """
    Normalize a keyword-weight mapping.

    Weight keys are compared case-insensitively so that:

        TensorFlow
        tensorflow
        TENSORFLOW

    all resolve to the same weight.
    """

    if not isinstance(
        value,
        dict,
    ):
        return {}

    result: Dict[str, int] = {}

    for raw_key, raw_weight in value.items():

        key = _normalize_keyword_key(
            raw_key
        )

        if not key:
            continue

        try:
            weight = int(
                raw_weight
            )
        except (
            TypeError,
            ValueError,
        ):
            weight = 1

        result[key] = max(
            1,
            weight,
        )

    return result


def _resolve_role(
    role: Any,
) -> str:
    """
    Resolve an incoming role to a valid role profile.

    Unknown/empty roles safely fall back to DEFAULT_ROLE.
    """

    if not isinstance(
        role,
        str,
    ):
        return DEFAULT_ROLE

    role = role.strip()

    if not role:
        return DEFAULT_ROLE

    if role not in ROLE_PROFILES:
        return DEFAULT_ROLE

    return role


def _safe_sections(
    sections: Any,
) -> Dict[str, Any]:
    """
    Return a safe section mapping.
    """

    if isinstance(
        sections,
        dict,
    ):
        return sections

    return {}


# ============================================================
# DEPLOYMENT HELPERS
# ============================================================

def _normalize_detection_text(
    text: Any,
) -> str:
    """
    Normalize text for deployment-context detection.

    This intentionally keeps punctuation because deployment
    evidence can occur in phrases such as:

        Flask + Gunicorn
        deployed to AWS
        hosted on Render
        Dockerized and deployed
    """

    value = normalize_text(
        _safe_text(text)
    )

    return " ".join(
        value.strip().split()
    )


def _contains_term(
    text: str,
    term: str,
) -> bool:
    """
    Case-insensitive term detection with word boundaries.

    Multi-word terms are matched as phrases.
    """

    text = _normalize_detection_text(
        text
    )

    term = _normalize_detection_text(
        term
    )

    if not text or not term:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(term)
        + r"(?![a-z0-9])"
    )

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def _find_term_spans(
    text: str,
    terms: Iterable[str],
) -> List[Tuple[str, int, int]]:
    """
    Find normalized term spans.

    Returns:
        (canonical_term, start, end)
    """

    normalized_text = _normalize_detection_text(
        text
    )

    results: List[Tuple[str, int, int]] = []

    for term in terms:

        normalized_term = _normalize_detection_text(
            term
        )

        if not normalized_term:
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(normalized_term)
            + r"(?![a-z0-9])"
        )

        for match in re.finditer(
            pattern,
            normalized_text,
            flags=re.IGNORECASE,
        ):
            results.append(
                (
                    term,
                    match.start(),
                    match.end(),
                )
            )

    results.sort(
        key=lambda item: (
            item[1],
            item[2],
            item[0].casefold(),
        )
    )

    return results


def _has_nearby_context(
    text: str,
    start: int,
    end: int,
    context_terms: Iterable[str],
    window: int = DEPLOYMENT_CONTEXT_WINDOW,
) -> str | None:
    """
    Return the first deployment-context term occurring close
    to a target span.

    Context may occur before or after the target.

    Example:

        deployed Flask API to AWS

    can associate:
        Flask <-> deployed
        Flask <-> AWS
        AWS <-> deployed
    """

    normalized_text = _normalize_detection_text(
        text
    )

    left = max(
        0,
        start - window,
    )

    right = min(
        len(normalized_text),
        end + window,
    )

    nearby_text = normalized_text[
        left:right
    ]

    for term in context_terms:

        if _contains_term(
            nearby_text,
            term,
        ):
            return term

    return None


def _find_nearby_application_technology(
    text: str,
    start: int,
    end: int,
    window: int = DEPLOYMENT_CONTEXT_WINDOW,
) -> str | None:
    """
    Find an application-serving technology near a span.
    """

    spans = _find_term_spans(
        text,
        APPLICATION_SERVING_TECHNOLOGIES.keys(),
    )

    for term, term_start, term_end in spans:

        if (
            term_start <= end + window
            and term_end >= start - window
        ):

            return APPLICATION_SERVING_TECHNOLOGIES.get(
                term.casefold(),
                term,
            )

    return None


def _find_nearby_platform(
    text: str,
    start: int,
    end: int,
    window: int = DEPLOYMENT_CONTEXT_WINDOW,
) -> str | None:
    """
    Find a deployment platform near a span.
    """

    spans = _find_term_spans(
        text,
        DEPLOYMENT_PLATFORMS.keys(),
    )

    for term, term_start, term_end in spans:

        if (
            term_start <= end + window
            and term_end >= start - window
        ):

            return DEPLOYMENT_PLATFORMS.get(
                term.casefold(),
                term,
            )

    return None


def analyze_deployment_evidence(
    text: str,
) -> Dict[str, Any]:
    """
    Distinguish application serving from actual production
    deployment evidence.

    Application serving:
        Flask
        FastAPI
        Streamlit
        Django
        Express
        Node.js
        Spring Boot
        Gradio

    Production deployment requires stronger contextual evidence.

    Examples that DO count:

        "Deployed Flask API to AWS"
        "Hosted FastAPI application on Render"
        "Dockerized the service and deployed it to AWS"
        "Flask API served in production using Gunicorn"

    Examples that do NOT count:

        "Flask"
        "FastAPI"
        "Streamlit"
        "AWS"
        "Docker"
        "AWS, Docker, Flask"
        "Built a Flask API"

    The function never infers deployment merely because a
    deployment-capable technology appears.
    """

    normalized_text = _normalize_detection_text(
        text
    )

    if not normalized_text:
        return {
            "application_serving": [],
            "production_deployment": [],
            "has_application_serving": False,
            "has_production_deployment": False,
        }

    # --------------------------------------------------------
    # Application serving
    # --------------------------------------------------------

    serving_spans = _find_term_spans(
        normalized_text,
        APPLICATION_SERVING_TECHNOLOGIES.keys(),
    )

    application_serving: List[str] = []

    for term, _, _ in serving_spans:

        canonical = APPLICATION_SERVING_TECHNOLOGIES.get(
            term.casefold(),
            term,
        )

        application_serving.append(
            canonical
        )

    application_serving = _dedupe_strings(
        application_serving
    )

    # --------------------------------------------------------
    # Production deployment evidence
    # --------------------------------------------------------

    production_evidence: List[str] = []

    # --------------------------------------------------------
    # 1. Explicit deployment context near an application
    #    serving technology.
    #
    # Examples:
    #     "deployed Flask API"
    #     "hosted FastAPI service"
    #     "Streamlit application is live"
    # --------------------------------------------------------

    for term, start, end in serving_spans:

        context = _has_nearby_context(
            normalized_text,
            start,
            end,
            DEPLOYMENT_CONTEXT_TERMS,
        )

        if context:

            canonical = APPLICATION_SERVING_TECHNOLOGIES.get(
                term.casefold(),
                term,
            )

            production_evidence.append(
                f"{canonical} with {context} context"
            )

    # --------------------------------------------------------
    # 2. Explicit deployment context near a deployment
    #    platform.
    #
    # Examples:
    #     "deployed to AWS"
    #     "hosted on Render"
    #
    # Platform alone does NOT count.
    # --------------------------------------------------------

    platform_spans = _find_term_spans(
        normalized_text,
        DEPLOYMENT_PLATFORMS.keys(),
    )

    for term, start, end in platform_spans:

        context = _has_nearby_context(
            normalized_text,
            start,
            end,
            DEPLOYMENT_CONTEXT_TERMS,
        )

        if not context:
            continue

        canonical_platform = DEPLOYMENT_PLATFORMS.get(
            term.casefold(),
            term,
        )

        nearby_app = _find_nearby_application_technology(
            normalized_text,
            start,
            end,
        )

        if nearby_app:

            production_evidence.append(
                f"{nearby_app} deployed/hosted on "
                f"{canonical_platform}"
            )

        else:

            production_evidence.append(
                f"{canonical_platform} with "
                f"{context} context"
            )

    # --------------------------------------------------------
    # 3. Production server technologies.
    #
    # Gunicorn/uWSGI/Waitress alone are not enough.
    #
    # They become strong evidence when:
    #
    #     Flask + Gunicorn
    #     FastAPI + Gunicorn
    #     production using Gunicorn
    #     deployed with Gunicorn
    # --------------------------------------------------------

    server_spans = _find_term_spans(
        normalized_text,
        PRODUCTION_SERVER_TECHNOLOGIES.keys(),
    )

    for term, start, end in server_spans:

        canonical_server = PRODUCTION_SERVER_TECHNOLOGIES.get(
            term.casefold(),
            term,
        )

        nearby_app = _find_nearby_application_technology(
            normalized_text,
            start,
            end,
        )

        context = _has_nearby_context(
            normalized_text,
            start,
            end,
            DEPLOYMENT_CONTEXT_TERMS,
        )

        if nearby_app and context:

            production_evidence.append(
                f"{nearby_app} with {canonical_server}"
            )

        elif context:

            production_evidence.append(
                f"{canonical_server} with "
                f"{context} context"
            )

    # --------------------------------------------------------
    # 4. Containerization + explicit deployment context.
    #
    # Docker alone is deliberately NOT enough.
    #
    # Examples:
    #     "Dockerized and deployed to AWS"
    #     "containerized the application and hosted it"
    # --------------------------------------------------------

    container_spans = _find_term_spans(
        normalized_text,
        CONTAINERIZATION_TERMS,
    )

    for term, start, end in container_spans:

        context = _has_nearby_context(
            normalized_text,
            start,
            end,
            DEPLOYMENT_CONTEXT_TERMS,
        )

        if not context:
            continue

        nearby_app = _find_nearby_application_technology(
            normalized_text,
            start,
            end,
        )

        nearby_platform = _find_nearby_platform(
            normalized_text,
            start,
            end,
        )

        canonical_container = (
            "Docker"
            if term.casefold() == "docker"
            else term.capitalize()
        )

        if nearby_app and nearby_platform:

            production_evidence.append(
                f"{canonical_container} deployed "
                f"{nearby_app} on {nearby_platform}"
            )

        elif nearby_platform:

            production_evidence.append(
                f"{canonical_container} with "
                f"{nearby_platform} deployment"
            )

        elif nearby_app:

            production_evidence.append(
                f"{canonical_container} deployed "
                f"{nearby_app}"
            )

        else:

            production_evidence.append(
                f"{canonical_container} with "
                f"{context} context"
            )

    production_evidence = _dedupe_strings(
        production_evidence
    )

    return {
        "application_serving": application_serving,
        "production_deployment": production_evidence,
        "has_application_serving": bool(
            application_serving
        ),
        "has_production_deployment": bool(
            production_evidence
        ),
    }


# ============================================================
# PRIORITY HELPERS
# ============================================================

def _get_keyword_priority(
    weight: int,
) -> str:
    """
    Convert keyword weight into ATS priority.

    Weight scale:

        5+ -> critical
        4  -> high
        3  -> important
        2  -> supporting
        1  -> optional
    """

    try:
        weight = int(weight)
    except (
        TypeError,
        ValueError,
    ):
        weight = 1

    weight = max(
        1,
        weight,
    )

    if weight >= 5:
        return "critical"

    if weight >= 4:
        return "high"

    if weight >= 3:
        return "important"

    if weight >= 2:
        return "supporting"

    return "optional"


def _empty_priority_groups() -> Dict[str, Dict[str, List[str]]]:
    """
    Create a complete priority structure.
    """

    return {
        priority: {
            "matched": [],
            "missing": [],
        }
        for priority in PRIORITY_ORDER
    }


# ============================================================
# ACTION VERBS
# ============================================================

def detect_action_verbs(
    text: str,
) -> List[str]:
    """
    Detect strong resume action verbs.
    """

    text = normalize_text(
        _safe_text(text)
    )

    return _dedupe_strings(
        find_keywords(
            text,
            ACTION_VERBS,
        )
    )


# ============================================================
# ROLE KEYWORDS
# ============================================================

def get_role_keywords(
    role: str = DEFAULT_ROLE,
) -> List[str]:
    """
    Return keywords relevant to the selected role.

    The central ROLE_PROFILES database is authoritative.

    Supported profile keyword representations:
        - set
        - list
        - tuple
        - dictionary
    """

    role = _resolve_role(
        role
    )

    profile = ROLE_PROFILES.get(
        role,
        {},
    )

    if not isinstance(
        profile,
        dict,
    ):
        return []

    keywords = profile.get(
        "keywords",
        [],
    )

    return _dedupe_strings(
        _iter_keywords(
            keywords
        )
    )


def get_role_keyword_weights(
    role: str = DEFAULT_ROLE,
) -> Dict[str, int]:
    """
    Return normalized keyword weights for a role.

    This is public-facing helper behavior even though it is
    primarily used internally. It ensures keyword weighting
    is consistent throughout the ATS engine.
    """

    role = _resolve_role(
        role
    )

    raw_weights = ROLE_KEYWORD_WEIGHTS.get(
        role,
        {},
    )

    return _normalize_weight_map(
        raw_weights
    )


# ============================================================
# KEYWORD ANALYSIS
# ============================================================

def analyze_keywords(
    text: str,
    role: str = DEFAULT_ROLE,
) -> Dict[str, Any]:
    """
    Analyze role-specific ATS keywords.

    Guarantees:

    - matched and missing are mutually exclusive
    - every role keyword belongs to exactly one group
    - priority groups agree with matched/missing
    - duplicate keywords are removed
    - keyword weights are normalized
    - keyword score is based on authoritative role weights
    """

    text = normalize_text(
        _safe_text(text)
    )

    role = _resolve_role(
        role
    )

    keywords = get_role_keywords(
        role
    )

    weights = get_role_keyword_weights(
        role
    )

    # --------------------------------------------------------
    # Detect matched keywords
    # --------------------------------------------------------

    raw_matched = find_keywords(
        text,
        keywords,
    )

    detected_keys = {
        _normalize_keyword_key(
            keyword
        )
        for keyword in _dedupe_strings(
            raw_matched
        )
    }

    # --------------------------------------------------------
    # Build canonical matched/missing lists from the role
    # keyword inventory.
    # --------------------------------------------------------

    matched: List[str] = []
    missing: List[str] = []

    for keyword in keywords:

        key = _normalize_keyword_key(
            keyword
        )

        if not key:
            continue

        if key in detected_keys:
            matched.append(
                keyword
            )
        else:
            missing.append(
                keyword
            )

    matched = _dedupe_strings(
        matched
    )

    missing = _dedupe_strings(
        missing
    )

    matched_keys = {
        _normalize_keyword_key(
            keyword
        )
        for keyword in matched
    }

    # Final defensive consistency check.
    missing = [
        keyword
        for keyword in missing
        if _normalize_keyword_key(keyword)
        not in matched_keys
    ]

    # --------------------------------------------------------
    # Priority groups and weighted scoring
    # --------------------------------------------------------

    priority_groups = (
        _empty_priority_groups()
    )

    total_weight = 0
    matched_weight = 0

    for keyword in keywords:

        key = _normalize_keyword_key(
            keyword
        )

        if not key:
            continue

        # The normalized weight map prevents accidental
        # fallback to weight 1 caused by casing differences.
        weight = max(
            1,
            weights.get(
                key,
                1,
            ),
        )

        total_weight += weight

        priority = _get_keyword_priority(
            weight
        )

        if key in matched_keys:

            matched_weight += weight

            priority_groups[
                priority
            ]["matched"].append(
                keyword
            )

        else:

            priority_groups[
                priority
            ]["missing"].append(
                keyword
            )

    # Defensive deduplication inside each group.
    for priority in PRIORITY_ORDER:

        priority_groups[
            priority
        ]["matched"] = _dedupe_strings(
            priority_groups[
                priority
            ]["matched"]
        )

        priority_groups[
            priority
        ]["missing"] = _dedupe_strings(
            priority_groups[
                priority
            ]["missing"]
        )

    if total_weight <= 0:

        score = 0.0

    else:

        score = round(
            (
                matched_weight
                / total_weight
            )
            * 100,
            2,
        )

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "priorities": priority_groups,
    }


# ============================================================
# TECHNOLOGY COVERAGE
# ============================================================

def _is_technical_term(
    value: Any,
) -> bool:
    """
    Determine whether a detected term should count as
    technical context.

    The check is intentionally conservative.
    """

    key = _normalize_keyword_key(
        value
    )

    if not key:
        return False

    return key not in NON_TECHNICAL_TERMS


def analyze_technology_coverage(
    text: str,
) -> Dict[str, Any]:
    """
    Analyze technology coverage across ResumeIQ categories.

    Categories can overlap.

    Non-technical soft-skill terms present in a broad central
    technology database are excluded from the technology
    count so that technical-context scoring remains meaningful.
    """

    text = normalize_text(
        _safe_text(text)
    )

    raw_technologies = _dedupe_strings(
        find_keywords(
            text,
            ALL_TECHNOLOGIES,
        )
    )

    technologies = [
        technology
        for technology in raw_technologies
        if _is_technical_term(
            technology
        )
    ]

    categories = Counter()

    ai_ml_keywords = {
        _normalize_keyword_key(item)
        for item in get_role_keywords(
            "machine_learning_engineer"
        )
    }

    software_keywords = {
        _normalize_keyword_key(item)
        for item in get_role_keywords(
            "software_engineer"
        )
    }

    full_stack_keywords = {
        _normalize_keyword_key(item)
        for item in get_role_keywords(
            "full_stack_engineer"
        )
    }

    for technology in technologies:

        key = _normalize_keyword_key(
            technology
        )

        if key in ai_ml_keywords:
            categories["AI/ML"] += 1

        if key in software_keywords:
            categories["Software"] += 1

        if key in full_stack_keywords:
            categories["FullStack"] += 1

    return {
        "technologies": technologies,
        "count": len(technologies),
        "categories": dict(categories),
    }


# ============================================================
# METRICS
# ============================================================

def analyze_metrics(
    text: str,
) -> Dict[str, Any]:
    """
    Backwards-compatible metric analyzer.

    This function analyzes the supplied text only.

    The main ATS pipeline passes project and experience
    sections instead of the complete resume, preventing
    education percentages such as 89% from being counted
    as achievement metrics.
    """

    text = normalize_text(
        _safe_text(text)
    )

    metrics = _dedupe_strings(
        extract_metrics(
            text
        )
    )

    score = clamp(
        len(metrics) * 5,
        0,
        20,
    )

    return {
        "score": score,
        "metrics": metrics,
    }


def analyze_achievement_metrics(
    sections: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Analyze metrics only where professional/project
    achievements are expected.

    Education metrics such as:

        89%
        9.3 CGPA
        8.55 CGPA

    are intentionally excluded.

    Project/experience metrics such as:

        95% accuracy
        30% faster
        5,000 users
        40% reduction

    are eligible only when they actually occur in relevant
    resume sections.
    """

    sections = _safe_sections(
        sections
    )

    achievement_text_parts: List[str] = []

    for section_name in (
        "projects",
        "experience",
        "internship",
        "achievements",
    ):

        value = sections.get(
            section_name,
            "",
        )

        if isinstance(
            value,
            str,
        ) and value.strip():

            achievement_text_parts.append(
                value
            )

    achievement_text = "\n".join(
        achievement_text_parts
    )

    return analyze_metrics(
        achievement_text
    )


# ============================================================
# SECTION QUALITY
# ============================================================

def analyze_section_quality(
    sections: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Score the presence of important resume sections.

    Freshers:
        Experience is NOT required.

    Experienced candidates:
        Experience is detected and reported separately.
    """

    sections = _safe_sections(
        sections
    )

    score = 0

    present: List[str] = []
    missing: List[str] = []

    for section in REQUIRED_SECTIONS:

        value = sections.get(
            section,
            "",
        )

        if (
            isinstance(
                value,
                str,
            )
            and value.strip()
        ):

            score += SECTION_WEIGHT.get(
                section,
                0,
            )

            present.append(
                section
            )

        else:

            missing.append(
                section
            )

    experience_value = sections.get(
        "experience",
        "",
    )

    has_experience = (
        isinstance(
            experience_value,
            str,
        )
        and bool(
            experience_value.strip()
        )
    )

    if has_experience:

        present.append(
            "experience"
        )

    if SECTION_MAX_SCORE <= 0:

        normalized = 0.0

    else:

        normalized = round(
            (
                score
                / SECTION_MAX_SCORE
            )
            * 20,
            2,
        )

    return {
        "score": normalized,
        "present": _dedupe_strings(
            present
        ),
        "missing": _dedupe_strings(
            missing
        ),
        "has_experience": has_experience,
    }


# ============================================================
# READABILITY
# ============================================================

def analyze_readability(
    text: str,
) -> Dict[str, Any]:
    """
    Analyze resume length/readability.
    """

    text = normalize_text(
        _safe_text(text)
    )

    words = word_count(
        text
    )

    comments: List[str] = []

    if words < 150:

        score = 8

        comments.append(
            "Resume is too short."
        )

    elif words <= 700:

        score = 15

        comments.append(
            "Good resume length."
        )

    elif words <= 1000:

        score = 12

        comments.append(
            "Slightly long."
        )

    else:

        score = 6

        comments.append(
            "Resume is excessively long."
        )

    return {
        "score": score,
        "word_count": words,
        "comments": comments,
    }


# ============================================================
# TECHNICAL CONTEXT
# ============================================================

def analyze_technical_context(
    text: str,
) -> Dict[str, Any]:
    """
    Measure technical richness.

    Maximum contribution: 15 points.

    This measures technologies actually detected in the
    resume. It does not infer missing technologies.
    """

    result = analyze_technology_coverage(
        text
    )

    technologies = result.get(
        "technologies",
        [],
    )

    score = clamp(
        len(
            _dedupe_strings(
                technologies
            )
        ),
        0,
        15,
    )

    return {
        "score": score,
        "technologies": _dedupe_strings(
            technologies
        ),
    }


# ============================================================
# OVERALL ATS SCORE
# ============================================================

def compute_ats_score(
    keyword_score: float,
    section_score: float,
    metric_score: float,
    readability_score: float,
    technical_score: float,
) -> float:
    """
    Calculate the final ATS score.

    Component ranges:

        keyword_score     -> 0-100
        section_score     -> 0-20
        metric_score      -> 0-20
        readability_score -> 0-15
        technical_score   -> 0-15

    Final score:

        Keyword coverage  -> 35%
        Section quality   -> 20%
        Metrics           -> 15%
        Readability       -> 15%
        Technical context -> 15%

    Total = 100%.

    The raw non-keyword components are normalized to 0-100
    before applying their weights.
    """

    try:
        keyword_score = float(
            keyword_score
        )
    except (
        TypeError,
        ValueError,
    ):
        keyword_score = 0.0

    try:
        section_score = float(
            section_score
        )
    except (
        TypeError,
        ValueError,
    ):
        section_score = 0.0

    try:
        metric_score = float(
            metric_score
        )
    except (
        TypeError,
        ValueError,
    ):
        metric_score = 0.0

    try:
        readability_score = float(
            readability_score
        )
    except (
        TypeError,
        ValueError,
    ):
        readability_score = 0.0

    try:
        technical_score = float(
            technical_score
        )
    except (
        TypeError,
        ValueError,
    ):
        technical_score = 0.0

    # Normalize each component to a 0-100 scale.
    keyword_normalized = clamp(
        keyword_score,
        0,
        100,
    )

    section_normalized = (
        clamp(
            section_score,
            0,
            20,
        )
        / 20
    ) * 100

    metric_normalized = (
        clamp(
            metric_score,
            0,
            20,
        )
        / 20
    ) * 100

    readability_normalized = (
        clamp(
            readability_score,
            0,
            15,
        )
        / 15
    ) * 100

    technical_normalized = (
        clamp(
            technical_score,
            0,
            15,
        )
        / 15
    ) * 100

    total = (
        keyword_normalized
        * ATS_WEIGHTS["keywords"]
        + section_normalized
        * ATS_WEIGHTS["sections"]
        + metric_normalized
        * ATS_WEIGHTS["metrics"]
        + readability_normalized
        * ATS_WEIGHTS["readability"]
        + technical_normalized
        * ATS_WEIGHTS["technical"]
    )

    return round(
        clamp(
            total,
            0,
            100,
        ),
        2,
    )


# ============================================================
# STRENGTHS
# ============================================================

def generate_strengths(
    keyword_result: Dict[str, Any],
    metric_result: Dict[str, Any],
    readability_result: Dict[str, Any],
    section_result: Dict[str, Any],
) -> List[str]:
    """
    Generate positive ATS observations.
    """

    strengths: List[str] = []

    try:
        keyword_score = float(
            keyword_result.get(
                "score",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        keyword_score = 0.0

    if keyword_score >= 70:

        strengths.append(
            "Strong keyword coverage"
        )

    elif keyword_score >= 50:

        strengths.append(
            "Moderate keyword coverage"
        )

    if metric_result.get(
        "metrics",
        [],
    ):

        strengths.append(
            "Contains measurable project or experience outcomes"
        )

    try:
        readability_score = float(
            readability_result.get(
                "score",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        readability_score = 0.0

    if readability_score >= 15:

        strengths.append(
            "Good resume readability"
        )

    if not section_result.get(
        "missing",
        [],
    ):

        strengths.append(
            "Complete core resume structure"
        )

    present = _dedupe_strings(
        section_result.get(
            "present",
            [],
        )
    )

    if len(present) >= 4:

        strengths.append(
            "Most important resume sections detected"
        )

    return _dedupe_strings(
        strengths
    )


# ============================================================
# ISSUES
# ============================================================

def generate_issues(
    keyword_result: Dict[str, Any],
    section_result: Dict[str, Any],
    readability_result: Dict[str, Any],
) -> List[str]:
    """
    Generate ATS issues.

    Missing professional experience is NOT treated as an ATS
    issue for freshers.
    """

    issues: List[str] = []

    priorities = keyword_result.get(
        "priorities",
        {},
    )

    if not isinstance(
        priorities,
        dict,
    ):
        priorities = {}

    def _priority_missing(
        priority: str,
    ) -> List[str]:

        data = priorities.get(
            priority,
            {},
        )

        if not isinstance(
            data,
            dict,
        ):
            return []

        return _dedupe_strings(
            data.get(
                "missing",
                [],
            )
        )

    critical_missing = _priority_missing(
        "critical"
    )

    high_missing = _priority_missing(
        "high"
    )

    missing_keywords = _dedupe_strings(
        keyword_result.get(
            "missing",
            [],
        )
    )

    if critical_missing:

        issues.append(
            "Missing critical ATS keywords: "
            + ", ".join(
                critical_missing[:6]
            )
        )

    elif high_missing:

        issues.append(
            "Missing high-priority ATS keywords: "
            + ", ".join(
                high_missing[:6]
            )
        )

    elif missing_keywords:

        issues.append(
            "Some role-relevant ATS keywords are missing"
        )

    missing_sections = _dedupe_strings(
        section_result.get(
            "missing",
            [],
        )
    )

    if missing_sections:

        issues.append(
            "Missing sections: "
            + ", ".join(
                missing_sections
            )
        )

    try:
        readability_score = float(
            readability_result.get(
                "score",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        readability_score = 0.0

    if readability_score < 10:

        comments = _dedupe_strings(
            readability_result.get(
                "comments",
                [],
            )
        )

        if comments:

            issues.append(
                comments[0]
            )

    return _dedupe_strings(
        issues
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

def _collect_priority_missing(
    priorities: Dict[str, Any],
    priority: str,
) -> List[str]:
    """
    Safely retrieve missing keywords from a priority group.
    """

    data = priorities.get(
        priority,
        {},
    )

    if not isinstance(
        data,
        dict,
    ):
        return []

    return _dedupe_strings(
        data.get(
            "missing",
            [],
        )
    )


def generate_recommendations(
    keyword_result: Dict[str, Any],
    metric_result: Dict[str, Any],
    section_result: Dict[str, Any],
    technology_result: Dict[str, Any],
) -> List[str]:
    """
    Generate actionable ATS recommendations.

    Rules:

    - Never recommend blindly adding every missing keyword.
    - Critical/high keywords are surfaced first.
    - Recommendations explicitly require genuine evidence.
    - Metrics are recommended only when absent.
    - Freshers are guided toward projects and evidence.
    """

    recommendations: List[str] = []

    priorities = keyword_result.get(
        "priorities",
        {},
    )

    if not isinstance(
        priorities,
        dict,
    ):
        priorities = {}

    critical_missing = (
        _collect_priority_missing(
            priorities,
            "critical",
        )
    )

    high_missing = (
        _collect_priority_missing(
            priorities,
            "high",
        )
    )

    important_missing = (
        _collect_priority_missing(
            priorities,
            "important",
        )
    )

    supporting_missing = (
        _collect_priority_missing(
            priorities,
            "supporting",
        )
    )

    optional_missing = (
        _collect_priority_missing(
            priorities,
            "optional",
        )
    )

    # --------------------------------------------------------
    # Critical keyword guidance
    # --------------------------------------------------------

    if critical_missing:

        recommendations.append(
            "Review the missing critical ATS keywords and "
            "include only those that genuinely match your "
            "skills or project experience: "
            + ", ".join(
                critical_missing[:5]
            )
        )

    # --------------------------------------------------------
    # High-priority keyword guidance
    # --------------------------------------------------------

    if high_missing:

        recommendations.append(
            "Strengthen high-priority role keywords where "
            "you can provide real evidence through your "
            "projects, skills, coursework, or experience: "
            + ", ".join(
                high_missing[:5]
            )
        )

    # --------------------------------------------------------
    # Important keyword guidance
    # --------------------------------------------------------

    if (
        not critical_missing
        and not high_missing
        and important_missing
    ):

        recommendations.append(
            "Consider relevant role keywords such as "
            + ", ".join(
                important_missing[:4]
            )
            + " only when you can support them with genuine "
            "skills, projects, coursework, or experience."
        )

    # --------------------------------------------------------
    # Metrics / measurable outcomes
    # --------------------------------------------------------

    metrics = _dedupe_strings(
        metric_result.get(
            "metrics",
            [],
        )
    )

    if not metrics:

        recommendations.append(
            "Add measurable project outcomes such as "
            "verified accuracy, performance improvement, "
            "dataset size, processing-time reduction, "
            "or deployment scale when you have real results."
        )

    # --------------------------------------------------------
    # Project structure
    # --------------------------------------------------------

    missing_sections = _dedupe_strings(
        section_result.get(
            "missing",
            [],
        )
    )

    if "projects" in missing_sections:

        recommendations.append(
            "Add 2-3 strong technical projects with "
            "technologies, implementation details, "
            "deployment information, and verified results."
        )

    # --------------------------------------------------------
    # Technical coverage
    # --------------------------------------------------------

    try:
        technology_count = int(
            technology_result.get(
                "count",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        technology_count = 0

    if technology_count < 8:

        recommendations.append(
            "Expand your technical stack with relevant "
            "tools, frameworks, databases, cloud platforms, "
            "or engineering practices that you can genuinely "
            "demonstrate."
        )

    # --------------------------------------------------------
    # Fresher-specific guidance
    # --------------------------------------------------------

    if not section_result.get(
        "has_experience",
        False,
    ):

        recommendations.append(
            "As a fresher, strengthen projects, GitHub work, "
            "certifications, and measurable technical "
            "achievements instead of adding unsupported "
            "professional experience."
        )

    # --------------------------------------------------------
    # Avoid noisy recommendations for low-priority gaps.
    #
    # Supporting/optional keywords remain available through
    # the structured priority output, but are not dumped into
    # recommendations.
    # --------------------------------------------------------

    _ = supporting_missing
    _ = optional_missing

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append(
            "Maintain strong keyword alignment and continue "
            "adding measurable engineering achievements."
        )

    return _dedupe_strings(
        recommendations
    )


# ============================================================
# SCORE BREAKDOWN
# ============================================================

def _build_score_breakdown(
    keyword_score: float,
    section_score: float,
    metric_score: float,
    readability_score: float,
    technical_score: float,
) -> Dict[str, Any]:
    """
    Build a score breakdown whose contribution values sum to
    the final ATS score.

    This keeps raw component scores separate from weighted
    contributions.
    """

    keyword_contribution = round(
        clamp(
            float(keyword_score),
            0,
            100,
        )
        * ATS_WEIGHTS["keywords"],
        2,
    )

    section_contribution = round(
        (
            clamp(
                float(section_score),
                0,
                20,
            )
            / 20
        )
        * 100
        * ATS_WEIGHTS["sections"],
        2,
    )

    metric_contribution = round(
        (
            clamp(
                float(metric_score),
                0,
                20,
            )
            / 20
        )
        * 100
        * ATS_WEIGHTS["metrics"],
        2,
    )

    readability_contribution = round(
        (
            clamp(
                float(readability_score),
                0,
                15,
            )
            / 15
        )
        * 100
        * ATS_WEIGHTS["readability"],
        2,
    )

    technical_contribution = round(
        (
            clamp(
                float(technical_score),
                0,
                15,
            )
            / 15
        )
        * 100
        * ATS_WEIGHTS["technical"],
        2,
    )

    contributions = [
        keyword_contribution,
        section_contribution,
        metric_contribution,
        readability_contribution,
        technical_contribution,
    ]

    contribution_total = round(
        sum(contributions),
        2,
    )

    return {
        "keyword_strength": keyword_contribution,
        "section_quality": section_contribution,
        "impact_score": metric_contribution,
        "readability": readability_contribution,
        "technical_context": technical_contribution,

        "raw_scores": {
            "keyword_score": round(
                clamp(
                    float(keyword_score),
                    0,
                    100,
                ),
                2,
            ),
            "section_score": round(
                clamp(
                    float(section_score),
                    0,
                    20,
                ),
                2,
            ),
            "metric_score": round(
                clamp(
                    float(metric_score),
                    0,
                    20,
                ),
                2,
            ),
            "readability_score": round(
                clamp(
                    float(readability_score),
                    0,
                    15,
                ),
                2,
            ),
            "technical_score": round(
                clamp(
                    float(technical_score),
                    0,
                    15,
                ),
                2,
            ),
        },

        "weights": {
            "keywords": 35,
            "sections": 20,
            "metrics": 15,
            "readability": 15,
            "technical": 15,
        },

        "contribution_total": contribution_total,
    }


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_ats(
    text: str,
    sections: Dict[str, Any] | None = None,
    role: str = DEFAULT_ROLE,
) -> Dict[str, Any]:
    """
    Production-ready ATS analysis.

    Output intentionally contains both:

        keyword_analysis

    and legacy top-level fields such as:

        matched_keywords
        missing_keywords
        action_verbs_found
        metrics_found

    This keeps the frontend and existing tests compatible.
    """

    text = normalize_text(
        _safe_text(text)
    )

    role = _resolve_role(
        role
    )

    sections = _safe_sections(
        sections
    )

    # --------------------------------------------------------
    # Core analyses
    # --------------------------------------------------------

    keyword_result = analyze_keywords(
        text,
        role,
    )

    technology_result = analyze_technology_coverage(
        text
    )

    # Only project/experience/achievement sections are used
    # for measurable achievement detection.
    metric_result = analyze_achievement_metrics(
        sections
    )

    section_result = analyze_section_quality(
        sections
    )

    readability_result = analyze_readability(
        text
    )

    technical_result = analyze_technical_context(
        text
    )

    verbs = detect_action_verbs(
        text
    )

    # --------------------------------------------------------
    # Deployment intelligence
    #
    # This is deliberately NOT included in the ATS score.
    # It is evidence intelligence used by downstream ResumeIQ
    # analysis and recommendations.
    # --------------------------------------------------------

    deployment_result = analyze_deployment_evidence(
        text
    )

    # --------------------------------------------------------
    # Final ATS score
    # --------------------------------------------------------

    ats_score = compute_ats_score(
        keyword_result["score"],
        section_result["score"],
        metric_result["score"],
        readability_result["score"],
        technical_result["score"],
    )

    # --------------------------------------------------------
    # Text intelligence
    # --------------------------------------------------------

    strengths = generate_strengths(
        keyword_result,
        metric_result,
        readability_result,
        section_result,
    )

    issues = generate_issues(
        keyword_result,
        section_result,
        readability_result,
    )

    recommendations = generate_recommendations(
        keyword_result,
        metric_result,
        section_result,
        technology_result,
    )

    # --------------------------------------------------------
    # Weighted analysis breakdown
    # --------------------------------------------------------

    analysis_breakdown = _build_score_breakdown(
        keyword_result["score"],
        section_result["score"],
        metric_result["score"],
        readability_result["score"],
        technical_result["score"],
    )

    # --------------------------------------------------------
    # Defensive score consistency
    #
    # The displayed contribution total and final ATS score
    # should differ by no more than rounding tolerance.
    # --------------------------------------------------------

    analysis_breakdown[
        "score_consistent"
    ] = (
        abs(
            float(
                analysis_breakdown[
                    "contribution_total"
                ]
            )
            - float(
                ats_score
            )
        )
        <= 0.02
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    return {
        # ----------------------------------------------------
        # Main score
        # ----------------------------------------------------

        "ats_score": ats_score,

        # ----------------------------------------------------
        # New structured keyword intelligence
        # ----------------------------------------------------

        "keyword_analysis": {
            "score": keyword_result["score"],
            "matched": keyword_result["matched"],
            "missing": keyword_result["missing"],
            "priorities": keyword_result["priorities"],
        },

        # ----------------------------------------------------
        # Backwards-compatible fields
        # ----------------------------------------------------

        "matched_keywords": keyword_result[
            "matched"
        ],

        "missing_keywords": keyword_result[
            "missing"
        ],

        "action_verbs_found": verbs,

        "metrics_found": metric_result[
            "metrics"
        ],

        "word_count": readability_result[
            "word_count"
        ],

        # ----------------------------------------------------
        # Detailed analysis
        # ----------------------------------------------------

        "analysis": analysis_breakdown,

        "strengths": strengths,

        "issues": issues,

        "recommendations": recommendations,

        "technology_coverage": technology_result,

        # ----------------------------------------------------
        # Deployment intelligence
        #
        # This does not affect ats_score. It provides a
        # conservative distinction between:
        #
        #   application serving
        #
        # and:
        #
        #   actual production deployment
        # ----------------------------------------------------

        "deployment_analysis": deployment_result,

        "section_analysis": {
            "present": section_result[
                "present"
            ],
            "missing": section_result[
                "missing"
            ],
            "score": section_result[
                "score"
            ],
            "has_experience": section_result[
                "has_experience"
            ],
        },
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "DEFAULT_ROLE",
    "REQUIRED_SECTIONS",
    "OPTIONAL_SECTIONS",
    "SECTION_WEIGHT",
    "ATS_WEIGHTS",
    "APPLICATION_SERVING_TECHNOLOGIES",
    "DEPLOYMENT_PLATFORMS",
    "PRODUCTION_SERVER_TECHNOLOGIES",
    "detect_action_verbs",
    "get_role_keywords",
    "get_role_keyword_weights",
    "analyze_keywords",
    "analyze_technology_coverage",
    "analyze_metrics",
    "analyze_achievement_metrics",
    "analyze_section_quality",
    "analyze_readability",
    "analyze_technical_context",
    "analyze_deployment_evidence",
    "compute_ats_score",
    "generate_strengths",
    "generate_issues",
    "generate_recommendations",
    "analyze_ats",
]