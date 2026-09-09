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
12. Preserve project titles for downstream profile construction.
13. Preserve complete project action sentences across PDF line wrapping.

Design goals
------------

- Deterministic
- Defensive
- No external dependencies
- Safe for malformed resume text
- Compatible with ResumeIQ analyzer
- Suitable for unit testing
- Backward compatible with existing analyzer consumers
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
    "html",
    "css",
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
    "simulated",
    "applied",
    "utilized",
    "performed",
    "configured",
    "engineered",
    "evaluated",
    "tested",
    "validated",
    "automated",
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
    "data preprocessing",
    "image preprocessing",
    "feature engineering",
    "feature extraction",
    "model evaluation",
    "data validation",
    "data integrity",
    "model updates",
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

    # Section headings
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
# ACTION VERBS
# ============================================================================

STRONG_ACTION_KEYWORDS: Sequence[str] = (
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

STANDARD_ACTION_KEYWORDS: Sequence[str] = (
    "developed",
    "built",
    "designed",
    "created",
    "trained",
    "simulated",
    "applied",
    "utilized",
    "performed",
    "configured",
    "engineered",
    "evaluated",
    "tested",
    "validated",
)


# ============================================================================
# EMBEDDED METADATA QUALIFIERS
# ============================================================================

# These words can remain after removing technology names from a normal
# technology metadata line, but they are not meaningful project-title
# vocabulary by themselves.
#
# Example:
#
#     Learning, Blockchain (Conceptual), Git
#
# After removing canonical technologies:
#
#     Learning (Conceptual)
#
# Neither "Learning" nor "Conceptual" should be treated as evidence of an
# embedded project title.
METADATA_QUALIFIER_WORDS: Set[str] = {
    "conceptual",
    "concept",
    "optional",
    "familiar",
    "familiarity",
    "basic",
    "basics",
    "beginner",
    "intermediate",
    "advanced",
    "knowledge",
    "experience",
    "proficiency",
    "proficient",
    "exposure",
    "exposed",
    "used",
    "using",
}


# These are continuation words from canonical multi-word technologies.
#
# This is intentionally conservative. The primary problematic case is:
#
#     Federated Learning
#                  ^^^^^^^
#
# A malformed metadata line can cause the embedded-title scanner to start at
# "Learning", making the remaining technology list look like a project title.
MULTIWORD_TECHNOLOGY_CONTINUATIONS: Set[str] = {
    "learning",
}


# ============================================================================
# ACTION EXTRACTION HELPERS
# ============================================================================

ACTION_START_PATTERN = re.compile(
    r"^(?:"
    r"implemented|optimized|automated|integrated|deployed|reduced|"
    r"increased|improved|achieved|developed|built|designed|created|"
    r"trained|simulated|applied|utilized|performed|configured|"
    r"engineered|evaluated|tested|validated|"
    r"used|leveraged|processed|preprocessed|conducted"
    r")\b",
    re.IGNORECASE,
)

ACTION_ANYWHERE_PATTERN = re.compile(
    r"\b(?:"
    r"implemented|optimized|automated|integrated|deployed|reduced|"
    r"increased|improved|achieved|developed|built|designed|created|"
    r"trained|simulated|applied|utilized|performed|configured|"
    r"engineered|evaluated|tested|validated|"
    r"used|leveraged|processed|preprocessed|conducted"
    r")\b",
    re.IGNORECASE,
)


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _normalize(value: Any) -> str:
    """Convert arbitrary input into normalized lowercase text."""
    if value is None:
        return ""

    if not isinstance(value, str):
        value = str(value)

    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")

    # Remove control characters while preserving newline and tab.
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", value)

    value = value.lower()
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)

    return value.strip()


