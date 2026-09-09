"""
ResumeIQ - Utility Functions

Shared helper functions used across all ResumeIQ engines.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Any

from .patterns import (
    MULTISPACE_PATTERN,
    PERCENT_METRIC_PATTERN,
    COUNT_METRIC_PATTERN,
    MULTIPLIER_PATTERN,
    TIME_PATTERN,
)


# ==========================================================
# TEXT
# ==========================================================

def normalize_text(text: str) -> str:
    """
    Lowercase and normalize whitespace.

    Args:
        text: Input text.

    Returns:
        Normalized lowercase text.
    """

    if not text:
        return ""

    text = text.replace("\n", " ")

    text = MULTISPACE_PATTERN.sub(" ", text)

    return text.lower().strip()


# ==========================================================
# UNIQUE
# ==========================================================

def unique(items: Iterable[Any]) -> List[Any]:
    """
    Preserve order while removing duplicates.

    Args:
        items: Iterable of values.

    Returns:
        List containing unique values in original order.
    """

    seen = set()
    result = []

    for item in items:
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            # Supports unhashable values gracefully.
            if item not in result:
                result.append(item)

    return result


# ==========================================================
# WHOLE WORD SEARCH
# ==========================================================

def contains_keyword(text: str, keyword: str) -> bool:
    """
    Whole-word keyword matching.

    Prevents:
        java matching javascript
        sql matching mysql

    Args:
        text: Text to search.
        keyword: Keyword to find.

    Returns:
        True if the keyword exists as a whole word.
    """

    if not text or not keyword:
        return False

    pattern = r"\b{}\b".format(
        re.escape(keyword.strip().lower())
    )

    return re.search(
        pattern,
        text.lower()
    ) is not None


# ==========================================================
# FIND KEYWORDS
# ==========================================================

def find_keywords(
    text: str,
    keywords: Iterable[str],
) -> List[str]:
    """
    Return all matched keywords.

    Args:
        text: Resume text.
        keywords: Keywords to search for.

    Returns:
        Unique matched keywords in database order.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    found = []

    for keyword in keywords:

        if not keyword:
            continue

        if contains_keyword(
            normalized_text,
            keyword,
        ):
            found.append(keyword)

    return unique(found)


# ==========================================================
# METRICS
# ==========================================================

def extract_metrics(text: str) -> List[str]:
    """
    Extract measurable achievements from resume text.

    Detects:
        - Percentages
        - Counts
        - Multipliers
        - Time durations

    Args:
        text: Resume text.

    Returns:
        Unique measurable metrics.
    """

    if not text:
        return []

    metrics = []

    for pattern in (
        PERCENT_METRIC_PATTERN,
        COUNT_METRIC_PATTERN,
        MULTIPLIER_PATTERN,
        TIME_PATTERN,
    ):
        matches = pattern.finditer(text)

        for match in matches:
            metrics.append(
                match.group(0)
            )

    return unique(metrics)


# ==========================================================
# SCORE
# ==========================================================

def percentage_score(
    value: int | float,
    maximum: int | float,
) -> float:
    """
    Convert raw score to percentage.

    Args:
        value: Current score.
        maximum: Maximum possible score.

    Returns:
        Percentage rounded to two decimal places.
    """

    if maximum <= 0:
        return 0.0

    return round(
        (value / maximum) * 100,
        2,
    )


# ==========================================================
# SAFE GET
# ==========================================================

def safe_get(
    dictionary,
    key,
    default=None,
):
    """
    Safely retrieve a value from a dictionary.

    Args:
        dictionary: Dictionary-like object.
        key: Key to retrieve.
        default: Fallback value.

    Returns:
        Dictionary value or default.
    """

    if not isinstance(
        dictionary,
        dict,
    ):
        return default

    return dictionary.get(
        key,
        default,
    )


# ==========================================================
# CLAMP
# ==========================================================

def clamp(
    value,
    minimum,
    maximum,
):
    """
    Restrict a value between bounds.

    Args:
        value: Input value.
        minimum: Lower bound.
        maximum: Upper bound.

    Returns:
        Value constrained between minimum and maximum.
    """

    if minimum > maximum:
        minimum, maximum = maximum, minimum

    return max(
        minimum,
        min(
            value,
            maximum,
        ),
    )


# ==========================================================
# AVERAGE
# ==========================================================

def average(values) -> float:
    """
    Calculate a safe average.

    Args:
        values: Iterable of numeric values.

    Returns:
        Average rounded to two decimal places.
    """

    values = list(values)

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        2,
    )


# ==========================================================
# WORD COUNT
# ==========================================================

def word_count(text: str) -> int:
    """
    Calculate resume word count.

    Args:
        text: Resume text.

    Returns:
        Number of words.
    """

    if not text:
        return 0

    return len(
        normalize_text(text).split()
    )