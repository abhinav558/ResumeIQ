"""
Certification Intelligence Engine

Extracts structured certification records from resume text while preserving
the legacy aggregate fields used by existing consumers.
"""

import re


TRUSTED_PROVIDERS = [
    "coursera",
    "aws",
    "ibm",
    "google",
    "microsoft",
    "udemy",
    "oracle",
    "nvidia",
]


# ---------------------------------------------------------------------------
# Section headings
# ---------------------------------------------------------------------------

SECTION_HEADINGS = {
    "education",
    "projects",
    "project",
    "technical skills",
    "skills",
    "experience",
    "internship",
    "achievements",
    "achievement",
    "professional summary",
    "summary",
    "certifications",
    "certification",
    "certificates",
    "certificate",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_line(line: str) -> str:
    """Normalize a certification line."""
    line = line.replace("\x7f", " ")

    # Remove common bullet characters.
    line = re.sub(
        r"^[\s•●▪◦*\-–—]+",
        "",
        line,
    )

    # Normalize horizontal whitespace.
    line = re.sub(r"[ \t]+", " ", line)

    return line.strip()


def _normalize_heading(line: str) -> str:
    """Normalize a possible section heading."""
    line = _clean_line(line)

    # Remove trailing punctuation.
    line = re.sub(r"[:|]+$", "", line).strip()

    return line.lower()


def _is_section_heading(line: str) -> bool:
    """Return True when a line is a recognized resume section heading."""
    return _normalize_heading(line) in SECTION_HEADINGS


def _normalize_provider(provider: str) -> str:
    """Return the canonical display name for a known provider."""
    mapping = {
        "coursera": "Coursera",
        "aws": "AWS",
        "ibm": "IBM",
        "google": "Google",
        "microsoft": "Microsoft",
        "udemy": "Udemy",
        "oracle": "Oracle",
        "nvidia": "NVIDIA",
    }

    return mapping.get(
        provider.lower(),
        provider,
    )


def _detect_provider(text: str) -> str | None:
    """Detect a trusted certification provider."""
    for provider in TRUSTED_PROVIDERS:
        if re.search(
            rf"\b{re.escape(provider)}\b",
            text,
            flags=re.IGNORECASE,
        ):
            return _normalize_provider(provider)

    return None


def _looks_like_certification(text: str) -> bool:
    """
    Determine whether a line is likely to represent a certification.

    This is intentionally conservative so arbitrary resume text is not
    incorrectly converted into certifications.
    """
    if _detect_provider(text) is not None:
        return True

    certification_words = re.search(
        r"\b("
        r"certified|"
        r"certification|"
        r"certificate|"
        r"essentials|"
        r"programming|"
        r"relational databases|"
        r"ai for everyone"
        r")\b",
        text,
        flags=re.IGNORECASE,
    )

    return certification_words is not None


def _extract_certification_name(
    text: str,
    provider: str | None,
) -> str:
    """Remove explicit provider formatting from a certification name."""
    name = text.strip()

    if provider:
        provider_patterns = [
            rf"\s*[-|–—:]\s*{re.escape(provider)}\s*$",
            rf"^{re.escape(provider)}\s*[-|–—:]\s*",
            rf"\s*\(\s*{re.escape(provider)}\s*\)\s*$",
        ]

        for pattern in provider_patterns:
            name = re.sub(
                pattern,
                "",
                name,
                flags=re.IGNORECASE,
            ).strip()

    # Remove trailing separators.
    name = re.sub(
        r"\s*[-|–—:]\s*$",
        "",
        name,
    ).strip()

    return name


def _extract_certification_section(text: str) -> str:
    """
    Extract the Certifications section without using a complex nested regex.

    This line-based approach is deliberately easier to reason about and
    avoids regex parser failures on newer Python versions.
    """
    lines = text.splitlines()

    in_certifications = False
    certification_lines = []

    for raw_line in lines:
        line = _clean_line(raw_line)

        if not line:
            if in_certifications:
                certification_lines.append("")
            continue

        heading = _normalize_heading(line)

        # Start certifications section.
        if heading in {
            "certifications",
            "certification",
            "certificates",
            "certificate",
        }:
            in_certifications = True
            continue

        # Stop when another major section begins.
        if in_certifications and heading in SECTION_HEADINGS:
            break

        if in_certifications:
            certification_lines.append(line)

    if certification_lines:
        return "\n".join(certification_lines)

    # If no Certifications heading exists, analyze the supplied text.
    return text


def _extract_certification_details(
    certification_text: str,
) -> list[dict]:
    """Build structured certification records."""
    lines = re.split(
        r"\n+",
        certification_text,
    )

    details = []
    seen = set()

    for raw_line in lines:
        line = _clean_line(raw_line)

        if not line:
            continue

        if _is_section_heading(line):
            continue

        if len(line) < 5:
            continue

        if not _looks_like_certification(line):
            continue

        provider = _detect_provider(line)

        name = _extract_certification_name(
            line,
            provider,
        )

        if len(name) < 3:
            continue

        key = (
            name.lower(),
            provider.lower() if provider else None,
        )

        if key in seen:
            continue

        seen.add(key)

        # Confidence represents extraction confidence, NOT external
        # certificate verification.
        confidence = (
            0.90
            if provider
            else 0.75
        )

        details.append(
            {
                "name": name,
                "provider": provider,
                "issue_date": None,
                "expiry_date": None,
                "credential_id": None,
                "credential_url": None,
                "skills": [],
                "confidence": confidence,
                "verified": False,
            }
        )

    return details


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_certifications(text):
    """
    Analyze resume certifications.

    Returns both structured certification records and legacy aggregate
    fields for backward compatibility.
    """

    if not text:
        return {
            "count": 0,
            "score": 0,
            "certifications": [],
            "certification_details": [],
            "trusted_providers": [],
        }

    # Normalize line endings while preserving certification boundaries.
    text = re.sub(
        r"\r\n?",
        "\n",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    certification_text = _extract_certification_section(
        text
    )

    details = _extract_certification_details(
        certification_text
    )

    # Legacy certification list.
    certifications = [
        detail["name"]
        for detail in details
    ]

    # Detect trusted providers in the certification section.
    trusted = []

    for provider in TRUSTED_PROVIDERS:
        if re.search(
            rf"\b{re.escape(provider)}\b",
            certification_text,
            flags=re.IGNORECASE,
        ):
            trusted.append(provider)

    score = min(
        len(certifications) * 25,
        100,
    )

    return {
        "count": len(certifications),
        "score": score,
        "certifications": certifications,
        "certification_details": details,
        "trusted_providers": trusted,
    }


__all__ = [
    "TRUSTED_PROVIDERS",
    "analyze_certifications",
]