def clean_text(text: Any) -> str:
    """Normalize text for analysis."""
    normalized = _normalize(text)

    if not normalized:
        return ""

    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def _contains_term(text: str, term: str) -> bool:
    """
    Boundary-aware keyword matching.

    Prevents:
        java -> javascript
        git -> github

    while supporting:
        flask.
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

    escaped_term = re.escape(normalized_term)

    pattern = (
        rf"(?<![a-z0-9])"
        rf"{escaped_term}"
        rf"(?![a-z0-9])"
    )

    return re.search(pattern, normalized_text) is not None


def _unique_preserve_order(
    items: Iterable[str],
) -> List[str]:
    """Remove duplicates while preserving deterministic order."""
    seen: Set[str] = set()
    result: List[str] = []

    for item in items:
        normalized = str(item).strip().lower()

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


def _is_bullet(line: str) -> bool:
    """
    Detect common resume bullet prefixes.

    Supports normal bullets as well as the standalone control-character
    marker commonly produced by PDF text extraction.
    """
    if not line:
        return False

    stripped = line.strip()

    if stripped in {"\x7f", "\x95", "\x96", "\x97"}:
        return True

    return bool(
        re.match(
            r"^\s*[-•●▪◦*‣►➢]\s*|\s*\d+[.)]\s+",
            line,
        )
    )


def _is_standalone_bullet_marker(line: str) -> bool:
    """Detect bullet markers that occupy their own extracted line."""
    if not line:
        return False

    stripped = line.strip()

    return stripped in {
        "\x7f",
        "\x95",
        "\x96",
        "\x97",
        "•",
        "●",
        "▪",
        "◦",
        "‣",
        "►",
        "➢",
        "-",
        "*",
    }


def _strip_bullet(line: str) -> str:
    """Remove a resume bullet marker."""
    if not line:
        return ""

    stripped = line.strip()

    if _is_standalone_bullet_marker(stripped):
        return ""

    return re.sub(
        r"^\s*[-•●▪◦*‣►➢]\s*|\s*\d+[.)]\s+",
        "",
        line,
    ).strip()


def _looks_like_year_only(text: str) -> bool:
    """Detect standalone four-digit years."""
    return bool(
        re.fullmatch(
            r"(?:19|20)\d{2}",
            text.strip(),
        )
    )


def _tokenize_project(text: str) -> Set[str]:
    """Create normalized token set for duplicate detection."""
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
    """Calculate Jaccard similarity between project blocks."""
    first_tokens = _tokenize_project(first)
    second_tokens = _tokenize_project(second)

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = len(first_tokens & second_tokens)
    union = len(first_tokens | second_tokens)

    if union == 0:
        return 0.0

    return intersection / union


def _is_subset_project(
    first: str,
    second: str,
) -> bool:
    """Determine whether one project is contained inside another."""
    first_tokens = _tokenize_project(first)
    second_tokens = _tokenize_project(second)

    if not first_tokens or not second_tokens:
        return False

    smaller = min(
        len(first_tokens),
        len(second_tokens),
    )

    if smaller < 3:
        return False

    intersection = len(first_tokens & second_tokens)

    return (
        intersection / smaller
    ) >= 0.80


def _extract_project_title(
    project: Any,
) -> str:
    """
    Extract a project title without inventing one.

    Supported inputs:
    - raw project string
    - structured mapping containing title/name
    """
    if isinstance(project, dict):
        for key in ("title", "name"):
            value = project.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

        return ""

    if project is None:
        return ""

    raw_text = str(project)

    for raw_line in (
        raw_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    ):
        line = raw_line.strip()

        if not line:
            continue

        candidate = _strip_bullet(line)

        if not candidate:
            continue

        if is_project_title(candidate):
            return candidate.strip()

        if (
            not _is_bullet(line)
            and len(candidate.split()) <= 10
            and len(candidate) <= 100
            and not _looks_like_year_only(candidate)
        ):
            return candidate.strip()

    return ""


def _extract_project_body(
    project: Any,
    title: str,
) -> str:
    """
    Return project evidence without the project title.

    Complexity should reflect the technical content demonstrated in the
    project description, not technical words that merely appear in the
    project name.
    """
    if project is None:
        return ""

    if isinstance(project, dict):
        content_parts: List[str] = []

        for key in (
            "description",
            "descriptions",
            "details",
            "content",
            "text",
            "body",
            "bullets",
            "evidence",
            "actions",
        ):
            value = project.get(key)

            if isinstance(value, str) and value.strip():
                content_parts.append(value)

            elif isinstance(value, (list, tuple, set)):
                content_parts.extend(
                    str(item)
                    for item in value
                    if str(item).strip()
                )

        if content_parts:
            return "\n".join(content_parts)

        raw_text = str(
            project.get("text")
            or project.get("content")
            or ""
        )

        if raw_text:
            project = raw_text
        else:
            return ""

    raw_text = str(project)

    lines = (
        raw_text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )

    normalized_title = clean_text(title)

    if not normalized_title:
        return raw_text

    result_lines: List[str] = []
    title_removed = False

    for line in lines:
        stripped = line.strip()

        if (
            not title_removed
            and stripped
            and clean_text(_strip_bullet(stripped))
            == normalized_title
        ):
            title_removed = True
            continue

        result_lines.append(line)

    return "\n".join(result_lines)


def _extract_project_actions(
    impact: Dict[str, Any],
) -> List[str]:
    """
    Backward-compatible impact keyword extraction.
    """
    if not isinstance(impact, dict):
        return []

    keywords = impact.get("keywords", [])

    if not isinstance(
        keywords,
        (list, tuple, set),
    ):
        return []

    return _unique_preserve_order(
        str(item)
        for item in keywords
        if str(item).strip()
    )


def _looks_like_metadata_line(
    text: str,
) -> bool:
    """Return True when a line starts with a technology metadata label."""
    normalized = clean_text(text)

    if not normalized:
        return False

    prefixes = (
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

    return normalized.startswith(prefixes)


# ============================================================================
# EMBEDDED PROJECT TITLE DETECTION
# ============================================================================

def _technology_token_count(text: str) -> int:
    """
    Count meaningful technology mentions in a candidate.

    This helper is intentionally based on the canonical TECHNOLOGIES list
    rather than raw word matching so that:

        Federated Learning, Blockchain (Conceptual), Git

    is recognized as technology metadata rather than a project title.
    """
    if not text:
        return 0

    return sum(
        1
        for technology in TECHNOLOGIES
        if _contains_term(text, technology)
    )


def _remove_technology_terms(text: str) -> str:
    """
    Remove canonical technology names from text.

    This is centralized so embedded-title validation uses exactly the same
    technology vocabulary everywhere.
    """
    remainder = text

    for technology in sorted(
        TECHNOLOGIES,
        key=lambda item: (-len(item), item),
    ):
        remainder = re.sub(
            rf"(?<![a-z0-9])"
            rf"{re.escape(technology.casefold())}"
            rf"(?![a-z0-9])",
            " ",
            remainder,
            flags=re.IGNORECASE,
        )

    return remainder


def _meaningful_non_technology_words(
    candidate: str,
) -> List[str]:
    """
    Return words that remain meaningful after technology removal.

    Metadata punctuation and generic technology qualifiers are intentionally
    ignored.

    Example:

        Learning, Blockchain (Conceptual), Git

    becomes approximately:

        Learning Conceptual

    and then both tokens are ignored because:
        - Learning is a continuation of a multi-word technology.
        - Conceptual is a metadata qualifier.

    Therefore the candidate contains no meaningful project-title vocabulary.
    """
    normalized = clean_text(candidate)

    if not normalized:
        return []

    remainder = _remove_technology_terms(normalized)

    # Remove punctuation left behind by technology lists.
    remainder = re.sub(
        r"[\s,;:/|(){}\[\].#+\-]+",
        " ",
        remainder,
    ).strip()

    words: List[str] = []

    for word in remainder.split():
        normalized_word = word.casefold().strip()

        if not normalized_word:
            continue

        if normalized_word in METADATA_QUALIFIER_WORDS:
            continue

        if normalized_word in MULTIWORD_TECHNOLOGY_CONTINUATIONS:
            continue

        words.append(normalized_word)

    return words


def _candidate_has_non_technology_content(
    candidate: str,
) -> bool:
    """
    Determine whether a candidate contains meaningful non-technology
    project-title content.

    Examples:

        "Pandas, Federated Learning, Blockchain (Conceptual), Git"
            -> False

        "TensorFlow, OpenCV, Flask, HTML, CSS, Scikit-learn"
            -> False

        "Crop Disease Prediction using Deep Learning"
            -> True

        "Movie Recommendation System using Python"
            -> True

    The important distinction is that residual words such as "Learning"
    from "Federated Learning" and qualifiers such as "Conceptual" do not
    constitute independent project-title content.
    """
    normalized = clean_text(candidate)

    if not normalized:
        return False

    technology_count = _technology_token_count(normalized)

    if technology_count == 0:
        return True

    meaningful_words = _meaningful_non_technology_words(
        normalized
    )

    return len(meaningful_words) >= 2


def _embedded_title_is_reliable(
    candidate: str,
) -> bool:
    """
    Apply conservative validation to a candidate found inside a metadata
    line.

    A candidate is accepted only when:

    1. It looks like a project title.
    2. It contains meaningful non-technology content.
    3. It is not dominated by technology-only vocabulary.
    4. It has at least two words.
    """
    normalized = clean_text(candidate)

    if not normalized:
        return False

    words = normalized.split()

    if len(words) < 2:
        return False

    if not is_project_title(candidate):
        return False

    if not _candidate_has_non_technology_content(candidate):
        return False

    technology_count = _technology_token_count(normalized)

    # A candidate containing several technology mentions must still contain
    # enough non-technology content to plausibly be a project title.
    if technology_count >= 3:
        meaningful_words = _meaningful_non_technology_words(
            normalized
        )

        if len(meaningful_words) < 2:
            return False

    return True


def _candidate_starts_inside_multiword_technology(
    content_words: Sequence[str],
    index: int,
) -> bool:
    """
    Determine whether an embedded-title candidate begins at the continuation
    of a canonical multi-word technology.

    Example:

        Federated Learning, Blockchain (Conceptual), Git
                         ^
                         candidate starts here

    "Learning" must not be interpreted as a new project title boundary.

    This check deliberately looks only at the immediately preceding tokens
    and the canonical TECHNOLOGIES list, keeping the behavior deterministic
    and conservative.
    """
    if index <= 0:
        return False

    current_word = re.sub(
        r"^[^A-Za-z0-9]+|[^A-Za-z0-9+#.-]+$",
        "",
        content_words[index],
    ).casefold()

    if current_word not in MULTIWORD_TECHNOLOGY_CONTINUATIONS:
        return False

    # Check whether the current token completes any canonical multi-word
    # technology ending in this token.
    for technology in TECHNOLOGIES:
        technology_words = technology.casefold().split()

        if len(technology_words) < 2:
            continue

        if technology_words[-1] != current_word:
            continue

        required_count = len(technology_words)

        if index < required_count - 1:
            continue

        preceding = [
            re.sub(
                r"^[^A-Za-z0-9]+|[^A-Za-z0-9+#.-]+$",
                "",
                content_words[index - offset],
            ).casefold()
            for offset in range(
                required_count - 1,
                -1,
                -1,
            )
        ]

        if preceding == technology_words:
            return True

    return False


def _split_embedded_project_title(
    line: str,
) -> Optional[tuple[str, str]]:
    """
    Detect a project title accidentally concatenated onto a technology
    metadata line.

    This helper is intentionally conservative.

    It supports malformed PDF extraction such as:

        Technologies: Python, TensorFlow, Git Crop Disease Prediction
        using Deep Learning

    and converts the first line into:

        Technologies: Python, TensorFlow, Git

    followed by:

        Crop Disease Prediction using Deep Learning

    IMPORTANT:

    Normal technology lists must NOT be interpreted as project titles.

    For example:

        Technologies: Python, TensorFlow, NumPy, Pandas, Federated Learning,
        Blockchain (Conceptual), Git

    remains one metadata line.

    The embedded-title detector additionally prevents a candidate from
    beginning inside a multi-word technology such as:

        Federated Learning
        Machine Learning
        Deep Learning
    """
    if not line:
        return None

    stripped_line = line.strip()

    if not _looks_like_metadata_line(stripped_line):
        return None

    words = stripped_line.split()

    if len(words) < 4:
        return None

    metadata_match = re.match(
        r"^\s*(?:"
        r"technologies|technology|tech stack|techstack|"
        r"technologies used|tools|tools used|built with|developed using"
        r")\s*:\s*",
        stripped_line,
        flags=re.IGNORECASE,
    )

    if not metadata_match:
        return None

    metadata_prefix = metadata_match.group(0)

    content_start = metadata_match.end()

    content = stripped_line[content_start:].strip()

    if not content:
        return None

    content_words = content.split()

    if len(content_words) < 3:
        return None

    candidates: List[tuple[int, str]] = []

    for index, word in enumerate(content_words):
        if index == 0:
            continue

        clean_word = re.sub(
            r"^[^A-Za-z0-9]+|[^A-Za-z0-9+#.-]+$",
            "",
            word,
        )

        if not clean_word:
            continue

        # PDF extraction often preserves capitalization from the original
        # title. Use it as a signal, but never as the sole criterion.
        if not clean_word[0].isupper():
            continue

        # CRITICAL:
        #
        # Do not start an embedded project candidate in the middle of a
        # multi-word technology such as:
        #
        #     Federated Learning
        #                  ^^^^^^^
        #
        # Otherwise:
        #
        #     Learning, Blockchain (Conceptual), Git
        #
        # can be falsely interpreted as a project title.
        if _candidate_starts_inside_multiword_technology(
            content_words,
            index,
        ):
            continue

        candidate_words = content_words[index:]

        if not (2 <= len(candidate_words) <= 10):
            continue

        candidate = " ".join(candidate_words).strip()

        if candidate.startswith(
            (",", ".", ";", ":", ")", "]", "}")
        ):
            continue

        # ------------------------------------------------------------------
        # CRITICAL FIX
        #
        # Reject candidates that are merely technology lists.
        #
        # This prevents:
        #
        #   Pandas, Federated Learning, Blockchain (Conceptual), Git
        #
        # and also:
        #
        #   Learning, Blockchain (Conceptual), Git
        #
        # from becoming projects.
        # ------------------------------------------------------------------
        if not _candidate_has_non_technology_content(candidate):
            continue

        if not _embedded_title_is_reliable(candidate):
            continue

        candidates.append(
            (index, candidate)
        )

    if not candidates:
        return None

    # Choose the earliest reliable title boundary.
    title_index, title = candidates[0]

    metadata_words = content_words[:title_index]

    if not metadata_words:
        return None

    metadata_part = (
        metadata_prefix
        + " ".join(metadata_words)
    ).strip()

    if not metadata_part:
        return None

    return metadata_part, title


# ============================================================================
# SENTENCE / ACTION EXTRACTION
# ============================================================================

def _sentence_split(
    text: str,
) -> List[str]:
    """
    Split prose into reasonably complete sentences.
    """
    if not text:
        return []

    normalized = clean_text(text)

    if not normalized:
        return []

    parts = re.split(
        r"(?<=[.!?])\s+(?=[a-z0-9])",
        normalized,
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def _extract_full_project_actions(
    text: Any,
) -> List[str]:
    """
    Extract complete project action sentences.
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

    actions: List[str] = []
    current_action: List[str] = []
    pending_bullet = False

    def flush_action() -> None:
        nonlocal current_action

        if not current_action:
            return

        action = clean_text(
            " ".join(
                part.strip()
                for part in current_action
                if part.strip()
            )
        )

        if (
            action
            and ACTION_START_PATTERN.match(action)
        ):
            actions.append(action)

        current_action = []

    for raw_line in lines:
        original = raw_line.strip()

        if not original:
            continue

        if _is_standalone_bullet_marker(original):
            flush_action()
            pending_bullet = True
            continue

        stripped = _strip_bullet(original)

        if not stripped:
            continue

        normalized = clean_text(stripped)

        if not normalized:
            continue

        if _looks_like_metadata_line(normalized):
            flush_action()
            pending_bullet = False
            continue

        explicit_bullet = _is_bullet(original)

        if explicit_bullet:
            flush_action()

            if ACTION_START_PATTERN.match(normalized):
                current_action = [stripped]

            elif len(normalized.split()) >= 6:
                current_action = [stripped]

            pending_bullet = False
            continue

        if ACTION_START_PATTERN.match(normalized):
            flush_action()
            current_action = [stripped]
            pending_bullet = False
            continue

        if pending_bullet:
            if ACTION_START_PATTERN.match(normalized):
                flush_action()
                current_action = [stripped]

            elif len(normalized.split()) >= 6:
                current_action = [stripped]

            pending_bullet = False
            continue

        if current_action:
            current_action.append(stripped)

    flush_action()

    if not actions:
        normalized = clean_text(text)

        for sentence in _sentence_split(normalized):
            if ACTION_ANYWHERE_PATTERN.search(sentence):
                actions.append(sentence)

    return _unique_preserve_order(actions)


