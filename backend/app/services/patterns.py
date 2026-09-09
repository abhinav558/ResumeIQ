"""
ResumeIQ - Regex Pattern Library

Centralized regular expressions used across ResumeIQ.
"""

import re


# ==========================================================
# BASIC
# ==========================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?"
    r"(?:\(?\d{3,5}\)?[-.\s]?)?"
    r"\d{3}[-.\s]?\d{4,6}\b"
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s]+",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
    re.IGNORECASE,
)

URL_PATTERN = re.compile(
    r"https?://[^\s]+",
    re.IGNORECASE,
)


# ==========================================================
# EDUCATION
# ==========================================================

CGPA_PATTERN = re.compile(
    r"\b(?:cgpa\s*[:\-]?\s*)?(\d(?:\.\d{1,2})?)\b",
    re.IGNORECASE,
)

PERCENTAGE_PATTERN = re.compile(
    r"\b\d{1,3}(?:\.\d+)?%"
)

YEAR_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b"
)

YEAR_RANGE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}\b"
)


# ==========================================================
# METRICS
# ==========================================================

PERCENT_METRIC_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?%"
)

COUNT_METRIC_PATTERN = re.compile(
    r"\b"
    # Prevent four-digit years such as 2020, 2024, 1999
    r"(?!(?:19|20)\d{2}\b)"
    # Normal counts:
    # 1, 25, 100
    # Comma-formatted counts:
    # 1,000 / 10,000 / 100,000
    r"(?:\d{1,3}(?:,\d{3})+|\d{1,3})"
    r"\+?\s*"
    r"(?:users?|clients?|records?|images?|samples?|datasets?|"
    r"transactions?|models?|projects?|downloads?|requests?)"
    r"\b",
    re.IGNORECASE,
)

MULTIPLIER_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?x\b",
    re.IGNORECASE,
)

TIME_PATTERN = re.compile(
    r"\b\d+\s*(?:days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)


# ==========================================================
# PROJECT
# ==========================================================

BULLET_PATTERN = re.compile(
    r"^\s*[-*•]\s+"
)

TITLE_CASE_PATTERN = re.compile(
    r"^[A-Z][A-Za-z0-9()\-, &, ]+$"
)


# ==========================================================
# EXPERIENCE
# ==========================================================

DATE_PATTERN = re.compile(
    r"\b"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    r"(?:[a-z]*)"
    r"\s+\d{4}\b",
    re.IGNORECASE,
)


# ==========================================================
# CLEANING
# ==========================================================

MULTISPACE_PATTERN = re.compile(
    r"\s+"
)

EMPTY_LINE_PATTERN = re.compile(
    r"\n\s*\n"
)