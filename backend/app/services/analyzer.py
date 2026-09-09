"""
ResumeIQ - Resume Intelligence Analyzer.

Production-grade orchestration layer that connects all resume
analysis engines into a single consistent analysis response.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence

# ============================================================================
# ENGINE IMPORTS
# ============================================================================

from .section_parser import extract_sections, detect_sections
from .skill_engine import analyze_skills
from .project_engine import analyze_projects
from .ats_engine import analyze_ats
from .experience_engine import analyze_experience
from .certification_engine import analyze_certifications
from .education_engine import analyze_education
from .scoring_engine import calculate_score, generate_recommendations
from .candidate.profile_builder import CandidateProfileBuilder


# ============================================================================
# CONSTANTS
# ============================================================================

MAX_RESUME_LENGTH = 100_000

ACHIEVEMENT_KEYWORDS: Sequence[str] = (
    "award",
    "awarded",
    "winner",
    "won",
    "achievement",
    "achieved",
    "hackathon",
    "competition",
    "finalist",
    "rank",
    "ranked",
    "scholarship",
    "recognition",
    "certified",
    "publication",
    "published",
)

ACHIEVEMENT_SCORE_PER_SIGNAL = 20
DEFAULT_SCORE = 0.0


# ============================================================================
# SAFE HELPERS
# ============================================================================

def _safe_dict(value: Any) -> Dict[str, Any]:
    """Return a dictionary or an empty dictionary."""
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    """Return a list for supported iterable containers."""
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return []


def _safe_score(
    value: Any,
    default: float = DEFAULT_SCORE,
) -> float:
    """Convert a score safely to float."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default

    if numeric != numeric:
        return default

    return round(max(numeric, 0.0), 2)


def _extract_score(
    result: Dict[str, Any],
    *keys: str,
) -> float:
    """
    Extract a score from an engine result.

    The first valid numeric key wins.
    This preserves compatibility with engines using:
    score, skill_score, project_score, ats_score, etc.
    """
    if not isinstance(result, dict):
        return 0.0

    for key in keys:
        if key not in result:
            continue

        value = result.get(key)

        if isinstance(value, bool):
            continue

        if isinstance(value, (int, float)):
            return _safe_score(value)

        try:
            return _safe_score(value)
        except Exception:
            continue

    return 0.0