def _extract_impact_evidence(
    text: Any,
) -> List[str]:
    """
    Extract qualitative evidence supporting project impact.
    """
    if text is None:
        return []

    raw_text = str(text)

    if not raw_text.strip():
        return []

    actions = _extract_full_project_actions(raw_text)

    if actions:
        return actions[:5]

    normalized = clean_text(raw_text)

    if not normalized:
        return []

    evidence: List[str] = []

    for sentence in _sentence_split(normalized):
        if _looks_like_metadata_line(sentence):
            continue

        if ACTION_ANYWHERE_PATTERN.search(sentence):
            evidence.append(sentence)

    return _unique_preserve_order(evidence)[:5]


def _extract_project_metrics(
    metrics: Dict[str, Any],
) -> List[str]:
    """Flatten metric analysis into domain-friendly metric strings."""
    if not isinstance(metrics, dict):
        return []

    values = metrics.get(
        "metrics_found",
        [],
    )

    if not isinstance(
        values,
        (list, tuple, set),
    ):
        return []

    return _unique_preserve_order(
        str(item)
        for item in values
        if str(item).strip()
    )


def _extract_project_deployment(
    deployment: Dict[str, Any],
) -> List[str]:
    """Flatten deployment features."""
    if not isinstance(deployment, dict):
        return []

    features = deployment.get(
        "features",
        [],
    )

    if not isinstance(
        features,
        (list, tuple, set),
    ):
        return []

    return _unique_preserve_order(
        str(item)
        for item in features
        if str(item).strip()
    )


