"""
ResumeIQ - Production Project Intelligence Engine

Responsibilities
----------------
1. Detect real academic/professional projects.
2. Prevent technology names from becoming projects.
3. Detect project technologies.
4. Analyze technical complexity.
5. Analyze project impact.
6. Detect meaningful metrics.
7. Detect deployment approaches.
8. Detect engineering practices.
9. Produce deterministic project scores.
10. Produce stable aggregate project analysis.
11. Prevent duplicate/fragmented project detection.

Design goals
------------
- Deterministic
- Defensive
- No external dependencies
- Safe for malformed resume text
- Compatible with ResumeIQ analyzer
- Suitable for unit testing
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set


# ============================================================================
# TECHNOLOGIES
# ============================================================================

TECHNOLOGIES: Sequence[str] = (
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "react",
    "node",
    "nodejs",
    "flask",
    "fastapi",
    "django",
    "tensorflow",
    "keras",
    "pytorch",
    "opencv",
    "scikit-learn",
    "numpy",
    "pandas",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "docker",
    "aws",
    "azure",
    "gcp",
    "streamlit",
    "blockchain",
    "federated learning",
    "git",
    "github",
)


# ============================================================================
# COMPLEXITY KEYWORDS
# ============================================================================

COMPLEXITY_KEYWORDS: Sequence[str] = (
    "machine learning",
    "deep learning",
    "neural network",
    "cnn",
    "transformer",
    "llm",
    "blockchain",
    "federated learning",
    "computer vision",
    "natural language processing",
    "nlp",
    "prediction",
    "predict",
    "classification",
    "classify",
    "forecasting",
    "forecast",
    "recommendation",
    "recommend",
    "optimization",
    "optimize",
    "automation",
)


# ============================================================================
# IMPACT KEYWORDS
# ============================================================================

IMPACT_KEYWORDS: Sequence[str] = (
    "developed",
    "built",
    "designed",
    "implemented",
    "created",
    "optimized",
    "improved",
    "reduced",
    "increased",
    "achieved",
    "trained",
    "integrated",
    "deployed",
)


# ============================================================================
# DEPLOYMENT KEYWORDS
# ============================================================================

DEPLOYMENT_KEYWORDS: Sequence[str] = (
    "rest api",
    "restful api",
    "api",
    "deployment",
    "deployed",
    "docker",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "streamlit",
    "flask",
    "fastapi",
)


# ============================================================================
# ENGINEERING KEYWORDS
# ============================================================================

ENGINEERING_KEYWORDS: Sequence[str] = (
    "github",
    "git",
    "version control",
    "testing",
    "unit test",
    "unit testing",
    "integration test",
    "integration testing",
    "debugging",
    "documentation",
    "ci/cd",
    "continuous integration",
    "continuous deployment",
)


# ============================================================================
# INVALID PROJECT TITLES
# ============================================================================

INVALID_PROJECT_TITLES: Set[str] = {
    # Programming languages
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",

    # Frameworks / libraries
    "react",
    "node",
    "nodejs",
    "tensorflow",
    "keras",
    "pytorch",
    "opencv",
    "scikit-learn",
    "numpy",
    "pandas",
    "flask",
    "fastapi",
    "django",

    # Databases / infrastructure
    "aws",
    "azure",
    "gcp",
    "docker",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    # Tools
    "git",
    "github",

    # AI / technical concepts
    "blockchain",
    "federated learning",
    "machine learning",
    "deep learning",

    # Section / category headings
    "technologies",
    "technology",
    "skills",
    "skill",
    "tools",
    "tool",
    "programming",
    "languages",
    "language",
    "frameworks",
    "framework",
    "libraries",
    "library",
    "technical skills",
    "technical skill",

    # Generic project-like words
    "prediction",
    "classification",
    "forecasting",
    "development",
    "experience",
}


# ============================================================================
# PROJECT TITLE KEYWORDS
# ============================================================================

PROJECT_TITLE_WORDS: Sequence[str] = (
    "system",
    "application",
    "platform",
    "portal",
    "website",
    "web app",
    "web application",
    "mobile app",
    "prediction",
    "predictor",
    "detection",
    "recognition",
    "classification",
    "management",
    "analysis",
    "analyzer",
    "model",
    "engine",
    "recommendation",
    "recommender",
    "dashboard",
    "automation",
    "monitoring",
    "forecast",
    "forecasting",
)


# ============================================================================
# PROJECT SECTION HEADINGS
# ============================================================================

PROJECT_SECTION_HEADINGS: Set[str] = {
    "projects",
    "project",
    "academic projects",
    "academic project",
    "personal projects",
    "personal project",
    "key projects",
    "selected projects",
    "major projects",
}


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _normalize(value: Any) -> str:
    """
    Convert arbitrary input into normalized lowercase text.
    """

    if value is None:
        return ""

    if not isinstance(value, str):
        value = str(value)

    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")

    value = value.lower()

    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )

    value = re.sub(
        r"\n{3,}",
        "\n\n",
        value,
    )

    return value.strip()


def clean_text(text: Any) -> str:
    """
    Normalize text for analysis.
    """

    normalized = _normalize(text)

    if not normalized:
        return ""

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def _contains_term(
    text: str,
    term: str,
) -> bool:
    """
    Boundary-aware keyword matching.

    Prevents false matches such as:

        java       -> does not match javascript
        git        -> does not match github

    while supporting:

        flask.
        (flask)
        python,
        scikit-learn
        c++
    """

    if not text or not term:
        return False

    normalized_text = str(text).casefold()
    normalized_term = str(term).casefold().strip()

    if not normalized_term:
        return False

    escaped_term = re.escape(
        normalized_term
    )

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{escaped_term}"
        rf"(?![a-z0-9])"
    )

    return re.search(
        pattern,
        normalized_text,
    ) is not None


def _unique_preserve_order(
    items: Iterable[str],
) -> List[str]:
    """
    Remove duplicates while preserving deterministic order.
    """

    seen: Set[str] = set()
    result: List[str] = []

    for item in items:
        normalized = str(item).strip().lower()

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


def _is_bullet(
    line: str,
) -> bool:
    """
    Detect common resume bullet prefixes.
    """

    return bool(
        re.match(
            r"^\s*(?:[-•●▪◦*‣►➢]|\d+[.)])\s+",
            line,
        )
    )


def _strip_bullet(
    line: str,
) -> str:
    """
    Remove a resume bullet marker.
    """

    return re.sub(
        r"^\s*(?:[-•●▪◦*‣►➢]|\d+[.)])\s+",
        "",
        line,
    ).strip()


def _looks_like_year_only(
    text: str,
) -> bool:
    """
    Detect standalone four-digit years.
    """

    return bool(
        re.fullmatch(
            r"(?:19|20)\d{2}",
            text.strip(),
        )
    )


def _tokenize_project(
    text: str,
) -> Set[str]:
    """
    Create a normalized token set for duplicate detection.
    """

    normalized = clean_text(text)

    if not normalized:
        return set()

    tokens = re.findall(
        r"[a-z0-9]+",
        normalized,
    )

    return set(tokens)


def _project_similarity(
    first: str,
    second: str,
) -> float:
    """
    Calculate Jaccard similarity between two project blocks.

    Used only for detecting accidental fragmentation.
    It does NOT determine project quality.
    """

    first_tokens = _tokenize_project(
        first
    )

    second_tokens = _tokenize_project(
        second
    )

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = len(
        first_tokens & second_tokens
    )

    union = len(
        first_tokens | second_tokens
    )

    if union == 0:
        return 0.0

    return intersection / union


def _is_subset_project(
    first: str,
    second: str,
) -> bool:
    """
    Determine whether one project block is essentially contained
    inside another.
    """

    first_tokens = _tokenize_project(
        first
    )

    second_tokens = _tokenize_project(
        second
    )

    if not first_tokens or not second_tokens:
        return False

    smaller = min(
        len(first_tokens),
        len(second_tokens),
    )

    if smaller < 3:
        return False

    intersection = len(
        first_tokens & second_tokens
    )

    return (
        intersection / smaller
    ) >= 0.80
# ============================================================================
# TECHNOLOGY DETECTION
# ============================================================================

def detect_technologies(
    text: Any,
) -> List[str]:
    """
    Detect technologies using boundary-aware matching.
    """

    normalized = clean_text(text)

    if not normalized:
        return []

    found: List[str] = []

    for technology in sorted(
        TECHNOLOGIES,
        key=lambda item: (-len(item), item),
    ):
        if _contains_term(
            normalized,
            technology,
        ):
            found.append(technology)

    return _unique_preserve_order(
        found
    )
# ============================================================================
# COMPLEXITY ANALYSIS
# ============================================================================

def calculate_complexity(
    text: Any,
) -> Dict[str, Any]:
    """
    Analyze technical complexity.

    Maximum score: 25.

    Related words such as:
        predict / prediction
        classify / classification
        forecast / forecasting
        recommend / recommendation

    are treated as one technical concept.
    """

    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "features": [],
        }

    # -------------------------------------------------------------------------
    # Related keywords are grouped into one concept.
    # -------------------------------------------------------------------------

    complexity_concepts = (
        (
            "machine learning",
            ("machine learning",),
        ),
        (
            "deep learning",
            ("deep learning",),
        ),
        (
            "neural network",
            ("neural network",),
        ),
        (
            "cnn",
            ("cnn",),
        ),
        (
            "transformer",
            ("transformer",),
        ),
        (
            "llm",
            ("llm",),
        ),
        (
            "blockchain",
            ("blockchain",),
        ),
        (
            "federated learning",
            ("federated learning",),
        ),
        (
            "computer vision",
            ("computer vision",),
        ),
        (
            "natural language processing",
            (
                "natural language processing",
                "nlp",
            ),
        ),
        (
            "prediction",
            (
                "predict",
                "prediction",
                "predicted",
                "predicting",
            ),
        ),
        (
            "classification",
            (
                "classify",
                "classification",
                "classified",
                "classifying",
            ),
        ),
        (
            "forecasting",
            (
                "forecast",
                "forecasting",
                "forecasted",
            ),
        ),
        (
            "recommendation",
            (
                "recommend",
                "recommendation",
                "recommended",
                "recommender",
            ),
        ),
        (
            "optimization",
            (
                "optimize",
                "optimized",
                "optimization",
                "optimizing",
            ),
        ),
        (
            "automation",
            (
                "automate",
                "automated",
                "automation",
                "automating",
            ),
        ),
    )

    features: List[str] = []

    for concept, keywords in complexity_concepts:

        for keyword in keywords:

            if _contains_term(
                normalized,
                keyword,
            ):
                features.append(concept)
                break

    features = _unique_preserve_order(
        features
    )

    # -------------------------------------------------------------------------
    # Base complexity score.
    # -------------------------------------------------------------------------

    score = min(
        len(features) * 5,
        25,
    )

    # -------------------------------------------------------------------------
    # Advanced technical combinations.
    # -------------------------------------------------------------------------

    advanced_combinations = (
        (
            "machine learning",
            "prediction",
        ),
        (
            "deep learning",
            "neural network",
        ),
        (
            "neural network",
            "cnn",
        ),
        (
            "computer vision",
            "cnn",
        ),
        (
            "federated learning",
            "blockchain",
        ),
        (
            "federated learning",
            "prediction",
        ),
        (
            "deep learning",
            "classification",
        ),
        (
            "transformer",
            "llm",
        ),
        (
            "natural language processing",
            "classification",
        ),
    )

    combination_bonus = 0

    for first, second in advanced_combinations:

        if (
            first in features
            and second in features
        ):
            combination_bonus += 3

    score = min(
        score + combination_bonus,
        25,
    )

    return {
        "score": score,
        "features": features,
    }

# ============================================================================
# IMPACT ANALYSIS
# ============================================================================

def calculate_impact(
    text: Any,
) -> Dict[str, Any]:
    """
    Analyze project impact and engineering action language.

    Maximum score: 20.

    Stronger implementation verbs receive more credit than
    generic activity words.
    """

    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "keywords": [],
        }

    keywords: List[str] = []

    # Strong implementation / engineering verbs.
    strong_keywords = (
        "implemented",
        "optimized",
        "automated",
        "integrated",
        "deployed",
        "reduced",
        "increased",
        "improved",
        "achieved",
    )

    # Standard project-development verbs.
    standard_keywords = (
        "developed",
        "built",
        "designed",
        "created",
        "trained",
    )

    for keyword in strong_keywords:
        if _contains_term(
            normalized,
            keyword,
        ):
            keywords.append(keyword)

    for keyword in standard_keywords:
        if _contains_term(
            normalized,
            keyword,
        ):
            keywords.append(keyword)

    keywords = _unique_preserve_order(
        keywords
    )

    # -------------------------------------------------------------------------
    # Score stronger engineering actions more heavily.
    # -------------------------------------------------------------------------

    score = 0

    for keyword in keywords:

        if keyword in strong_keywords:
            score += 3
        else:
            score += 2

    score = min(
        score,
        20,
    )

    return {
        "score": score,
        "keywords": keywords,
    }


# ============================================================================
# METRICS
# ============================================================================

_METRIC_PATTERNS: Sequence[str] = (
    # Percentages
    r"(?<![\d.])\d+(?:\.\d+)?\s*%",

    # Plus counts
    r"(?<![\d.])\d+(?:,\d{3})*\+",

    # Explicit counts
    r"(?<![\d.])\d+(?:,\d{3})*\s+"
    r"(?:users?|records?|images?|samples?|datasets?|"
    r"transactions?|requests?|downloads?|customers?|"
    r"products?|documents?|rows?|entries?|"
    r"predictions?|vehicles?|employees?)\b",
)


_PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d[\d\s().-]{7,}\d)"
    r"(?!\d)"
)


def _is_valid_metric(
    raw_metric: str,
) -> bool:
    """
    Filter values that are unlikely to represent
    meaningful project impact.
    """

    metric = raw_metric.strip().lower()

    if not metric:
        return False

    digits_only = re.sub(
        r"\D",
        "",
        metric,
    )

    if not digits_only:
        return False

    # ------------------------------------------------------------
    # Phone-number protection.
    # ------------------------------------------------------------

    if (
        len(digits_only) >= 10
        and "%" not in metric
    ):
        return False

    # ------------------------------------------------------------
    # Standalone year protection.
    # ------------------------------------------------------------

    if re.fullmatch(
        r"(?:19|20)\d{2}",
        metric,
    ):
        return False

    # ------------------------------------------------------------
    # Four-digit values without meaningful units
    # are usually years.
    # ------------------------------------------------------------

    if (
        len(digits_only) == 4
        and "%" not in metric
        and "+" not in metric
        and not re.search(
            r"\b(?:users?|records?|images?|samples?|datasets?)\b",
            metric,
        )
    ):
        return False

    return True


def calculate_metrics(
    text: Any,
) -> Dict[str, Any]:
    """
    Detect meaningful measurable results.

    Maximum score: 20.
    """

    normalized = clean_text(text)

    if not normalized:
        return {
            "metrics_found": [],
            "score": 0,
        }

    metrics: List[str] = []

    for pattern in _METRIC_PATTERNS:

        for match in re.findall(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        ):

            if isinstance(match, tuple):
                match = " ".join(match)

            metric = str(match).strip()

            if _is_valid_metric(metric):
                metrics.append(metric)

    # ------------------------------------------------------------
    # Detect possible phone numbers separately.
    # ------------------------------------------------------------

    phone_ranges = [
        match.group(0)
        for match in _PHONE_PATTERN.finditer(
            normalized
        )
    ]

    filtered: List[str] = []

    for metric in metrics:

        if any(
            metric in phone
            for phone in phone_ranges
        ):
            continue

        filtered.append(metric)

    metrics = _unique_preserve_order(
        filtered
    )

    score = min(
        len(metrics) * 10,
        20,
    )

    return {
        "metrics_found": metrics,
        "score": score,
    }


# ============================================================================
# DEPLOYMENT ANALYSIS
# ============================================================================

def calculate_deployment(
    text: Any,
) -> Dict[str, Any]:
    """
    Detect deployment and integration technologies.

    Maximum score: 10.
    """

    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "features": [],
        }

    features: List[str] = []

    for keyword in DEPLOYMENT_KEYWORDS:

        if _contains_term(
            normalized,
            keyword,
        ):
            features.append(keyword)

    features = _unique_preserve_order(
        features
    )

    score = min(
        len(features) * 3,
        10,
    )

    return {
        "score": score,
        "features": features,
    }


# ============================================================================
# ENGINEERING ANALYSIS
# ============================================================================

def calculate_engineering(
    text: Any,
) -> Dict[str, Any]:
    """
    Detect engineering practices.

    Maximum score: 10.
    """

    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "features": [],
        }

    features: List[str] = []

    for keyword in ENGINEERING_KEYWORDS:

        if _contains_term(
            normalized,
            keyword,
        ):
            features.append(keyword)

    features = _unique_preserve_order(
        features
    )

    score = min(
        len(features) * 2,
        10,
    )

    return {
        "score": score,
        "features": features,
    }


# ============================================================================
# PROJECT TITLE DETECTION
# ============================================================================

def is_project_title(
    line: Any,
) -> bool:
    """
    Determine whether a resume line is likely
    to be a project title.

    The detector is intentionally conservative.

    A false project is worse than failing to detect
    an ambiguous project title because false projects
    distort the project count and average score.
    """

    if line is None:
        return False

    raw = str(line).strip()

    if not raw:
        return False

    # ------------------------------------------------------------
    # Bullets are descriptions, not headings.
    # ------------------------------------------------------------

    if _is_bullet(raw):
        return False

    cleaned = clean_text(
        _strip_bullet(raw)
    )

    if not cleaned:
        return False

    # ------------------------------------------------------------
    # Section headings.
    # ------------------------------------------------------------

    if cleaned in PROJECT_SECTION_HEADINGS:
        return False

    # ------------------------------------------------------------
    # Length restrictions.
    # ------------------------------------------------------------

    if len(cleaned) < 5:
        return False

    if len(cleaned) > 100:
        return False

    # ------------------------------------------------------------
    # Standalone year.
    # ------------------------------------------------------------

    if _looks_like_year_only(cleaned):
        return False

    # ------------------------------------------------------------
    # Invalid project titles.
    # ------------------------------------------------------------

    if cleaned in INVALID_PROJECT_TITLES:
        return False

    # ------------------------------------------------------------
    # Phone number.
    # ------------------------------------------------------------

    if _PHONE_PATTERN.search(cleaned):
        return False

    words = cleaned.split()

    # ------------------------------------------------------------
    # Sentence-like lines are descriptions.
    # ------------------------------------------------------------

    if len(words) > 10:
        return False

    if cleaned.endswith(
        (".", ";", ":")
    ):
        return False

    # ------------------------------------------------------------
    # Strong project-title vocabulary.
    # ------------------------------------------------------------

    for keyword in PROJECT_TITLE_WORDS:

        if _contains_term(
            cleaned,
            keyword,
        ):
            return True

    # ------------------------------------------------------------
    # Conservative title-style fallback.
    # ------------------------------------------------------------

    if 2 <= len(words) <= 6:

        action_words = {
            "developed",
            "built",
            "created",
            "implemented",
            "designed",
            "trained",
            "worked",
            "used",
            "using",
            "integrated",
            "achieved",
            "improved",
            "optimized",
            "deployed",
            "develop",
            "build",
            "create",
            "implement",
            "design",
            "train",
        }

        if words[0] in action_words:
            return False

        # --------------------------------------------------------
        # Count technologies in the title.
        # --------------------------------------------------------

        technology_count = sum(
            1
            for technology in TECHNOLOGIES
            if _contains_term(
                cleaned,
                technology,
            )
        )

        # A title consisting almost entirely
        # of technology names is not a project.
        if (
            technology_count >= len(words)
            and len(words) <= 3
        ):
            return False

        # --------------------------------------------------------
        # Require title-like capitalization.
        # --------------------------------------------------------

        original_words = raw.split()

        capitalized_count = sum(
            1
            for word in original_words
            if word
            and word[0].isupper()
        )

        if (
            capitalized_count >= 2
            or raw.isupper()
        ):
            return True

    return False


# ============================================================================
# DESCRIPTION DETECTION
# ============================================================================

def _is_description_line(
    line: str,
) -> bool:
    """
    Determine whether a line is clearly descriptive
    rather than a title.
    """

    cleaned = clean_text(
        _strip_bullet(line)
    )

    if not cleaned:
        return False

    words = cleaned.split()

    action_words = {
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "trained",
        "used",
        "using",
        "integrated",
        "achieved",
        "improved",
        "optimized",
        "deployed",
        "worked",
        "responsible",
        "develop",
        "build",
        "create",
        "implement",
        "design",
        "train",
    }

    if words and words[0] in action_words:
        return True

    if _is_bullet(line):
        return True

    if re.search(
        r"\b(?:using|with|through|for|by)\b",
        cleaned,
    ):
        return True

    return False
# ============================================================================
# PROJECT BLOCK MERGING
# ============================================================================

def _merge_fragmented_projects(
    projects: List[str],
) -> List[str]:
    """
    Merge project blocks that are actually fragments
    of the same project.

    This protects against PDF/text extraction producing:

        Project A
        technologies...
        Project A
        description...

    or:

        Project A
        short project title variation
        description...
    """

    if len(projects) <= 1:
        return projects

    merged: List[str] = []

    for project in projects:

        if not merged:
            merged.append(project)
            continue

        previous = merged[-1]

        similarity = _project_similarity(
            previous,
            project,
        )

        subset = (
            _is_subset_project(
                previous,
                project,
            )
            or _is_subset_project(
                project,
                previous,
            )
        )

        # ------------------------------------------------------------
        # Strong overlap = same project.
        # ------------------------------------------------------------

        if (
            similarity >= 0.55
            or subset
        ):
            merged[-1] = (
                previous.strip()
                + " "
                + project.strip()
            ).strip()

            continue

        merged.append(project)

    return merged


# ============================================================================
# PROJECT SPLITTING
# ============================================================================

def split_projects(
    text: Any,
) -> List[str]:
    """
    Split a Projects section into real project blocks.

    Project metadata such as:

        Technologies:
        Tech Stack:
        Tools:
        Technologies Used:

    belongs to the current project.

    The function also performs a second pass
    to merge accidental fragmentation caused
    by PDF extraction.
    """

    if text is None:
        return []

    raw_text = str(text)

    if not raw_text.strip():
        return []

    lines = (
        raw_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )

    metadata_prefixes = (
        "technologies:",
        "technology:",
        "tech stack:",
        "techstack:",
        "technologies used:",
        "tools:",
        "tools used:",
        "built with:",
        "developed using:",
    )

    projects: List[str] = []

    current: List[str] = []

    def flush_current() -> None:
        """
        Save the current project block if it contains
        enough meaningful text.
        """

        if not current:
            return

        project = " ".join(
            item.strip()
            for item in current
            if item.strip()
        ).strip()

        cleaned_project = clean_text(
            project
        )

        # Ignore tiny fragments.
        if len(cleaned_project) >= 30:
            projects.append(project)

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        normalized_line = clean_text(
            _strip_bullet(line)
        )

        # ------------------------------------------------------------
        # Metadata always belongs to current project.
        # ------------------------------------------------------------

        if normalized_line.startswith(
            metadata_prefixes
        ):

            if current:
                current.append(
                    _strip_bullet(line)
                )

            continue

        # ------------------------------------------------------------
        # A real project title starts a new project.
        # ------------------------------------------------------------

        if is_project_title(line):

            flush_current()

            current.clear()

            current.append(line)

            continue

        # ------------------------------------------------------------
        # Ignore content before first project title.
        # ------------------------------------------------------------

        if not current:
            continue

        # ------------------------------------------------------------
        # Everything else belongs to current project.
        # ------------------------------------------------------------

        current.append(
            _strip_bullet(line)
        )

    # Flush final project.
    flush_current()

    # ========================================================================
    # REMOVE EXACT DUPLICATES
    # ========================================================================

    unique_projects: List[str] = []

    seen_signatures: Set[str] = set()

    for project in projects:

        normalized = clean_text(
            project
        )

        signature = re.sub(
            r"[^a-z0-9]+",
            " ",
            normalized,
        ).strip()

        if not signature:
            continue

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)

        unique_projects.append(project)

    # ========================================================================
    # MERGE ACCIDENTAL FRAGMENTATION
    # ========================================================================

    unique_projects = _merge_fragmented_projects(
        unique_projects
    )

    return unique_projects


# ============================================================================
# SINGLE PROJECT ANALYSIS
# ============================================================================

def analyze_single_project(
    project: Any,
) -> Dict[str, Any]:
    """
    Analyze one project and return a stable result schema.
    """

    text = clean_text(project)

    if not text:
        return {
            "score": 0,
            "technologies": [],
            "complexity": {
                "score": 0,
                "features": [],
            },
            "impact": {
                "score": 0,
                "keywords": [],
            },
            "metrics": {
                "metrics_found": [],
                "score": 0,
            },
            "deployment": {
                "score": 0,
                "features": [],
            },
            "engineering": {
                "score": 0,
                "features": [],
            },
            "strengths": [],
        }

    # ========================================================================
    # INDIVIDUAL ANALYSES
    # ========================================================================

    technologies = detect_technologies(
        text
    )

    complexity = calculate_complexity(
        text
    )

    impact = calculate_impact(
        text
    )

    metrics = calculate_metrics(
        text
    )

    deployment = calculate_deployment(
        text
    )

    engineering = calculate_engineering(
        text
    )

    # ========================================================================
    # TECHNOLOGY SCORE
    # ========================================================================

    # Technology contribution is deliberately capped
    # so that simply listing technologies cannot dominate
    # the project score.

    technology_score = min(
        len(technologies) * 3,
        20,
    )

    # ========================================================================
    # TOTAL SCORE
    # ========================================================================

    score = (
        technology_score
        + complexity["score"]
        + impact["score"]
        + metrics["score"]
        + deployment["score"]
        + engineering["score"]
    )

    # Safety bounds.
    score = min(
        max(score, 0),
        100,
    )

    # ========================================================================
    # STRENGTHS
    # ========================================================================

    strengths: List[str] = []

    if complexity["score"] >= 20:
        strengths.append(
            "Technically complex project"
        )

    if len(technologies) >= 5:
        strengths.append(
            "Uses multiple technologies"
        )

    if metrics["score"] > 0:
        strengths.append(
            "Contains measurable results"
        )

    if deployment["score"] > 0:
        strengths.append(
            "Contains deployment approach"
        )

    if engineering["score"] > 0:
        strengths.append(
            "Follows engineering practices"
        )

    return {
        "score": score,
        "technologies": technologies,
        "complexity": complexity,
        "impact": impact,
        "metrics": metrics,
        "deployment": deployment,
        "engineering": engineering,
        "strengths": strengths,
    }


# ============================================================================
# QUALITY RATING
# ============================================================================

def project_quality(
    score: float,
) -> str:
    """
    Convert numerical project score to quality label.
    """

    try:
        numeric_score = float(score)

    except (
        TypeError,
        ValueError,
    ):
        numeric_score = 0.0

    if numeric_score >= 85:
        return "Excellent"

    if numeric_score >= 70:
        return "Good"

    if numeric_score >= 50:
        return "Average"

    return "Basic"


# ============================================================================
# MAIN PROJECT ANALYZER
# ============================================================================

def analyze_projects(
    sections: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze the Projects section from a parsed resume.

    Expected input:

        {
            "projects": "..."
        }

    Output:

        {
            "score": float,
            "quality": str,
            "project_count": int,
            "technologies": [...],
            "projects": [...]
        }
    """

    # ========================================================================
    # VALIDATE INPUT
    # ========================================================================

    if not isinstance(
        sections,
        dict,
    ):
        return {
            "score": 0,
            "quality": "Invalid",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    project_text = sections.get(
        "projects",
        "",
    )

    if project_text is None:
        project_text = ""

    if not isinstance(
        project_text,
        str,
    ):
        project_text = str(
            project_text
        )

    # ========================================================================
    # EMPTY PROJECT SECTION
    # ========================================================================

    if not project_text.strip():
        return {
            "score": 0,
            "quality": "No projects detected",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # ========================================================================
    # SPLIT PROJECTS
    # ========================================================================

    projects = split_projects(
        project_text
    )

    if not projects:
        return {
            "score": 0,
            "quality": "No valid projects",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # ========================================================================
    # ANALYZE EACH PROJECT
    # ========================================================================

    results: List[
        Dict[str, Any]
    ] = []

    for project in projects:

        result = analyze_single_project(
            project
        )

        results.append(
            result
        )

    if not results:
        return {
            "score": 0,
            "quality": "No valid projects",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # ========================================================================
    # CALCULATE AVERAGE SCORE
    # ========================================================================

    scores = [
        float(
            result.get(
                "score",
                0,
            )
        )
        for result in results
    ]

    average_score = (
        sum(scores)
        / len(scores)
    )

    # ========================================================================
    # COLLECT TECHNOLOGIES
    # ========================================================================

    technologies: List[str] = []

    for result in results:

        technologies.extend(
            result.get(
                "technologies",
                [],
            )
        )

    technologies = _unique_preserve_order(
        technologies
    )

    # ========================================================================
    # FINAL RESULT
    # ========================================================================

    return {
        "score": round(
            average_score,
            2,
        ),
        "quality": project_quality(
            average_score
        ),
        "project_count": len(results),
        "technologies": technologies,
        "projects": results,
    }
# ============================================================================
# METRICS
# ============================================================================

_METRIC_PATTERNS: Sequence[str] = (
    # Percentages
    r"(?<![\d.])\d+(?:\.\d+)?\s*%",

    # Plus counts
    r"(?<![\d.])\d+(?:,\d{3})*\+",

    # Explicit counts
    r"(?<![\d.])\d+(?:,\d{3})*\s+"
    r"(?:users?|records?|images?|samples?|datasets?|"
    r"transactions?|requests?|downloads?|customers?|"
    r"products?|documents?|rows?|entries?|"
    r"predictions?|vehicles?|employees?)\b",
)


_PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d[\d\s().-]{7,}\d)"
    r"(?!\d)"
)



# ============================================================================
# PROJECT TITLE DETECTION
# ============================================================================



# ============================================================================
# DESCRIPTION DETECTION
# ============================================================================

def _is_description_line(
    line: str,
) -> bool:
    """
    Determine whether a line is clearly descriptive rather than a title.
    """

    cleaned = clean_text(
        _strip_bullet(line)
    )

    if not cleaned:
        return False

    words = cleaned.split()

    action_words = {
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "trained",
        "used",
        "using",
        "integrated",
        "achieved",
        "improved",
        "optimized",
        "deployed",
        "worked",
        "responsible",
        "develop",
        "build",
        "create",
        "implement",
        "design",
        "train",
    }

    # ------------------------------------------------------------------
    # Action-based description.
    # ------------------------------------------------------------------

    if words and words[0] in action_words:
        return True

    # ------------------------------------------------------------------
    # Resume bullet.
    # ------------------------------------------------------------------

    if _is_bullet(line):
        return True

    # ------------------------------------------------------------------
    # Lines containing common descriptive connectors.
    # ------------------------------------------------------------------

    if re.search(
        r"\b(?:using|with|through|for|by)\b",
        cleaned,
    ):
        return True

    return False


# ============================================================================
# PROJECT BLOCK MERGING
# ============================================================================

def _merge_fragmented_projects(
    projects: List[str],
) -> List[str]:
    """
    Merge project blocks that are actually fragments of the same project.

    This protects against PDF/text extraction producing:

        Project A
        technologies...
        Project A
        description...

    or:

        Project A
        short project title variation
        description...

    as separate project blocks.
    """

    if len(projects) <= 1:
        return projects

    merged: List[str] = []

    for project in projects:

        # --------------------------------------------------------------
        # First project.
        # --------------------------------------------------------------

        if not merged:
            merged.append(project)
            continue

        previous = merged[-1]

        # --------------------------------------------------------------
        # Calculate similarity.
        # --------------------------------------------------------------

        similarity = _project_similarity(
            previous,
            project,
        )

        # --------------------------------------------------------------
        # Check whether one project is essentially contained
        # inside the other.
        # --------------------------------------------------------------

        subset = (
            _is_subset_project(
                previous,
                project,
            )
            or
            _is_subset_project(
                project,
                previous,
            )
        )

        # --------------------------------------------------------------
        # Strong overlap means same project.
        # --------------------------------------------------------------

        if (
            similarity >= 0.55
            or subset
        ):
            merged[-1] = (
                previous.strip()
                + " "
                + project.strip()
            ).strip()

            continue

        # --------------------------------------------------------------
        # Otherwise keep them separate.
        # --------------------------------------------------------------

        merged.append(project)

    return merged
# ============================================================================
# PROJECT SPLITTING
# ============================================================================

def split_projects(
    text: Any,
) -> List[str]:
    """
    Split a Projects section into real project blocks.

    Project metadata such as:

        Technologies:
        Tech Stack:
        Tools:
        Technologies Used:

    belongs to the current project.

    The function also performs a second pass to merge accidental
    fragmentation caused by PDF/text extraction.
    """

    if text is None:
        return []

    raw_text = str(text)

    if not raw_text.strip():
        return []

    # ------------------------------------------------------------------
    # Normalize line endings.
    # ------------------------------------------------------------------

    lines = (
        raw_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )

    # ------------------------------------------------------------------
    # Metadata prefixes.
    #
    # These lines should NEVER start a new project.
    # They belong to the project currently being processed.
    # ------------------------------------------------------------------

    metadata_prefixes = (
        "technologies:",
        "technology:",
        "tech stack:",
        "techstack:",
        "technologies used:",
        "tools:",
        "tools used:",
        "built with:",
        "developed using:",
    )

    projects: List[str] = []

    current: List[str] = []

    # ------------------------------------------------------------------
    # Helper to finalize the current project.
    # ------------------------------------------------------------------

    def flush_current() -> None:

        if not current:
            return

        project = " ".join(
            item.strip()
            for item in current
            if item.strip()
        ).strip()

        cleaned_project = clean_text(
            project
        )

        # Ignore extremely small fragments.
        if len(cleaned_project) >= 30:
            projects.append(project)

    # ------------------------------------------------------------------
    # Process each line.
    # ------------------------------------------------------------------

    for raw_line in lines:

        line = raw_line.strip()

        # Ignore empty lines.
        if not line:
            continue

        normalized_line = clean_text(
            _strip_bullet(line)
        )

        # ------------------------------------------------------------------
        # Metadata belongs to current project.
        # ------------------------------------------------------------------

        if normalized_line.startswith(
            metadata_prefixes
        ):

            if current:
                current.append(
                    _strip_bullet(line)
                )

            continue

        # ------------------------------------------------------------------
        # A recognized project title starts a new project.
        # ------------------------------------------------------------------

        if is_project_title(line):

            # Save previous project first.
            flush_current()

            # Start a new project.
            current.clear()

            current.append(line)

            continue

        # ------------------------------------------------------------------
        # Ignore content before the first project title.
        # ------------------------------------------------------------------

        if not current:
            continue

        # ------------------------------------------------------------------
        # Everything else belongs to the current project.
        # ------------------------------------------------------------------

        current.append(
            _strip_bullet(line)
        )

    # ------------------------------------------------------------------
    # Flush final project.
    # ------------------------------------------------------------------

    flush_current()

    # =========================================================================
    # REMOVE EXACT DUPLICATES
    # =========================================================================

    unique_projects: List[str] = []

    seen_signatures: Set[str] = set()

    for project in projects:

        normalized = clean_text(
            project
        )

        # Convert punctuation to spaces.
        signature = re.sub(
            r"[^a-z0-9]+",
            " ",
            normalized,
        ).strip()

        if not signature:
            continue

        if signature in seen_signatures:
            continue

        seen_signatures.add(signature)

        unique_projects.append(project)

    # =========================================================================
    # MERGE ACCIDENTAL FRAGMENTATION
    # =========================================================================

    unique_projects = _merge_fragmented_projects(
        unique_projects
    )

    return unique_projects
# ============================================================================
# SINGLE PROJECT ANALYSIS
# ============================================================================

def analyze_single_project(
    project: Any,
) -> Dict[str, Any]:
    """
    Analyze one project and return a stable result schema.

    The returned structure is intentionally stable so the main
    ResumeIQ analyzer can consume it safely.
    """

    text = clean_text(project)

    # ------------------------------------------------------------------
    # Empty project protection.
    # ------------------------------------------------------------------

    if not text:
        return {
            "score": 0,
            "technologies": [],
            "complexity": {
                "score": 0,
                "features": [],
            },
            "impact": {
                "score": 0,
                "keywords": [],
            },
            "metrics": {
                "metrics_found": [],
                "score": 0,
            },
            "deployment": {
                "score": 0,
                "features": [],
            },
            "engineering": {
                "score": 0,
                "features": [],
            },
            "strengths": [],
        }

    # =========================================================================
    # ANALYZE PROJECT COMPONENTS
    # =========================================================================

    technologies = detect_technologies(
        text
    )

    complexity = calculate_complexity(
        text
    )

    impact = calculate_impact(
        text
    )

    metrics = calculate_metrics(
        text
    )

    deployment = calculate_deployment(
        text
    )

    engineering = calculate_engineering(
        text
    )

    # =========================================================================
    # TECHNOLOGY SCORE
    # =========================================================================

    # Each detected technology contributes 3 points.
    #
    # Technology contribution is capped at 20 so that a project
    # cannot receive a high score simply by listing many tools.

    technology_score = min(
        len(technologies) * 3,
        20,
    )

    # =========================================================================
    # TOTAL PROJECT SCORE
    # =========================================================================

    score = (
        technology_score
        + complexity["score"]
        + impact["score"]
        + metrics["score"]
        + deployment["score"]
        + engineering["score"]
    )

    # ------------------------------------------------------------------
    # Defensive score boundaries.
    # ------------------------------------------------------------------

    score = min(
        max(score, 0),
        100,
    )

    # =========================================================================
    # STRENGTH DETECTION
    # =========================================================================

    strengths: List[str] = []

    # ------------------------------------------------------------------
    # Technical complexity.
    # ------------------------------------------------------------------

    if complexity["score"] >= 20:
        strengths.append(
            "Technically complex project"
        )

    # ------------------------------------------------------------------
    # Technology diversity.
    # ------------------------------------------------------------------

    if len(technologies) >= 5:
        strengths.append(
            "Uses multiple technologies"
        )

    # ------------------------------------------------------------------
    # Measurable outcomes.
    # ------------------------------------------------------------------

    if metrics["score"] > 0:
        strengths.append(
            "Contains measurable results"
        )

    # ------------------------------------------------------------------
    # Deployment.
    # ------------------------------------------------------------------

    if deployment["score"] > 0:
        strengths.append(
            "Contains deployment approach"
        )

    # ------------------------------------------------------------------
    # Engineering practices.
    # ------------------------------------------------------------------

    if engineering["score"] > 0:
        strengths.append(
            "Follows engineering practices"
        )

    # =========================================================================
    # RETURN STABLE RESULT
    # =========================================================================

    return {
        "score": score,
        "technologies": technologies,
        "complexity": complexity,
        "impact": impact,
        "metrics": metrics,
        "deployment": deployment,
        "engineering": engineering,
        "strengths": strengths,
    }
# ============================================================================
# QUALITY RATING
# ============================================================================

def project_quality(
    score: float,
) -> str:
    """
    Convert numerical project score to a quality label.

    Score ranges
    ------------
    85 - 100 : Excellent
    70 - 84  : Good
    50 - 69  : Average
    0  - 49  : Basic
    """

    try:
        numeric_score = float(score)

    except (
        TypeError,
        ValueError,
    ):
        numeric_score = 0.0

    if numeric_score >= 85:
        return "Excellent"

    if numeric_score >= 70:
        return "Good"

    if numeric_score >= 50:
        return "Average"

    return "Basic"


# ============================================================================
# MAIN PROJECT ANALYZER
# ============================================================================

def analyze_projects(
    sections: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze the Projects section from a parsed resume.

    Expected input
    --------------

        {
            "projects": "..."
        }

    Output
    ------

        {
            "score": float,
            "quality": str,
            "project_count": int,
            "technologies": [...],
            "projects": [...]
        }

    The function is defensive and always returns a predictable
    result structure.
    """

    # =========================================================================
    # INVALID INPUT
    # =========================================================================

    if not isinstance(
        sections,
        dict,
    ):
        return {
            "score": 0,
            "quality": "Invalid",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # =========================================================================
    # GET PROJECT SECTION
    # =========================================================================

    project_text = sections.get(
        "projects",
        "",
    )

    # -------------------------------------------------------------------------
    # Handle None.
    # -------------------------------------------------------------------------

    if project_text is None:
        project_text = ""

    # -------------------------------------------------------------------------
    # Convert unexpected input safely.
    # -------------------------------------------------------------------------

    if not isinstance(
        project_text,
        str,
    ):
        project_text = str(project_text)

    # =========================================================================
    # EMPTY PROJECT SECTION
    # =========================================================================

    if not project_text.strip():
        return {
            "score": 0,
            "quality": "No projects detected",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # =========================================================================
    # SPLIT PROJECTS
    # =========================================================================

    projects = split_projects(
        project_text
    )

    # =========================================================================
    # NO VALID PROJECTS
    # =========================================================================

    if not projects:
        return {
            "score": 0,
            "quality": "No valid projects",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # =========================================================================
    # ANALYZE EACH PROJECT
    # =========================================================================

    results: List[
        Dict[str, Any]
    ] = []

    for project in projects:

        result = analyze_single_project(
            project
        )

        results.append(
            result
        )

    # =========================================================================
    # SAFETY CHECK
    # =========================================================================

    if not results:
        return {
            "score": 0,
            "quality": "No valid projects",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # =========================================================================
    # CALCULATE AVERAGE PROJECT SCORE
    # =========================================================================

    scores = [
        float(
            result.get(
                "score",
                0,
            )
        )
        for result in results
    ]

    average_score = (
        sum(scores) / len(scores)
    )

    # =========================================================================
    # COLLECT TECHNOLOGIES
    # =========================================================================

    technologies: List[str] = []

    for result in results:

        technologies.extend(
            result.get(
                "technologies",
                [],
            )
        )

    # -------------------------------------------------------------------------
    # Remove duplicates while preserving order.
    # -------------------------------------------------------------------------

    technologies = _unique_preserve_order(
        technologies
    )

    # =========================================================================
    # FINAL RESULT
    # =========================================================================

    return {
        "score": round(
            average_score,
            2,
        ),
        "quality": project_quality(
            average_score
        ),
        "project_count": len(results),
        "technologies": technologies,
        "projects": results,
    }


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "TECHNOLOGIES",
    "COMPLEXITY_KEYWORDS",
    "IMPACT_KEYWORDS",
    "DEPLOYMENT_KEYWORDS",
    "ENGINEERING_KEYWORDS",
    "INVALID_PROJECT_TITLES",
    "PROJECT_TITLE_WORDS",
    "clean_text",
    "detect_technologies",
    "calculate_complexity",
    "calculate_impact",
    "calculate_metrics",
    "calculate_deployment",
    "calculate_engineering",
    "is_project_title",
    "split_projects",
    "analyze_single_project",
    "project_quality",
    "analyze_projects",
]