def _normalize_confidence(value: Any) -> float:
    """Normalize confidence into a 0-100 scale."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0

    if numeric <= 1:
        numeric *= 100

    return round(
        min(max(numeric, 0.0), 100.0),
        2,
    )


def _normalize_strength(value: Any) -> str:
    """Normalize strength labels."""
    if not value:
        return ""

    return str(value).strip()


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

def _normalize_resume_text(text: Any) -> str:
    """
    Normalize and validate resume text.

    Contract:
    - None -> ValueError
    - Empty/whitespace-only string -> ValueError
    - Other non-string input -> TypeError
    """
    if text is None:
        raise ValueError("resume_text cannot be None")

    if not isinstance(text, str):
        raise TypeError("resume_text must be a string")

    text = text.strip()

    if not text:
        raise ValueError("resume_text cannot be empty")

    if len(text) > MAX_RESUME_LENGTH:
        text = text[:MAX_RESUME_LENGTH]

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = text.replace("●", "•")
    text = text.replace("▪", "•")
    text = text.replace("◦", "•")
    text = text.replace("‣", "•")

    text = "".join(
        char
        for char in text
        if char in ("\n", "\t") or ord(char) >= 32
    )

    text = text.strip()

    if not text:
        raise ValueError("resume_text cannot be empty")

    return text


# ============================================================================
# METADATA EXTRACTION
# ============================================================================

def _extract_email(text: str) -> Optional[str]:
    match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    patterns = (
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        r"(?<!\d)\+?\d[\d\s().-]{8,}\d(?!\d)",
    )

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            value = match.group(0).strip()

            digits = re.sub(r"\D", "", value)

            if len(digits) >= 10:
                return value

    return None


def _extract_link(text: str) -> Optional[str]:
    """
    Extract the first GitHub, LinkedIn, or HTTP(S) URL.

    Supports both:
        https://github.com/user
        github.com/user
    """
    patterns = (
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s]+",
        r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
        r"https?://[^\s]+",
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(0).rstrip(".,);")

    return None


def _is_section_heading(line: str) -> bool:
    """Conservative section-heading detection."""
    normalized = re.sub(
        r"[^a-z ]",
        " ",
        line.lower(),
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    headings = {
        "summary",
        "objective",
        "profile",
        "education",
        "skills",
        "technical skills",
        "projects",
        "academic projects",
        "experience",
        "work experience",
        "internship",
        "internships",
        "certifications",
        "achievements",
        "awards",
        "publications",
        "languages",
    }

    return normalized in headings


def _extract_name(text: str) -> Optional[str]:
    """
    Extract a likely candidate name from the first meaningful lines.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:8]:
        if _is_section_heading(line):
            continue

        if "@" in line:
            continue

        if re.search(r"\d{7,}", line):
            continue

        if re.search(
            r"https?://|www\.|github\.com|linkedin\.com",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        if len(line) > 60:
            continue

        words = line.split()

        if not 2 <= len(words) <= 5:
            continue

        if all(
            re.fullmatch(
                r"[A-Za-z][A-Za-z.'-]*",
                word,
            )
            for word in words
        ):
            return line

    return None


def _extract_summary(
    text: str,
    sections: Dict[str, Any],
) -> Optional[str]:
    """Extract summary from section data when available."""
    for key in (
        "summary",
        "objective",
        "profile",
    ):
        value = sections.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _extract_resume_metadata(
    text: str,
    sections: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "name": _extract_name(text),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "link": _extract_link(text),
        "summary": _extract_summary(
            text,
            sections,
        ),
    }


# ============================================================================
# METRIC EXTRACTION
# ============================================================================

def _metric_has_impact_context(
    text: str,
    start: int,
    end: int,
) -> bool:
    """Determine whether a numeric value appears in meaningful context."""
    window_start = max(0, start - 80)
    window_end = min(len(text), end + 100)

    context = text[window_start:window_end].lower()

    impact_terms = (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "improved",
        "improvement",
        "reduced",
        "reduction",
        "increased",
        "increase",
        "achieved",
        "performance",
        "efficiency",
        "faster",
        "speed",
        "users",
        "records",
        "predictions",
        "images",
        "samples",
        "requests",
    )

    return any(
        term in context
        for term in impact_terms
    )


def _extract_metrics(text: str) -> List[str]:
    """Extract meaningful project/result metrics."""
    if not text:
        return []

    metrics: List[str] = []

    patterns = (
        r"(?<![\d.])\d+(?:\.\d+)?\s*%",
        r"(?<![\d.])\d+(?:,\d{3})?\+",
        r"(?<![\d.])\d+(?:,\d{3})*\s+"
        r"(?:users?|records?|images?|samples?|"
        r"datasets?|transactions?|requests?|"
        r"predictions?|vehicles?|employees?)",
    )

    for pattern in patterns:
        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            value = match.group(0).strip()

            digits = re.sub(
                r"\D",
                "",
                value,
            )

            if not digits:
                continue

            if len(digits) >= 10 and "%" not in value:
                continue

            if re.fullmatch(
                r"(?:19|20)\d{2}",
                value,
            ):
                continue

            if not _metric_has_impact_context(
                text,
                match.start(),
                match.end(),
            ):
                continue

            if value.lower() not in {
                item.lower()
                for item in metrics
            }:
                metrics.append(value)

    return metrics


# ============================================================================
# ACHIEVEMENTS
# ============================================================================

def _calculate_achievement_score(
    text: str,
) -> Dict[str, Any]:
    """Calculate achievement signals deterministically."""
    if not text:
        return {
            "score": 0,
            "signals": [],
            "count": 0,
        }

    lower = text.lower()
    signals = []

    for keyword in ACHIEVEMENT_KEYWORDS:
        if re.search(
            rf"(?<![a-z0-9])"
            rf"{re.escape(keyword)}"
            rf"(?![a-z0-9])",
            lower,
        ):
            if keyword not in signals:
                signals.append(keyword)

    score = min(
        len(signals) * ACHIEVEMENT_SCORE_PER_SIGNAL,
        100,
    )

    return {
        "score": score,
        "signals": signals,
        "count": len(signals),
    }


# ============================================================================
# CONFIDENCE
# ============================================================================

def _calculate_confidence(
    *,
    text: str,
    sections: Dict[str, Any],
    skills: Dict[str, Any],
    projects: Dict[str, Any],
    ats: Dict[str, Any],
    experience: Dict[str, Any],
    education: Dict[str, Any],
    certifications: Dict[str, Any],
) -> int:
    """Calculate overall extraction confidence."""
    score = 0

    if text:
        score += 15

    if sections:
        score += 15

    if _safe_list(skills.get("skills")):
        score += 10

    if _safe_list(projects.get("projects")):
        score += 15

    if education.get("education_found"):
        score += 15

    if experience:
        score += 10

    if certifications:
        score += 10

    if ats:
        score += 10

    return int(round(min(score, 100)))


# ============================================================================
# SCORE INPUT
# ============================================================================

def _build_score_input(
    *,
    skills: Dict[str, Any],
    projects: Dict[str, Any],
    ats: Dict[str, Any],
    experience: Dict[str, Any],
    certifications: Dict[str, Any],
    education: Dict[str, Any],
    achievements: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the stable input contract for scoring_engine."""
    return {
        "skills_score": _extract_score(
            skills,
            "skill_score",
            "skills_score",
            "score",
        ),
        "project_score": _extract_score(
            projects,
            "project_score",
            "projects_score",
            "score",
        ),
        "ats_score": _extract_score(
            ats,
            "ats_score",
            "score",
        ),
        "experience_score": _extract_score(
            experience,
            "experience_score",
            "score",
        ),
        "certification_score": _extract_score(
            certifications,
            "certification_score",
            "certifications_score",
            "score",
        ),
        "education_score": _extract_score(
            education,
            "education_score",
            "score",
        ),
        "achievement_score": _extract_score(
            achievements,
            "achievement_score",
            "achievements_score",
            "score",
        ),
    }


# ============================================================================
# SKILL NORMALIZATION
# ============================================================================

def _normalize_skill_entries(
    skills_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Normalize skill engine output."""
    raw = (
        skills_result.get("skills")
        or skills_result.get("skills_found")
        or skills_result.get("items")
        or skills_result.get("skill_details")
        or []
    )

    entries: List[Dict[str, Any]] = []

    for item in _safe_list(raw):
        if isinstance(item, str):
            name = item.strip()

            if name:
                entries.append({"name": name})

            continue

        if not isinstance(item, dict):
            continue

        name = (
            item.get("name")
            or item.get("skill")
            or item.get("technology")
        )

        if not name:
            continue

        normalized = dict(item)
        normalized["name"] = str(name).strip()

        entries.append(normalized)

    return _deduplicate_items(
        entries,
        keys=("name",),
    )


def _normalize_skills_result(
    skills_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Normalize the public skill-analysis contract.

    The skill engine historically exposes detected skills through
    ``skills_found`` while the rest of ResumeIQ expects ``skills``.
    Keep both aliases synchronized and derive ``total_skills`` from the
    canonical deduplicated list so downstream consumers receive the same
    skill set.
    """
    result = dict(_safe_dict(skills_result))

    entries = _normalize_skill_entries(result)

    skills: List[str] = []

    for entry in entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue

        signature = name.casefold()

        if any(
            existing.casefold() == signature
            for existing in skills
        ):
            continue

        skills.append(name)

    result["skills"] = skills
    result["skills_found"] = list(skills)
    result["total_skills"] = len(skills)

    # Preserve rich skill metadata when supplied by the engine, but make
    # sure an absent/empty skills list can still be represented correctly.
    if not isinstance(result.get("skill_details"), list):
        result["skill_details"] = entries

    score = _extract_score(
        result,
        "skill_score",
        "skills_score",
        "score",
    )

    result["skill_score"] = score
    result["skills_score"] = score
    result["score"] = score

    return result


# ============================================================================
# PROJECT NORMALIZATION
# ============================================================================

def _normalize_project_title(
    title: Any,
) -> str:
    """Normalize project title without inventing content."""
    if title is None:
        return ""

    value = str(title).strip()

    if not value:
        return ""

    value = re.sub(r"\s+", " ", value)

    value = re.sub(
        r"^\s*(?:[-•●▪◦*‣►➢]|\d+[.)])\s*",
        "",
        value,
    )

    return value.strip()


def _extract_project_titles_from_section(
    project_text: Any,
) -> List[str]:
    """Recover project titles directly from the Projects section."""
    if not project_text:
        return []

    text = str(project_text)

    try:
        from .project_engine import is_project_title
    except ImportError:
        return []

    titles: List[str] = []

    for raw_line in (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .splitlines()
    ):
        line = raw_line.strip()

        if not line:
            continue

        try:
            valid_title = is_project_title(line)
        except Exception:
            valid_title = False

        if not valid_title:
            continue

        title = re.sub(
            r"^\s*(?:[-•●▪◦*‣►➢]|\d+[.)])\s*",
            "",
            line,
        ).strip()

        if (
            title
            and title.lower()
            not in {
                existing.lower()
                for existing in titles
            }
        ):
            titles.append(title)

    return titles


def _normalize_project_entries(
    project_result: Dict[str, Any],
    project_section_text: Any = "",
) -> List[Dict[str, Any]]:
    """Normalize project engine output."""
    raw = (
        project_result.get("projects")
        or project_result.get("items")
        or project_result.get("project_details")
        or []
    )

    title_fallbacks = _extract_project_titles_from_section(
        project_section_text
    )

    entries: List[Dict[str, Any]] = []

    for index, item in enumerate(_safe_list(raw)):
        if isinstance(item, str):
            title = _normalize_project_title(item)

            if title:
                entries.append({"title": title})

            continue

        if not isinstance(item, dict):
            continue

        normalized = dict(item)

        title = _normalize_project_title(
            item.get("title")
            or item.get("name")
        )

        if not title and index < len(title_fallbacks):
            title = title_fallbacks[index]

        if not title:
            technologies = _safe_list(
                item.get("technologies")
            )

            actions = _safe_list(
                item.get("actions")
            )

            if not technologies and not actions:
                continue

        normalized["title"] = title

        for field in (
            "technologies",
            "actions",
            "metrics",
            "deployment",
            "engineering",
            "strengths",
        ):
            if field in normalized:
                normalized[field] = [
                    str(value).strip()
                    for value in _safe_list(
                        normalized.get(field)
                    )
                    if str(value).strip()
                ]

        normalized["score"] = _safe_score(
            normalized.get("score")
        )

        if "confidence" in normalized:
            normalized["confidence"] = _normalize_confidence(
                normalized.get("confidence")
            )

        entries.append(normalized)

    return _merge_project_entries(entries)


def _merge_project_entries(
    entries: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Merge duplicate project entries."""
    merged: List[Dict[str, Any]] = []

    def normalized_key(title: str) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            title.lower(),
        ).strip()

    for entry in entries:
        title = str(
            entry.get("title") or ""
        ).strip()

        key = normalized_key(title)

        if not key:
            merged.append(entry)
            continue

        existing_index = None

        for index, existing in enumerate(merged):
            existing_key = normalized_key(
                str(
                    existing.get("title") or ""
                )
            )

            if existing_key == key:
                existing_index = index
                break

        if existing_index is None:
            merged.append(entry)
            continue

        existing = merged[existing_index]

        for field, value in entry.items():
            if field not in existing:
                existing[field] = value
                continue

            current = existing[field]

            if not current and value:
                existing[field] = value
                continue

            if isinstance(current, list):
                combined = current + (
                    value
                    if isinstance(value, list)
                    else []
                )

                seen = set()
                deduped = []

                for item in combined:
                    signature = str(item).strip().lower()

                    if signature and signature not in seen:
                        seen.add(signature)
                        deduped.append(item)

                existing[field] = deduped

            elif (
                field == "score"
                and _safe_score(value)
                > _safe_score(current)
            ):
                existing[field] = value

    return merged


# ============================================================================
# EDUCATION NORMALIZATION
# ============================================================================

def _sanitize_education_entry(
    entry: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Clean malformed education records."""
    if not isinstance(entry, dict):
        return None

    normalized = dict(entry)

    degree = str(
        normalized.get("degree") or ""
    ).strip()

    institution = str(
        normalized.get("institution") or ""
    ).strip()

    if "|" in institution:
        parts = [
            part.strip()
            for part in institution.split("|")
            if part.strip()
        ]

        if len(parts) >= 2:
            possible_year = parts[-1]

            if re.fullmatch(
                r"(?:19|20)\d{2}",
                possible_year,
            ):
                if not normalized.get("end_date"):
                    normalized["end_date"] = possible_year

                institution = " | ".join(parts[:-1])

    generic_labels = {
        "education",
        "secondary school education",
        "higher secondary education",
        "intermediate education",
        "school education",
        "secondary school",
        "intermediate",
    }

    def normalize_value(value: Any) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            str(value or "").lower(),
        ).strip()

    degree_normalized = normalize_value(degree)
    institution_normalized = normalize_value(institution)

    if (
        degree_normalized
        and institution_normalized == degree_normalized
    ):
        institution = ""

    if institution_normalized in generic_labels:
        institution = ""

    # Repair:
    # institution = "Secondary School Education | 2020"
    if institution:
        match = re.match(
            r"^(.*?)\s*\|\s*((?:19|20)\d{2})$",
            institution,
        )

        if match:
            prefix = match.group(1).strip()
            year = match.group(2)

            if normalize_value(prefix) in generic_labels:
                if not normalized.get("end_date"):
                    normalized["end_date"] = year

                institution = ""

    # Normalize dates.
    for field in (
        "start_date",
        "end_date",
    ):
        value = normalized.get(field)

        if value is not None:
            value = str(value).strip()

            if not re.fullmatch(
                r"(?:19|20)\d{2}",
                value,
            ):
                normalized[field] = None
            else:
                normalized[field] = value

    # Normalize numerical fields.
    for field in (
        "cgpa",
        "percentage",
    ):
        value = normalized.get(field)

        if value is None:
            continue

        try:
            normalized[field] = float(value)
        except (
            TypeError,
            ValueError,
        ):
            normalized[field] = None

    normalized["degree"] = degree or None
    normalized["institution"] = institution or None

    if not any(
        normalized.get(field)
        for field in (
            "degree",
            "institution",
            "start_date",
            "end_date",
            "cgpa",
            "percentage",
        )
    ):
        return None

    return normalized


def _extract_source_education_entries(
    education_text: Any,
) -> List[Dict[str, Any]]:
    """Extract conservative education records directly from the source text.

    The education engine is the primary parser, but PDF extraction can split a
    school record from its score/date metadata. In that situation, the engine
    may accidentally attach the trailing CGPA to the previous institution.
    This helper reconstructs records from the original Education section so the
    orchestration layer can correct that specific class of corruption without
    inventing values.
    """
    if not education_text:
        return []

    text = str(education_text)
    lines = [
        re.sub(r"\s+", " ", line).strip(" |")
        for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    ]
    lines = [line for line in lines if line]

    generic = {
        "education",
        "secondary school education",
        "higher secondary education",
        "intermediate education",
        "school education",
        "secondary school",
        "intermediate",
        "bachelor of technology",
        "bachelor of engineering",
        "bachelor of science",
        "master of technology",
        "master of science",
        "master of engineering",
    }

    year_re = re.compile(
        r"\b((?:19|20)\d{2})(?:\s*[–—-]\s*((?:19|20)\d{2}))?\b"
    )
    cgpa_re = re.compile(
        r"\bcgpa\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        re.I,
    )
    percentage_re = re.compile(
        r"\bpercentage\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%?",
        re.I,
    )
    percent_symbol_re = re.compile(
        r"\b(\d+(?:\.\d+)?)\s*%"
    )

    def norm(value: Any) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            str(value or "").lower(),
        ).strip()

    def is_metadata(line: str) -> bool:
        low = norm(line)

        if low in generic:
            return True

        if year_re.fullmatch(line.strip()):
            return True

        if (
            cgpa_re.search(line)
            or percentage_re.search(line)
            or percent_symbol_re.search(line)
        ):
            return True

        return False

    def looks_like_institution(line: str) -> bool:
        low = norm(line)

        if not low or is_metadata(line):
            return False

        if len(low.split()) < 2:
            return False

        if (
            year_re.search(line)
            or cgpa_re.search(line)
            or percentage_re.search(line)
        ):
            return False

        # Degree/education descriptors belong to the current institution.
        degree_markers = (
            "bachelor",
            "master",
            "degree",
            "education",
            "school",
            "college",
            "university",
            "institute",
            "academy",
        )

        return any(
            marker in low
            for marker in degree_markers
        )

    records: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    def ensure_current() -> Dict[str, Any]:
        nonlocal current

        if current is None:
            current = {
                "institution": None,
                "degree": None,
                "field_of_study": None,
                "start_date": None,
                "end_date": None,
                "cgpa": None,
                "percentage": None,
            }

        return current

    for line in lines:
        low = norm(line)

        if looks_like_institution(line):
            # A real institution starts a new record once the current record
            # already has an institution. This prevents Vikas Grammar High
            # School from being folded into ABV Junior College.
            if current and current.get("institution"):
                records.append(current)
                current = None

            rec = ensure_current()
            rec["institution"] = line
            continue

        rec = ensure_current()

        # Degree/level line.
        if low in generic or any(
            marker in low
            for marker in (
                "bachelor of technology",
                "bachelor of engineering",
                "bachelor of science",
                "master of technology",
                "master of science",
                "master of engineering",
                "intermediate education",
                "secondary school education",
            )
        ):
            degree_part = re.split(
                r"\|",
                line,
                maxsplit=1,
            )[0].strip()

            if degree_part:
                rec["degree"] = degree_part

            # A degree line can also contain field of study.
            if " in " in degree_part.lower():
                degree, field = re.split(
                    r"\s+in\s+",
                    degree_part,
                    maxsplit=1,
                    flags=re.I,
                )
                rec["degree"] = degree.strip()
                rec["field_of_study"] = (
                    field.strip()
                    or None
                )

        year_match = year_re.search(line)

        if year_match:
            start = year_match.group(1)
            end = year_match.group(2) or start

            rec["start_date"] = start
            rec["end_date"] = end

        cgpa_match = cgpa_re.search(line)

        if cgpa_match:
            value = float(cgpa_match.group(1))

            if 0 <= value <= 10:
                rec["cgpa"] = value

        percentage_match = percentage_re.search(line)

        if percentage_match:
            value = float(
                percentage_match.group(1)
            )

            if 0 <= value <= 100:
                rec["percentage"] = value

        else:
            percent_match = percent_symbol_re.search(line)

            if percent_match:
                value = float(
                    percent_match.group(1)
                )

                if 0 <= value <= 100:
                    rec["percentage"] = value

    if current and any(current.values()):
        records.append(current)

    # Only use source reconstruction when it produced genuine institution
    # records. This keeps the normal engine output authoritative for unusual
    # or very sparse education sections.
    return [
        record
        for record in records
        if record.get("institution")
    ]


def _reconcile_education_with_source(
    entries: List[Dict[str, Any]],
    education_text: Any,
) -> List[Dict[str, Any]]:
    """Correct education records using institution-level source evidence."""
    source_entries = _extract_source_education_entries(
        education_text
    )

    if len(source_entries) < 2:
        return entries

    def norm(value: Any) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            str(value or "").lower(),
        ).strip()

    reconciled: List[Dict[str, Any]] = []

    for source in source_entries:
        source_inst = norm(
            source.get("institution")
        )

        best = None

        for entry in entries:
            entry_inst = norm(
                entry.get("institution")
            )

            if entry_inst and (
                entry_inst == source_inst
                or entry_inst in source_inst
                or source_inst in entry_inst
            ):
                best = entry
                break

        if best is None:
            # Preserve source-derived structure when the engine omitted an
            # institution entirely. No value is invented; everything comes
            # directly from the Education section.
            best = {}
        else:
            best = dict(best)

        # Source evidence wins for score/date fields. This is crucial when a
        # previous record accidentally inherited a later school's CGPA.
        # Institution/degree/field are filled from source when available.
        for field in (
            "institution",
            "degree",
            "field_of_study",
        ):
            source_value = source.get(field)

            if source_value is not None:
                best[field] = source_value

        # Dates and academic scores are authoritative in the source record.
        # Explicitly clear a stale engine value when the source record has no
        # value for that field.
        for field in (
            "start_date",
            "end_date",
            "cgpa",
            "percentage",
        ):
            best[field] = source.get(field)

        if best.get("degree"):
            if not best.get("education_level"):
                degree_norm = norm(
                    best.get("degree")
                )

                if "master" in degree_norm:
                    best["education_level"] = "master"

                elif (
                    "bachelor" in degree_norm
                    or "b tech" in degree_norm
                ):
                    best["education_level"] = "bachelor"

                elif (
                    "intermediate" in degree_norm
                    or "higher secondary" in degree_norm
                ):
                    best["education_level"] = "intermediate"

                elif (
                    "secondary school" in degree_norm
                    or "high school" in degree_norm
                ):
                    best["education_level"] = "secondary"

                else:
                    best["education_level"] = (
                        best.get("education_level")
                    )

            best["level"] = (
                best.get("level")
                or best.get("education_level")
            )

        if (
            best.get("start_date")
            and best.get("end_date")
        ):
            best["year"] = (
                f"{best['start_date']}–"
                f"{best['end_date']}"
            )

        reconciled.append(best)

    # Keep engine-only records only when they have an institution that was not
    # recoverable from the source parser. This avoids dropping legitimate
    # unusual education records.
    source_institutions = {
        norm(item.get("institution"))
        for item in source_entries
        if item.get("institution")
    }

    for entry in entries:
        entry_inst = norm(
            entry.get("institution")
        )

        if not entry_inst:
            continue

        if not any(
            entry_inst == source_inst
            or entry_inst in source_inst
            or source_inst in entry_inst
            for source_inst in source_institutions
        ):
            reconciled.append(dict(entry))

    return _merge_education_entries(
        reconciled
    )


def _normalize_education_entries(
    education_result: Dict[str, Any],
    education_text: Any = "",
) -> List[Dict[str, Any]]:
    """Normalize education engine output."""
    raw = (
        education_result.get("entries")
        or education_result.get("education")
        or education_result.get("items")
        or education_result.get("details")
        or []
    )

    entries: List[Dict[str, Any]] = []

    for item in _safe_list(raw):
        if not isinstance(item, dict):
            continue

        normalized = _sanitize_education_entry(
            item
        )

        if normalized:
            entries.append(normalized)

    entries = _merge_education_entries(
        entries
    )

    return _reconcile_education_with_source(
        entries,
        education_text,
    )


def _merge_education_entries(
    entries: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Merge education records describing the same qualification."""
    merged: List[Dict[str, Any]] = []

    def normalize_value(value: Any) -> str:
        if value is None:
            return ""

        return re.sub(
            r"[^a-z0-9]+",
            " ",
            str(value).lower(),
        ).strip()

    for entry in entries:
        degree = normalize_value(
            entry.get("degree")
        )

        institution = normalize_value(
            entry.get("institution")
        )

        if institution or degree:
            key = (
                degree,
                institution,
            )
        else:
            key = (
                normalize_value(
                    entry.get("education_level")
                ),
                entry.get("start_date"),
                entry.get("end_date"),
            )

        existing_index = None

        for index, existing in enumerate(merged):
            existing_key = (
                normalize_value(
                    existing.get("degree")
                ),
                normalize_value(
                    existing.get("institution")
                ),
            )

            if existing_key == key:
                existing_index = index
                break

        if existing_index is None:
            merged.append(dict(entry))
            continue

        existing = merged[existing_index]

        for field, value in entry.items():
            if not value:
                continue

            if not existing.get(field):
                existing[field] = value

    return merged


def _normalize_education_result(
    education_result: Dict[str, Any],
    education_text: Any = "",
) -> Dict[str, Any]:
    """Normalize the complete education result and keep all aliases aligned."""
    result = dict(
        _safe_dict(education_result)
    )

    entries = _normalize_education_entries(
        result,
        education_text,
    )

    result["entries"] = entries
    result["details"] = list(entries)
    result["education"] = list(entries)
    result["count"] = len(entries)
    result["education_found"] = bool(entries)

    result["degree"] = [
        entry.get("degree")
        for entry in entries
        if entry.get("degree")
    ]

    result["institutions"] = [
        entry.get("institution")
        for entry in entries
        if entry.get("institution")
    ]

    result["cgpa"] = [
        str(entry["cgpa"])
        for entry in entries
        if entry.get("cgpa") is not None
    ]

    result["percentage"] = [
        str(entry["percentage"])
        for entry in entries
        if entry.get("percentage") is not None
    ]

    result["timeline"] = [
        [
            entry.get("start_date"),
            entry.get("end_date"),
        ]
        for entry in entries
        if (
            entry.get("start_date")
            or entry.get("end_date")
        )
    ]

    score = _extract_score(
        result,
        "education_score",
        "score",
    )

    result["score"] = score
    result["education_score"] = score

    return result


# ============================================================================
# EXPERIENCE NORMALIZATION
# ============================================================================

def _normalize_experience_entries(
    experience_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    raw = (
        experience_result.get("entries")
        or experience_result.get("experience")
        or experience_result.get("items")
        or []
    )

    entries: List[Dict[str, Any]] = []

    for item in _safe_list(raw):
        if isinstance(item, str):
            if item.strip():
                entries.append(
                    {"title": item.strip()}
                )
            continue

        if not isinstance(item, dict):
            continue

        normalized = dict(item)

        if not any(
            normalized.get(key)
            for key in (
                "title",
                "role",
                "position",
                "company",
                "organization",
            )
        ):
            continue

        entries.append(normalized)

    return _deduplicate_items(
        entries,
        keys=(
            "title",
            "role",
            "company",
            "organization",
        ),
    )


# ============================================================================
# CERTIFICATION NORMALIZATION
# ============================================================================

def _normalize_certification_entries(
    certification_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    raw = (
        certification_result.get("certifications")
        or certification_result.get("entries")
        or certification_result.get("items")
        or certification_result.get("details")
        or []
    )

    entries: List[Dict[str, Any]] = []

    for item in _safe_list(raw):
        if isinstance(item, str):
            if item.strip():
                entries.append(
                    {"name": item.strip()}
                )
            continue

        if not isinstance(item, dict):
            continue

        normalized = dict(item)

        if not any(
            normalized.get(key)
            for key in (
                "name",
                "title",
                "certification",
            )
        ):
            continue

        entries.append(normalized)

    return _deduplicate_items(
        entries,
        keys=(
            "name",
            "title",
            "certification",
        ),
    )


# ============================================================================
# ACHIEVEMENT NORMALIZATION
# ============================================================================

def _normalize_achievement_entries(
    achievement_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    raw = (
        achievement_result.get("achievements")
        or achievement_result.get("entries")
        or achievement_result.get("items")
        or []
    )

    entries: List[Dict[str, Any]] = []

    for item in _safe_list(raw):
        if isinstance(item, str):
            if item.strip():
                entries.append(
                    {"description": item.strip()}
                )
            continue

        if not isinstance(item, dict):
            continue

        normalized = dict(item)

        if any(
            normalized.get(key)
            for key in (
                "description",
                "title",
                "name",
                "achievement",
            )
        ):
            entries.append(normalized)

    return _deduplicate_items(
        entries,
        keys=(
            "description",
            "title",
            "name",
            "achievement",
        ),
    )


# ============================================================================
# GENERIC DEDUPLICATION
# ============================================================================

def _deduplicate_items(
    items: Iterable[Dict[str, Any]],
    keys: Sequence[str],
) -> List[Dict[str, Any]]:
    """Deduplicate dictionaries deterministically."""
    result: List[Dict[str, Any]] = []
    seen = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        values = []

        for key in keys:
            value = item.get(key)

            if value is None:
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                str(value).strip().lower(),
            )

            values.append(normalized)

        if not values:
            continue

        signature = tuple(values)

        if signature in seen:
            continue

        seen.add(signature)
        result.append(item)

    return result


# ============================================================================
# CANDIDATE PROFILE MERGING
# ============================================================================

def _merge_candidate_profile(
    profile: Dict[str, Any],
    *,
    metadata: Dict[str, Any],
    skills: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    education: List[Dict[str, Any]],
    experience: List[Dict[str, Any]],
    certifications: List[Dict[str, Any]],
    achievements: List[Dict[str, Any]],
    metrics: List[str],
) -> Dict[str, Any]:
    """Merge normalized engine information into CandidateProfile."""
    result = dict(profile or {})

    for field in (
        "name",
        "email",
        "phone",
        "link",
        "summary",
    ):
        if not result.get(field):
            value = metadata.get(field)

            if value:
                result[field] = value

    if not result.get("candidate_id"):
        result["candidate_id"] = "anonymous"

    result["skills"] = (
        skills
        if skills
        else _safe_list(
            result.get("skills")
        )
    )

    profile_projects = _safe_list(
        result.get("projects")
    )

    if projects:
        result["projects"] = projects

    elif profile_projects:
        result["projects"] = profile_projects

    else:
        result["projects"] = []

    result["education"] = (
        education
        if education
        else _safe_list(
            result.get("education")
        )
    )

    result["experience"] = (
        experience
        if experience
        else _safe_list(
            result.get("experience")
        )
    )

    result["certifications"] = (
        certifications
        if certifications
        else _safe_list(
            result.get("certifications")
        )
    )

    result["achievements"] = (
        achievements
        if achievements
        else _safe_list(
            result.get("achievements")
        )
    )

    profile_metrics = _safe_list(
        result.get("metrics")
    )

    if metrics:
        combined_metrics = (
            profile_metrics + metrics
        )

        seen = set()
        deduped = []

        for metric in combined_metrics:
            signature = str(
                metric
            ).strip().lower()

            if (
                signature
                and signature not in seen
            ):
                seen.add(signature)
                deduped.append(metric)

        result["metrics"] = deduped

    elif "metrics" not in result:
        result["metrics"] = []

    existing_confidence = _normalize_confidence(
        result.get("confidence")
    )

    if existing_confidence <= 0:
        evidence_count = sum(
            bool(value)
            for value in (
                result.get("skills"),
                result.get("projects"),
                result.get("education"),
                result.get("experience"),
                result.get("certifications"),
                result.get("achievements"),
            )
        )

        result["confidence"] = int(
            min(
                evidence_count * 15,
                90,
            )
        )

    else:
        result["confidence"] = int(
            round(existing_confidence)
        )

    return result


# ============================================================================
# PROJECT ANALYSIS CONSISTENCY
# ============================================================================

def _normalize_project_result_for_analysis(
    project_result: Dict[str, Any],
    project_section_text: Any = "",
) -> Dict[str, Any]:
    """Normalize project analysis before it is exposed or scored.

    The project engine can return valid project evidence with an empty title
    when PDF extraction separates the heading from the body. The source
    Projects section is the authoritative place to recover those titles.
    """
    result = dict(
        _safe_dict(project_result)
    )

    projects = _normalize_project_entries(
        result,
        project_section_text,
    )

    result["projects"] = projects
    result["project_count"] = len(projects)
    result["projects_count"] = len(projects)

    technologies: List[str] = []
    seen = set()

    for project in projects:
        for technology in _safe_list(
            project.get("technologies")
        ):
            value = str(
                technology
            ).strip()

            if not value:
                continue

            signature = re.sub(
                r"\s+",
                " ",
                value.casefold(),
            ).strip()

            if signature in seen:
                continue

            seen.add(signature)
            technologies.append(value)

    result["technologies"] = technologies

    score = _extract_score(
        result,
        "project_score",
        "projects_score",
        "score",
    )

    result["project_score"] = score
    result["projects_score"] = score
    result["score"] = score

    return result


# ============================================================================
# SKILL EVIDENCE CONSISTENCY
# ============================================================================

def _strengthen_explicit_skill_evidence(
    skills_result: Dict[str, Any],
    skills_section_text: Any = "",
) -> Dict[str, Any]:
    """Improve evidence quality when a skill is explicitly listed in Skills.

    An explicit Technical Skills occurrence is stronger evidence than a long
    generic text-window match. We only raise the evidence-quality signal when
    the skill is actually present in the supplied Skills section; no skills or
    evidence are invented.
    """
    result = dict(
        _safe_dict(skills_result)
    )

    details = result.get("skill_details")

    if (
        not isinstance(details, list)
        or not skills_section_text
    ):
        return result

    section = str(
        skills_section_text
    ).casefold()

    normalized_section = re.sub(
        r"[^a-z0-9+#./-]+",
        " ",
        section,
    )

    for detail in details:
        if not isinstance(detail, dict):
            continue

        name = str(
            detail.get("name") or ""
        ).strip()

        if not name:
            continue

        normalized_name = re.sub(
            r"[^a-z0-9+#./-]+",
            " ",
            name.casefold(),
        ).strip()

        if not normalized_name:
            continue

        # Compare against normalized section text so punctuation/casing do not
        # prevent an explicit skills-section match.
        if normalized_name not in normalized_section:
            continue

        try:
            current_quality = float(
                detail.get(
                    "evidence_quality",
                    0,
                )
                or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            current_quality = 0.0

        detail["evidence_quality"] = round(
            min(
                max(current_quality, 0.75),
                1.0,
            ),
            2,
        )

        sources = detail.get("sources")

        if not isinstance(sources, list):
            sources = []
            detail["sources"] = sources

        if "skills" not in [
            str(source).casefold()
            for source in sources
        ]:
            sources.append("skills")

    result["skill_details"] = details

    return result


# ============================================================================
# CANDIDATE PROFILE BUILDER
# ============================================================================

def _build_candidate_profile(
    *,
    metadata: Dict[str, Any],
    skills_result: Dict[str, Any],
    project_result: Dict[str, Any],
    education_result: Dict[str, Any],
    experience_result: Dict[str, Any],
    certification_result: Dict[str, Any],
    achievement_result: Dict[str, Any],
    metrics: List[str],
    project_section_text: Any = "",
    education_text: Any = "",
) -> Dict[str, Any]:
    """Build the final candidate profile."""
    skills = _normalize_skill_entries(
        skills_result
    )

    projects = _normalize_project_entries(
        project_result,
        project_section_text,
    )

    education = _normalize_education_entries(
        education_result,
        education_text,
    )

    experience = _normalize_experience_entries(
        experience_result
    )

    certifications = _normalize_certification_entries(
        certification_result
    )

    achievements = _normalize_achievement_entries(
        achievement_result
    )

    # CandidateProfileBuilder expects the structured engine-analysis
    # contract, not the already-normalized candidate-profile collections.
    #
    # Passing the normalized collections under "skills", "projects",
    # "education", etc. causes CandidateProfileBuilder to look for its
    # *_analysis keys, receive empty/default sections, calculate 0 confidence,
    # and eventually trigger the fallback confidence calculation in
    # _merge_candidate_profile().
    #
    # Keep the original engine results under the exact keys expected by
    # CandidateProfileBuilder so its own confidence calculation can use the
    # actual evidence from every analysis section.
    builder_input = {
        "name": metadata.get("name"),
        "email": metadata.get("email"),
        "phone": metadata.get("phone"),
        "link": metadata.get("link"),
        "summary": metadata.get("summary"),
        "skills_analysis": skills_result,
        "projects_analysis": project_result,
        "experience_analysis": experience_result,
        "education_analysis": education_result,
        "certifications_analysis": certification_result,
        "achievements_analysis": achievement_result,
        "metrics": metrics,
    }

    candidate_id = (
        metadata.get("candidate_id")
        or "anonymous"
    )

    try:
        builder = CandidateProfileBuilder()

        profile = builder.build(
            builder_input,
            candidate_id,
        )

        if hasattr(
            profile,
            "__dataclass_fields__",
        ):
            profile_dict = asdict(
                profile
            )

        elif isinstance(profile, dict):
            profile_dict = dict(
                profile
            )

        else:
            profile_dict = {}

    except Exception:
        profile_dict = {}

    return _merge_candidate_profile(
        profile_dict,
        metadata=metadata,
        skills=skills,
        projects=projects,
        education=education,
        experience=experience,
        certifications=certifications,
        achievements=achievements,
        metrics=metrics,
    )


# ============================================================================
# MAIN ANALYZER
# ============================================================================

def analyze_resume(
    resume_text: Any,
) -> Dict[str, Any]:
    """Analyze a resume end-to-end."""

    # =========================================================================
    # INPUT VALIDATION + NORMALIZATION
    # =========================================================================

    text = _normalize_resume_text(
        resume_text
    )

    # =========================================================================
    # SECTION EXTRACTION
    # =========================================================================

    try:
        sections = extract_sections(text)
    except Exception:
        sections = {}

    sections = _safe_dict(sections)

    try:
        section_detection = detect_sections(
            sections
        )
    except Exception:
        section_detection = {}

    section_detection = _safe_dict(
        section_detection
    )

    # =========================================================================
    # METADATA
    # =========================================================================

    metadata = _extract_resume_metadata(
        text,
        sections,
    )

    # =========================================================================
    # ENGINE ANALYSIS
    # =========================================================================

    # -------------------------------------------------------------------------
    # Skills
    # -------------------------------------------------------------------------

    try:
        raw_skills_result = analyze_skills(
            text,
            sections,
        )

    except TypeError:
        try:
            raw_skills_result = analyze_skills(
                text
            )
        except Exception:
            raw_skills_result = None

    except Exception:
        raw_skills_result = None

    # Preserve the analyzer's historical contract for a missing engine result:
    # if the skill engine returns None (or fails), expose an empty mapping
    # instead of manufacturing a zero-score skill-analysis structure.
    if raw_skills_result is None:
        skills_result = {}

    else:
        skills_result = _normalize_skills_result(
            _safe_dict(raw_skills_result)
        )

        skills_result = _strengthen_explicit_skill_evidence(
            skills_result,
            sections.get(
                "skills",
                "",
            ),
        )

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    try:
        project_result = _safe_dict(
            analyze_projects(
                sections
            )
        )

    except TypeError:
        try:
            project_result = _safe_dict(
                analyze_projects(text)
            )
        except Exception:
            project_result = {}

    except Exception:
        project_result = {
            "score": 0,
            "quality": "Analysis unavailable",
            "project_count": 0,
            "technologies": [],
            "projects": [],
        }

    # Normalize projects at the orchestration boundary so the public
    # project_analysis payload uses the same title recovery logic as the
    # candidate profile. This also keeps project_count/technologies/score
    # aliases synchronized before scoring and serialization.
    project_section_text = sections.get(
        "projects",
        "",
    )

    project_result = _normalize_project_result_for_analysis(
        project_result,
        project_section_text,
    )

    # -------------------------------------------------------------------------
    # ATS
    # -------------------------------------------------------------------------

    try:
        ats_result = _safe_dict(
            analyze_ats(
                text,
                sections,
            )
        )

    except TypeError:
        try:
            ats_result = _safe_dict(
                analyze_ats(text)
            )
        except Exception:
            ats_result = {}

    except Exception:
        ats_result = {}

    # -------------------------------------------------------------------------
    # Experience
    # -------------------------------------------------------------------------

    try:
        experience_result = _safe_dict(
            analyze_experience(
                sections
            )
        )

    except TypeError:
        try:
            experience_result = _safe_dict(
                analyze_experience(text)
            )
        except Exception:
            experience_result = {}

    except Exception:
        experience_result = {}

    # -------------------------------------------------------------------------
    # Certifications
    # -------------------------------------------------------------------------

    try:
        certification_result = _safe_dict(
            analyze_certifications(
                sections
            )
        )

    except TypeError:
        try:
            certification_result = _safe_dict(
                analyze_certifications(text)
            )
        except Exception:
            certification_result = {}

    except Exception:
        certification_result = {}

    # -------------------------------------------------------------------------
    # Education
    # -------------------------------------------------------------------------

    education_text = sections.get(
        "education",
        "",
    )

    try:
        education_result = _safe_dict(
            analyze_education(
                education_text
            )
        )

    except Exception:
        education_result = {
            "score": 0,
            "education_found": False,
            "entries": [],
            "details": [],
        }

    education_result = _normalize_education_result(
        education_result,
        education_text,
    )

    # =========================================================================
    # ACHIEVEMENTS
    # =========================================================================

    achievement_text = sections.get(
        "achievements",
        "",
    )

    achievement_result = (
        _calculate_achievement_score(
            achievement_text
        )
    )

    achievement_result["achievements"] = []

    # =========================================================================
    # METRICS
    # =========================================================================

    metrics = _extract_metrics(text)

    # =========================================================================
    # SCORE INPUT
    # =========================================================================

    score_input = _build_score_input(
        skills=skills_result,
        projects=project_result,
        ats=ats_result,
        experience=experience_result,
        certifications=certification_result,
        education=education_result,
        achievements=achievement_result,
    )

    # =========================================================================
    # SCORE CALCULATION
    # =========================================================================

    try:
        score_result = calculate_score(
            score_input["skills_score"],
            score_input["project_score"],
            score_input["experience_score"],
            score_input["ats_score"],
            score_input["certification_score"],
            score_input["education_score"],
            score_input["achievement_score"],
        )

    except TypeError:
        try:
            score_result = calculate_score(
                **score_input
            )
        except Exception:
            score_result = {}

    except Exception:
        score_result = {}

    score_result = _safe_dict(
        score_result
    )

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    # The scoring engine's recommendation API consumes the numeric component
    # scores directly. Rich engine output is still supplied alongside those
    # scores because the recommendation helpers use it for evidence such as
    # missing ATS keywords, project metrics, deployment evidence, experience,
    # and achievements.
    recommendation_input = {
        "skills": score_input.get(
            "skills_score",
            0,
        ),
        "projects": score_input.get(
            "project_score",
            0,
        ),
        "experience": score_input.get(
            "experience_score",
            0,
        ),
        "ats": score_input.get(
            "ats_score",
            0,
        ),
        "certifications": score_input.get(
            "certification_score",
            0,
        ),
        "education": score_input.get(
            "education_score",
            0,
        ),
        "achievements": score_input.get(
            "achievement_score",
            0,
        ),

        "skills_analysis": skills_result,
        "project_analysis": project_result,
        "ats_analysis": ats_result,
        "experience_analysis": experience_result,
        "certification_analysis": certification_result,
        "education_analysis": education_result,
        "achievement_analysis": achievement_result,
        "metrics": metrics,
        "score_breakdown": score_result,
    }

    try:
        recommendations = generate_recommendations(
            recommendation_input
        )
    except Exception:
        recommendations = []

    if not isinstance(
        recommendations,
        list,
    ):
        recommendations = []

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    confidence = _calculate_confidence(
        text=text,
        sections=sections,
        skills=skills_result,
        projects=project_result,
        ats=ats_result,
        experience=experience_result,
        education=education_result,
        certifications=certification_result,
    )

    # =========================================================================
    # CANDIDATE PROFILE
    # =========================================================================

    project_section_text = sections.get(
        "projects",
        "",
    )

    candidate_profile = _build_candidate_profile(
        metadata=metadata,
        skills_result=skills_result,
        project_result=project_result,
        education_result=education_result,
        experience_result=experience_result,
        certification_result=certification_result,
        achievement_result=achievement_result,
        metrics=metrics,
        project_section_text=project_section_text,
        education_text=education_text,
    )

    # =========================================================================
    # FINAL SCORE
    # =========================================================================

    final_score = _safe_score(
        score_result.get(
            "resume_intelligence_score",
            score_result.get(
                "score",
                0,
            ),
        )
    )

    rating = (
        score_result.get("rating")
        or score_result.get("quality")
        or (
            "Excellent"
            if final_score >= 85
            else "Strong"
            if final_score >= 75
            else "Good"
            if final_score >= 60
            else "Needs Improvement"
        )
    )

    # =========================================================================
    # FINAL RESPONSE
    # =========================================================================

    return {
        "resume_intelligence_score": final_score,
        "rating": rating,
        "confidence": confidence,

        "sections": {
            **section_detection,
        },

        "sections_detected": section_detection,

        "metadata": metadata,

        "skills_analysis": skills_result,

        "project_analysis": project_result,

        "ats_analysis": ats_result,

        "experience_analysis": experience_result,

        "certification_analysis": certification_result,

        "certifications": certification_result,

        "education_analysis": education_result,

        "education": education_result,

        "achievement_analysis": achievement_result,

        "metrics_found": metrics,

        "score_breakdown": score_result,

        "candidate_profile": candidate_profile,

        "recommendations": recommendations,

        "analysis_version": "5.4",
    }


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "analyze_resume",
]