def _extract_project_engineering(
    engineering: Dict[str, Any],
) -> List[str]:
    """Flatten engineering features."""
    if not isinstance(engineering, dict):
        return []

    features = engineering.get(
        "features",
        [],
    )

    if not isinstance(
        features,
        (list, tuple, set),
    ):
        return []

    return _unique_preserve_order(
        str(item)
        for item in features
        if str(item).strip()
    )


def _calculate_project_confidence(
    *,
    title: str,
    technologies: Sequence[str],
    actions: Sequence[str],
    metrics: Sequence[str],
    deployment: Sequence[str],
    engineering: Sequence[str],
) -> float:
    """
    Calculate deterministic project confidence.
    """
    score = 0.0

    if title:
        score += 0.25

    if technologies:
        score += 0.20

    if actions:
        score += 0.20

    if metrics:
        score += 0.15

    if deployment:
        score += 0.10

    if engineering:
        score += 0.10

    return round(
        min(max(score, 0.0), 1.0),
        2,
    )


# ============================================================================
# TECHNOLOGY DETECTION
# ============================================================================

def detect_technologies(
    text: Any,
) -> List[str]:
    """Detect technologies using boundary-aware matching."""
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

    return _unique_preserve_order(found)


# ============================================================================
# COMPLEXITY ANALYSIS
# ============================================================================

def calculate_complexity(
    text: Any,
) -> Dict[str, Any]:
    """
    Analyze technical complexity.

    Maximum score: 25.
    """
    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "features": [],
        }

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
        if any(
            _contains_term(
                normalized,
                keyword,
            )
            for keyword in keywords
        ):
            features.append(concept)

    features = _unique_preserve_order(features)

    score = min(
        len(features) * 5,
        25,
    )

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

def _has_action_context(
    text: str,
    keyword: str,
) -> bool:
    """
    Determine whether an impact keyword is being used as an actual project
    action rather than merely as a descriptor.
    """
    if not text or not keyword:
        return False

    if keyword != "automated":
        return _contains_term(
            text,
            keyword,
        )

    pattern = re.compile(
        r"\bautomated\b"
        r"(?:\s+the)?"
        r"\s+"
        r"(?:"
        r"process|workflow|pipeline|system|task|procedure|"
        r"analysis|testing|deployment|prediction|classification|"
        r"detection|training|evaluation|processing"
        r"(?:\s+\w+){0,4}"
        r")",
        flags=re.IGNORECASE,
    )

    if pattern.search(text):
        return True

    explicit_pattern = re.compile(
        r"\b(?:i|we|team|project)\s+automated\b",
        flags=re.IGNORECASE,
    )

    return explicit_pattern.search(text) is not None


def calculate_impact(
    text: Any,
) -> Dict[str, Any]:
    """
    Analyze project impact and engineering action language.

    Maximum score: 20.
    """
    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "keywords": [],
            "evidence": [],
            "qualitative_evidence": [],
            "has_qualitative_evidence": False,
        }

    keywords: List[str] = []

    for keyword in STRONG_ACTION_KEYWORDS:
        if _has_action_context(
            normalized,
            keyword,
        ):
            keywords.append(keyword)

    for keyword in STANDARD_ACTION_KEYWORDS:
        if _has_action_context(
            normalized,
            keyword,
        ):
            keywords.append(keyword)

    keywords = _unique_preserve_order(
        keywords
    )

    score = 0

    for keyword in keywords:
        if keyword in STRONG_ACTION_KEYWORDS:
            score += 3
        else:
            score += 2

    score = min(
        score,
        20,
    )

    evidence = _extract_impact_evidence(text)
    has_qualitative_evidence = bool(evidence)

    return {
        "score": score,
        "keywords": keywords,
        "evidence": evidence,
        "qualitative_evidence": evidence,
        "has_qualitative_evidence": has_qualitative_evidence,
    }


# ============================================================================
# METRICS
# ============================================================================

_METRIC_PATTERNS: Sequence[str] = (
    r"(?<![\d.])\d+(?:\.\d+)?\s*%",
    r"(?<![\d.])\d+(?:,\d{3})*\+",
    r"(?<![\d.])\d+(?:,\d{3})*\s+"
    r"(?:users?|records?|images?|samples?|datasets?|"
    r"transactions?|requests?|downloads?|customers?|"
    r"products?|documents?|rows?|entries?|"
    r"predictions?|vehicles?|employees?|"
    r"projects?|models?|classes?|epochs?|"
    r"queries?)\b",
    r"\b(?:accuracy|precision|recall|f1(?:\s+score)?|"
    r"f1-score|specificity|auc|roc-auc|"
    r"latency|response time|training time|"
    r"inference time|error rate)\s*"
    r"(?:[:=]\s*)?"
    r"\d+(?:\.\d+)?(?:\s*%)?",
)

_PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"\+?\d[\d\s().-]{7,}\d"
    r"(?!\d)"
)


def _is_valid_metric(
    raw_metric: str,
) -> bool:
    """Filter values unlikely to represent project results."""
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

    if (
        len(digits_only) >= 10
        and "%" not in metric
        and not re.search(
            r"\b(?:accuracy|precision|recall|f1|auc|latency|"
            r"response time|training time|inference time|error rate)\b",
            metric,
        )
    ):
        return False

    if re.fullmatch(
        r"(?:19|20)\d{2}",
        metric,
    ):
        return False

    if (
        len(digits_only) == 4
        and "%" not in metric
        and "+" not in metric
        and not re.search(
            r"\b(?:users?|records?|images?|samples?|datasets?|"
            r"transactions?|requests?|predictions?|vehicles?|"
            r"employees?|projects?|models?|classes?|epochs?|"
            r"queries?|documents?|accuracy|precision|recall|"
            r"f1|auc|latency|response time|training time|"
            r"inference time|error rate)\b",
            metric,
        )
    ):
        return False

    return True


def _normalize_metric_string(
    metric: str,
) -> str:
    """Normalize extracted metric formatting."""
    metric = re.sub(
        r"\s+",
        " ",
        metric.strip(),
    )

    metric = re.sub(
        r"\s+%",
        "%",
        metric,
    )

    metric = re.sub(
        r"\s*=\s*",
        "=",
        metric,
    )

    metric = re.sub(
        r"\s*:\s*",
        ":",
        metric,
    )

    return metric


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
        matches = re.findall(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )

        for match in matches:
            if isinstance(match, tuple):
                match = " ".join(
                    part
                    for part in match
                    if part
                )

            metric = _normalize_metric_string(
                str(match)
            )

            if _is_valid_metric(metric):
                metrics.append(metric)

    phone_ranges = [
        match.group(0)
        for match in _PHONE_PATTERN.finditer(
            normalized
        )
    ]

    filtered: List[str] = []

    for metric in metrics:
        if any(
            metric == phone
            or (
                metric.isdigit()
                and metric in phone
            )
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
    Detect deployment and application/integration approaches.
    """
    normalized = clean_text(text)

    if not normalized:
        return {
            "score": 0,
            "features": [],
        }

    explicit_deployment = (
        "deployment",
        "deployed",
        "docker",
        "cloud",
        "aws",
        "azure",
        "gcp",
        "rest api",
        "restful api",
        "api",
    )

    application_frameworks = (
        "streamlit",
        "flask",
        "fastapi",
    )

    features: List[str] = []

    for keyword in explicit_deployment:
        if _contains_term(
            normalized,
            keyword,
        ):
            features.append(keyword)

    for keyword in application_frameworks:
        if _contains_term(
            normalized,
            keyword,
        ):
            features.append(keyword)

    features = _unique_preserve_order(
        features
    )

    score = 0

    for feature in features:
        if feature in application_frameworks:
            continue

        score += 3

    score = min(
        score,
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
    Determine whether a resume line is likely to be a project title.

    The detector is intentionally conservative.
    """
    if line is None:
        return False

    raw = str(line).strip()

    if not raw:
        return False

    if _is_bullet(raw):
        return False

    cleaned = clean_text(
        _strip_bullet(raw)
    )

    if not cleaned:
        return False

    if cleaned in PROJECT_SECTION_HEADINGS:
        return False

    if len(cleaned) < 5:
        return False

    if len(cleaned) > 100:
        return False

    if _looks_like_year_only(cleaned):
        return False

    if cleaned in INVALID_PROJECT_TITLES:
        return False

    if _PHONE_PATTERN.search(cleaned):
        return False

    words = cleaned.split()

    if len(words) > 10:
        return False

    if cleaned.endswith(
        (".", ";", ":")
    ):
        return False

    for keyword in PROJECT_TITLE_WORDS:
        if _contains_term(
            cleaned,
            keyword,
        ):
            return True

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
            "simulated",
            "applied",
            "utilized",
            "performed",
            "configured",
            "evaluated",
            "tested",
            "validated",
            "develop",
            "build",
            "create",
            "implement",
            "design",
            "train",
        }

        if words[0] in action_words:
            return False

        technology_count = sum(
            1
            for technology in TECHNOLOGIES
            if _contains_term(
                cleaned,
                technology,
            )
        )

        if (
            technology_count >= len(words)
            and len(words) <= 3
        ):
            return False

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
    """Determine whether a line is clearly descriptive."""
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
        "simulated",
        "applied",
        "utilized",
        "performed",
        "configured",
        "engineered",
        "evaluated",
        "tested",
        "validated",
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
    Merge project blocks that are accidental fragments of the same project.
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

        if (
            similarity >= 0.55
            or subset
        ):
            merged[-1] = (
                previous.strip()
                + "\n"
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

    The returned strings preserve:

    - detected project title as first line
    - bullet boundaries
    - PDF-wrapped continuation lines
    - technology metadata attached to the correct project
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
        if not current:
            return

        project = "\n".join(
            item.strip()
            for item in current
            if item.strip()
        ).strip()

        cleaned_project = clean_text(project)

        if len(cleaned_project) >= 30:
            projects.append(project)

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if _is_standalone_bullet_marker(line):
            if current:
                current.append(line)
            continue

        normalized_line = clean_text(
            _strip_bullet(line)
        )

        if not normalized_line:
            continue

        # --------------------------------------------------------------------
        # TECHNOLOGY METADATA
        # --------------------------------------------------------------------

        if normalized_line.startswith(
            metadata_prefixes
        ):
            embedded_title = _split_embedded_project_title(line)

            if embedded_title is not None:
                metadata_part, title_part = embedded_title

                if current:
                    current.append(
                        _strip_bullet(metadata_part)
                    )

                    flush_current()
                    current.clear()

                current.append(title_part)
                continue

            # Normal technology metadata belongs to the active project.
            if current:
                current.append(
                    _strip_bullet(line)
                )

            continue

        # --------------------------------------------------------------------
        # PROJECT TITLE
        # --------------------------------------------------------------------

        if is_project_title(line):
            flush_current()
            current.clear()

            current.append(
                _strip_bullet(line)
            )

            continue

        # --------------------------------------------------------------------
        # PROJECT BODY
        # --------------------------------------------------------------------

        if not current:
            continue

        current.append(
            _strip_bullet(line)
        )

    flush_current()

    # ------------------------------------------------------------------------
    # Exact duplicate removal.
    # ------------------------------------------------------------------------

    unique_projects: List[str] = []
    seen_signatures: Set[str] = set()

    for project in projects:
        normalized = clean_text(project)

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

    return _merge_fragmented_projects(
        unique_projects
    )


# ============================================================================
# SINGLE PROJECT ANALYSIS
# ============================================================================

def analyze_single_project(
    project: Any,
) -> Dict[str, Any]:
    """
    Analyze one project.

    Project score:

        Technologies : 15
        Complexity   : 25
        Impact       : 20
        Metrics      : 20
        Deployment   : 10
        Engineering  : 10
        TOTAL         : 100
    """
    text = clean_text(project)
    title = _extract_project_title(project)

    if not text:
        empty_impact = {
            "score": 0,
            "keywords": [],
            "evidence": [],
            "qualitative_evidence": [],
            "has_qualitative_evidence": False,
        }

        return {
            "title": title,
            "score": 0,
            "quality": "Basic",
            "technologies": [],
            "actions": [],
            "metrics": [],
            "deployment": [],
            "engineering": [],
            "strengths": [],
            "confidence": 0.0,
            "complexity": {
                "score": 0,
                "features": [],
            },
            "impact": empty_impact,
            "metrics_analysis": {
                "metrics_found": [],
                "score": 0,
            },
            "deployment_analysis": {
                "score": 0,
                "features": [],
            },
            "engineering_analysis": {
                "score": 0,
                "features": [],
            },
        }

    technologies = detect_technologies(text)

    complexity_text = _extract_project_body(
        project,
        title,
    )

    complexity = calculate_complexity(
        complexity_text
    )

    impact = calculate_impact(text)

    qualitative_evidence = _extract_impact_evidence(
        project
    )

    if qualitative_evidence:
        impact["evidence"] = qualitative_evidence
        impact["qualitative_evidence"] = qualitative_evidence
        impact["has_qualitative_evidence"] = True
    else:
        impact["evidence"] = []
        impact["qualitative_evidence"] = []
        impact["has_qualitative_evidence"] = False

    metrics_analysis = calculate_metrics(text)

    deployment_analysis = calculate_deployment(text)

    engineering_analysis = calculate_engineering(text)

    actions = _extract_full_project_actions(
        project
    )

    if not actions:
        actions = _extract_project_actions(
            impact
        )

    metrics = _extract_project_metrics(
        metrics_analysis
    )

    deployment = _extract_project_deployment(
        deployment_analysis
    )

    engineering = _extract_project_engineering(
        engineering_analysis
    )

    technology_score = min(
        len(technologies) * 2.5,
        15,
    )

    score = (
        technology_score
        + complexity["score"]
        + impact["score"]
        + metrics_analysis["score"]
        + deployment_analysis["score"]
        + engineering_analysis["score"]
    )

    score = min(
        max(score, 0),
        100,
    )

    score = round(
        score,
        2,
    )

    quality = project_quality(
        score
    )

    strengths: List[str] = []

    if complexity["score"] >= 20:
        strengths.append(
            "Technically complex project"
        )

    if len(technologies) >= 5:
        strengths.append(
            "Uses multiple technologies"
        )

    if metrics_analysis["score"] > 0:
        strengths.append(
            "Contains measurable results"
        )

    if deployment_analysis["score"] > 0:
        strengths.append(
            "Contains deployment or integration approach"
        )

    if engineering_analysis["score"] > 0:
        strengths.append(
            "Follows engineering practices"
        )

    confidence = _calculate_project_confidence(
        title=title,
        technologies=technologies,
        actions=actions,
        metrics=metrics,
        deployment=deployment,
        engineering=engineering,
    )

    return {
        "title": title,
        "score": score,
        "quality": quality,
        "technologies": technologies,
        "actions": actions,
        "metrics": metrics,
        "deployment": deployment,
        "engineering": engineering,
        "strengths": strengths,
        "confidence": confidence,
        "complexity": complexity,
        "impact": impact,
        "metrics_analysis": metrics_analysis,
        "deployment_analysis": deployment_analysis,
        "engineering_analysis": engineering_analysis,
    }


# ============================================================================
# QUALITY RATING
# ============================================================================

def project_quality(
    score: float,
) -> str:
    """
    Convert numerical project score to quality label.

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
    """
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
        project_text = str(project_text)

    if not project_text.strip():
        return {
            "score": 0,
            "quality": "No projects detected",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

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

    results: List[Dict[str, Any]] = []

    for project in projects:
        result = analyze_single_project(
            project
        )

        results.append(result)

    if not results:
        return {
            "score": 0,
            "quality": "No valid projects",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

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