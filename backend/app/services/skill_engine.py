"""
ResumeIQ - Production Skill Intelligence Engine v5.5

Purpose
-------

Detect demonstrated technical skills from meaningful resume sections.

Important
---------

ATS keyword matching remains completely separate and belongs to
ats_engine.py.

Canonical skill definitions are owned exclusively by keyword_db.py.

Evidence philosophy
-------------------

A skill declaration in a Skills/Technologies section is useful evidence,
but actual implementation evidence is stronger.

Evidence priority:

    experience / internship
        >
    projects
        >
    summary
        >
    skills

Within a section, implementation/action evidence is preferred over a
plain technology declaration.

This prevents output such as:

    evidence = "Technologies: Python, TensorFlow, Pandas, Git"

from incorrectly becoming the primary evidence when the resume also says:

    "Built and trained a TensorFlow model using Python..."
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from .keyword_db import (
    CATEGORY_MAP,
    DEMONSTRATED_SKILL_SECTIONS,
    INDUSTRY_SKILLS,
    get_canonical_skill,
)
from .patterns import PERCENT_METRIC_PATTERN
from .utils import normalize_text


# =====================================================================
# VERSION
# =====================================================================

ANALYSIS_VERSION = "5.5"


# =====================================================================
# CONFIGURATION
# =====================================================================

SECTION_WEIGHTS: Dict[str, float] = {
    "experience": 1.00,
    "internship": 1.00,
    "projects": 0.95,
    "summary": 0.65,
    "skills": 0.55,
    "resume": 0.40,
}

EVIDENCE_SOURCE_PRIORITY: Dict[str, int] = {
    "experience": 5,
    "internship": 5,
    "projects": 4,
    "summary": 2,
    "skills": 1,
    "resume": 0,
}

MAX_EVIDENCE_PER_SKILL = 3
MAX_EVIDENCE_LENGTH = 180

# Complete logical sentences/bullets are allowed a larger limit so that
# meaningful evidence is not destroyed merely because PDF extraction
# wrapped the sentence across multiple physical lines.
MAX_COMPLETE_EVIDENCE_LENGTH = 320

MIN_SUMMARY_EVIDENCE_QUALITY = 0.50
MIN_FALLBACK_EVIDENCE_QUALITY = 0.70
SKILLS_SECTION_BASE_CONFIDENCE = 0.68


# =====================================================================
# TECHNICAL ACTION LANGUAGE
# =====================================================================

TECHNICAL_ACTION_WORDS = (
    "built",
    "developed",
    "designed",
    "implemented",
    "deployed",
    "integrated",
    "trained",
    "created",
    "configured",
    "used",
    "using",
    "worked",
    "applied",
    "automated",
    "optimized",
    "managed",
    "engineered",
    "programmed",
    "maintained",
    "architected",
    "constructed",
    "developing",
    "implementing",
    "deploying",
    "testing",
    "tested",
    "evaluated",
)


# =====================================================================
# TECHNICAL CONTEXT
# =====================================================================

TECHNICAL_CONTEXT_WORDS = (
    "application",
    "model",
    "system",
    "api",
    "database",
    "server",
    "deployment",
    "pipeline",
    "framework",
    "algorithm",
    "dataset",
    "platform",
    "service",
    "cloud",
    "backend",
    "frontend",
    "infrastructure",
    "project",
    "software",
    "architecture",
    "repository",
    "website",
    "web app",
    "prediction",
    "classification",
    "training",
    "preprocessing",
    "feature",
    "integration",
    "testing",
)


# =====================================================================
# TECHNOLOGY DECLARATION PATTERNS
# =====================================================================

TECHNOLOGY_LINE_PATTERNS = (
    r"^\s*\**technologies?\s*\*?:",
    r"^\s*\**tech\s*stack\s*\*?:",
    r"^\s*\**tools?\s*\*?:",
    r"^\s*\**frameworks?\s*\*?:",
    r"^\s*\**libraries\s*\*?:",
)


# =====================================================================
# SKILLS DECLARATION PATTERNS
# =====================================================================

SKILLS_DECLARATION_LINE_PATTERNS = (
    r"^\s*\**languages?\s*(?:&|and)\s*databases?\s*\**\s*:",
    r"^\s*\**machine\s+learning\s*(?:&|and)\s*frameworks?\s*\**\s*:",
    r"^\s*\**developer\s+tools?\s*\**\s*:",
    r"^\s*\**core\s+concepts?\s*(?:&|and)\s*soft\s+skills?\s*\**\s*:",
)


# =====================================================================
# CATEGORY OWNERSHIP PRIORITY
# =====================================================================

CATEGORY_PRIORITY = (
    "Programming",
    "Frontend",
    "Backend",
    "Database",
    "AI/ML",
    "Tools",
    "Engineering",
    "Blockchain",
    "Professional",
)


# =====================================================================
# NORMALIZATION
# =====================================================================

def _normalize(value: Any) -> str:
    """
    Convert arbitrary values into normalized searchable text.

    Line boundaries are intentionally preserved because evidence
    extraction reconstructs logical resume bullets from them.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return _normalize_preserving_lines(value)

    if isinstance(value, list):
        parts: List[str] = []

        for item in value:
            if item is None:
                continue

            normalized = _normalize_preserving_lines(str(item))

            if normalized:
                parts.append(normalized)

        return "\n".join(parts).strip()

    if isinstance(value, dict):
        parts: List[str] = []

        for item in value.values():
            if item is None:
                continue

            normalized = _normalize_preserving_lines(str(item))

            if normalized:
                parts.append(normalized)

        return "\n".join(parts).strip()

    return _normalize_preserving_lines(str(value))


def _normalize_preserving_lines(value: str) -> str:
    """
    Normalize text while preserving meaningful line boundaries.
    """
    if not value:
        return ""

    lines: List[str] = []

    for raw_line in str(value).splitlines():
        line = normalize_text(raw_line)

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


# =====================================================================
# REGEX
# =====================================================================

def _skill_pattern(skill: str) -> re.Pattern[str]:
    """
    Build a safe regex for a canonical skill.
    """
    canonical = get_canonical_skill(skill)

    if not canonical:
        return re.compile(r"(?!x)x")

    escaped = re.escape(canonical)

    if canonical.casefold() in {
        "r",
        "go",
        "c",
        "c++",
        "c#",
    }:
        return re.compile(
            rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )

    if any(
        symbol in canonical
        for symbol in (
            "+",
            "#",
            ".",
            "/",
        )
    ):
        return re.compile(
            rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )

    return re.compile(
        rf"\b{escaped}\b",
        re.IGNORECASE,
    )


def _contains_skill(
    text: str,
    skill: str,
) -> bool:
    """
    Return True when a canonical skill appears as a real token.
    """
    if not text or not skill:
        return False

    return bool(
        _skill_pattern(skill).search(text)
    )


# =====================================================================
# SECTION HANDLING
# =====================================================================

def _build_evidence_sections(
    sections: Dict[str, Any],
) -> Dict[str, str]:
    """
    Build evidence only from sections explicitly allowed to establish
    demonstrated skills.

    Education, certifications and achievements are intentionally
    excluded.

    Physical line boundaries are preserved initially. Evidence
    extraction later reconstructs logical bullets/sentences.
    """
    evidence: Dict[str, str] = {}

    for section_name in DEMONSTRATED_SKILL_SECTIONS:
        value = sections.get(section_name)
        normalized = _normalize(value)

        if not normalized:
            continue

        evidence[section_name] = normalized

    return evidence


def _build_safe_fallback(
    full_text: str,
    sections: Dict[str, Any],
) -> Dict[str, str]:
    """
    Use complete resume text only when section extraction produced
    no usable evidence sections.
    """
    if sections:
        return {}

    if full_text:
        return {
            "resume": _normalize_preserving_lines(full_text),
        }

    return {}


# =====================================================================
# EVIDENCE CLEANING
# =====================================================================

def _clean_evidence(value: str) -> str:
    """
    Clean extracted evidence while preserving useful text.
    """
    if not value:
        return ""

    cleaned = re.sub(
        r"[\x00-\x1F\x7F]",
        " ",
        value,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    if len(cleaned) < 8:
        return ""

    return cleaned


def _evidence_dedupe_key(value: str) -> str:
    """
    Build a stable comparison key for evidence.

    Evidence that differs only by:

        - capitalization
        - whitespace
        - punctuation

    is considered the same evidence.
    """
    cleaned = _clean_evidence(value)

    if not cleaned:
        return ""

    key = cleaned.casefold()

    key = re.sub(
        r"[^\w\s]",
        " ",
        key,
    )

    key = re.sub(
        r"\s+",
        " ",
        key,
    ).strip()

    return key


def _is_technology_only_line(
    evidence: str,
) -> bool:
    """
    Detect evidence that is essentially a technology declaration.

    Example:

        Technologies: Python, TensorFlow, Pandas, Git

    This is valid resume evidence, but weaker than:

        Built a TensorFlow model using Python.
    """
    if not evidence:
        return False

    text = evidence.strip()

    if any(
        re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
        for pattern in TECHNOLOGY_LINE_PATTERNS
    ):
        return True

    return any(
        re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
        for pattern in SKILLS_DECLARATION_LINE_PATTERNS
    )


# =====================================================================
# LOGICAL RESUME EVIDENCE UNITS
# =====================================================================

def _line_starts_new_evidence_unit(
    line: str,
) -> bool:
    """
    Determine whether a physical line most likely starts a new
    resume bullet/evidence unit.

    PDF/text extraction often wraps one sentence across multiple
    physical lines. We therefore cannot treat every newline as a
    sentence boundary.

    A new unit is strongly indicated by:

        - bullet markers
        - action verbs
        - technology declaration labels
        - skills category declaration labels
        - common resume headings
    """
    if not line:
        return False

    text = line.strip()

    # Common bullet markers.
    if re.match(
        r"^(?:[-•▪◦●○*]\s+)",
        text,
    ):
        return True

    # Remove a leading bullet marker before checking the first word.
    cleaned = re.sub(
        r"^(?:[-•▪◦●○*]\s+)+",
        "",
        text,
    ).strip()

    # Technology declaration lines are independent units.
    if _is_technology_only_line(cleaned):
        return True

    # Explicit skills category declarations are independent units.
    if any(
        re.search(
            pattern,
            cleaned,
            re.IGNORECASE,
        )
        for pattern in SKILLS_DECLARATION_LINE_PATTERNS
    ):
        return True

    # Common action-led resume bullets.
    action_pattern = (
        r"^(?:"
        + "|".join(
            re.escape(word)
            for word in TECHNICAL_ACTION_WORDS
        )
        + r")\b"
    )

    if re.search(
        action_pattern,
        cleaned,
        re.IGNORECASE,
    ):
        return True

    # Common resume section labels.
    if re.match(
        r"^(?:"
        r"technologies?|"
        r"tech\s*stack|"
        r"skills?|"
        r"tools?|"
        r"frameworks?|"
        r"libraries?|"
        r"responsibilities?|"
        r"achievements?|"
        r"certifications?"
        r")\s*:?\s*$",
        cleaned,
        re.IGNORECASE,
    ):
        return True

    return False


def _build_logical_evidence_units(
    text: str,
) -> List[Tuple[int, int, str]]:
    """
    Reconstruct logical evidence units from PDF-extracted text.

    A single resume sentence may physically appear as:

        Applied data preprocessing and feature engineering techniques
        using Python to improve model quality and
        prediction performance.

    This function reconstructs it into:

        Applied data preprocessing and feature engineering techniques
        using Python to improve model quality and prediction performance.

    Separate action bullets remain separate:

        Designed a machine learning system...
        Simulated collaborative model training...
        Applied data preprocessing...

    Returns:
        (start_offset, end_offset, cleaned_text)
    """
    if not text:
        return []

    raw_lines = text.splitlines()

    units: List[Tuple[int, int, str]] = []

    current_start: int | None = None
    current_end: int | None = None
    current_parts: List[str] = []

    offset = 0

    def flush_current() -> None:
        nonlocal current_start
        nonlocal current_end
        nonlocal current_parts

        if current_start is None:
            current_parts = []
            current_end = None
            return

        combined = _clean_evidence(
            " ".join(current_parts)
        )

        if combined:
            units.append(
                (
                    current_start,
                    current_end
                    if current_end is not None
                    else current_start + len(combined),
                    combined,
                )
            )

        current_start = None
        current_end = None
        current_parts = []

    for raw_line in raw_lines:
        line = raw_line.strip()

        line_start = offset
        line_end = offset + len(raw_line)

        # Advance offset including the newline.
        offset = line_end + 1

        if not line:
            flush_current()
            continue

        starts_new = _line_starts_new_evidence_unit(
            line
        )

        # If this is clearly a new bullet/action/declaration line,
        # finalize the previous wrapped sentence first.
        if starts_new and current_parts:
            flush_current()

        if current_start is None:
            current_start = line_start

        current_parts.append(line)
        current_end = line_end

        # If the physical line itself ends a sentence, finalize it.
        #
        # Do NOT require this for every bullet because PDF extraction
        # frequently removes punctuation from intermediate lines.
        if re.search(
            r"[.!?;:]\s*$",
            line,
        ):
            flush_current()

    flush_current()

    return units


def _extract_logical_unit_for_match(
    text: str,
    start: int,
    end: int,
) -> str:
    """
    Return the logical resume evidence unit containing a skill match.
    """
    units = _build_logical_evidence_units(text)

    for unit_start, unit_end, evidence in units:
        if (
            unit_start <= start < unit_end
            or unit_start < end <= unit_end
            or start <= unit_start < end
        ):
            return evidence

    return _extract_line_evidence(
        text,
        start,
        end,
    )


# =====================================================================
# SKILLS-SECTION-SPECIFIC EVIDENCE
# =====================================================================

def _extract_skills_declaration_evidence_candidates(
    text: str,
    skill: str,
) -> List[str]:
    """
    Extract skill-specific evidence from a Technical Skills section.

    The old implementation could treat the entire Technical Skills
    section as one logical evidence unit, producing evidence such as:

        Languages & Databases: Python, SQL...
        Machine Learning & Frameworks: TensorFlow...
        Developer Tools: Git...

    for every skill.

    This implementation treats each skills category line as its own
    declaration and checks only the value after the category label.

    This also prevents a category heading such as:

        Machine Learning & Frameworks:

    from falsely demonstrating the `machine learning` skill.
    """
    if not text or not skill:
        return []

    pattern = _skill_pattern(skill)
    candidates: List[str] = []

    logical_units = _build_logical_evidence_units(
        text
    )

    for _, _, evidence in logical_units:
        if not evidence:
            continue

        # Only inspect explicit skills declaration units.
        if not any(
            re.search(
                declaration_pattern,
                evidence,
                re.IGNORECASE,
            )
            for declaration_pattern in SKILLS_DECLARATION_LINE_PATTERNS
        ):
            continue

        # Split the declaration from its value.
        #
        # Example:
        #   Developer Tools: Git, GitHub, Visual Studio Code
        #
        # becomes:
        #   label = Developer Tools
        #   value = Git, GitHub, Visual Studio Code
        parts = re.split(
            r":\s*",
            evidence,
            maxsplit=1,
        )

        if len(parts) != 2:
            continue

        value = _clean_evidence(parts[1])

        if not value:
            continue

        # Critical: match only the value, never the category heading.
        if not pattern.search(value):
            continue

        candidates.append(
            _clean_evidence(evidence)
        )

        if len(candidates) >= 6:
            break

    unique_candidates: List[str] = []
    seen_keys = set()

    for candidate in candidates:
        key = _evidence_dedupe_key(candidate)

        if not key or key in seen_keys:
            continue

        seen_keys.add(key)
        unique_candidates.append(candidate)

    return unique_candidates


# =====================================================================
# EVIDENCE EXTRACTION
# =====================================================================

def _extract_line_evidence(
    text: str,
    start: int,
    end: int,
) -> str:
    """
    Extract the complete physical line containing a matched skill.

    This remains as a defensive fallback. Normal evidence extraction
    uses logical resume units instead.
    """
    line_start = text.rfind(
        "\n",
        0,
        start,
    )

    line_end = text.find(
        "\n",
        end,
    )

    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    if line_end == -1:
        line_end = len(text)

    return _clean_evidence(
        text[line_start:line_end]
    )


def _extract_sentence_evidence(
    text: str,
    start: int,
    end: int,
) -> str:
    """
    Extract the logical sentence/bullet containing a matched skill.

    This method deliberately reconstructs wrapped physical lines
    before performing sentence extraction.
    """
    logical_evidence = _extract_logical_unit_for_match(
        text,
        start,
        end,
    )

    if not logical_evidence:
        return ""

    return _clean_evidence(
        logical_evidence
    )


def _extract_evidence_candidates(
    text: str,
    skill: str,
    source: str | None = None,
) -> List[str]:
    """
    Extract multiple useful evidence candidates for a skill.

    Evidence is reconstructed from logical resume units rather than
    raw physical lines, preventing PDF wrapping from creating
    truncated fragments.

    For the `skills` source, declaration lines are handled specially
    so that each skill receives only the relevant Technical Skills
    category line rather than the entire skills block.
    """
    if not text or not skill:
        return []

    if source == "skills":
        return _extract_skills_declaration_evidence_candidates(
            text,
            skill,
        )

    pattern = _skill_pattern(skill)

    candidates: List[str] = []

    logical_units = _build_logical_evidence_units(
        text
    )

    # -----------------------------------------------------------------
    # Primary path: find skills within reconstructed logical units.
    # -----------------------------------------------------------------
    for (
        unit_start,
        unit_end,
        evidence,
    ) in logical_units:
        if not evidence:
            continue

        if not pattern.search(evidence):
            continue

        cleaned = _clean_evidence(evidence)

        if not cleaned:
            continue

        candidates.append(cleaned)

        if len(candidates) >= 6:
            break

    # -----------------------------------------------------------------
    # Defensive fallback for unusual text structures.
    # -----------------------------------------------------------------
    if not candidates:
        for match in pattern.finditer(text):
            line_evidence = _extract_line_evidence(
                text,
                match.start(),
                match.end(),
            )

            sentence_evidence = _extract_sentence_evidence(
                text,
                match.start(),
                match.end(),
            )

            if line_evidence:
                candidates.append(
                    line_evidence
                )

            if sentence_evidence:
                candidates.append(
                    sentence_evidence
                )

            if len(candidates) >= 6:
                break

    # -----------------------------------------------------------------
    # Stable punctuation-insensitive de-duplication.
    # -----------------------------------------------------------------
    unique_candidates: List[str] = []
    seen_keys = set()

    for candidate in candidates:
        key = _evidence_dedupe_key(candidate)

        if not key:
            continue

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_candidates.append(candidate)

    return unique_candidates


# =====================================================================
# EVIDENCE LENGTH HANDLING
# =====================================================================

def _is_complete_logical_evidence(
    evidence: str,
) -> bool:
    """
    Determine whether evidence looks like a complete logical sentence
    or bullet rather than a fragment.

    Complete project/action sentences are allowed to exceed the legacy
    180-character snippet limit so meaningful evidence is not replaced
    with an artificial `...` truncation.
    """
    if not evidence:
        return False

    cleaned = _clean_evidence(evidence)

    if not cleaned:
        return False

    if not re.search(
        r"[.!?]\s*$",
        cleaned,
    ):
        return False

    return _has_technical_action(cleaned)


def _truncate_evidence(
    evidence: str,
) -> str:
    """
    Apply deterministic evidence length limits.

    Normal evidence retains the historical 180-character limit.

    A complete logical action sentence/bullet may use the larger
    MAX_COMPLETE_EVIDENCE_LENGTH limit. If that larger limit is still
    exceeded, truncation happens at a word boundary.
    """
    cleaned = _clean_evidence(evidence)

    if not cleaned:
        return ""

    if _is_complete_logical_evidence(cleaned):
        limit = MAX_COMPLETE_EVIDENCE_LENGTH
    else:
        limit = MAX_EVIDENCE_LENGTH

    if len(cleaned) <= limit:
        return cleaned

    truncated = cleaned[: limit - 3].rstrip()

    # Prefer a clean word boundary.
    if " " in truncated:
        truncated = truncated.rsplit(
            " ",
            1,
        )[0].rstrip()

    return truncated + "..."


def _extract_evidence(
    text: str,
    skill: str,
    source: str | None = None,
) -> str:
    """
    Return the strongest local evidence candidate for a skill.
    """
    candidates = _extract_evidence_candidates(
        text,
        skill,
        source=source,
    )

    if not candidates:
        return ""

    ranked = sorted(
        candidates,
        key=lambda item: (
            _is_technology_only_line(item),
            -_evidence_quality(
                item,
                skill,
            ),
            -len(item),
        ),
    )

    evidence = ranked[0]

    return _truncate_evidence(
        evidence
    )


# =====================================================================
# EVIDENCE QUALITY
# =====================================================================

def _has_technical_action(
    evidence: str,
) -> bool:
    """
    Detect meaningful technical action language.
    """
    if not evidence:
        return False

    text = evidence.casefold()

    return any(
        re.search(
            rf"\b{re.escape(word)}\b",
            text,
        )
        for word in TECHNICAL_ACTION_WORDS
    )


def _technical_context_hits(
    evidence: str,
) -> int:
    """
    Count meaningful technical context signals.
    """
    if not evidence:
        return 0

    text = evidence.casefold()

    return sum(
        1
        for word in TECHNICAL_CONTEXT_WORDS
        if re.search(
            rf"\b{re.escape(word)}\b",
            text,
        )
    )


def _evidence_quality(
    evidence: str,
    skill: str,
) -> float:
    """
    Estimate how strongly evidence demonstrates actual use.

    0.0 -> no useful evidence
    1.0 -> very strong technical evidence
    """
    if not evidence or not skill:
        return 0.0

    text = evidence.casefold()
    score = 0.30

    # ---------------------------------------------------------------
    # Technology declaration
    # ---------------------------------------------------------------

    if _is_technology_only_line(evidence):
        return 0.38

    # ---------------------------------------------------------------
    # Technical action
    # ---------------------------------------------------------------

    if _has_technical_action(evidence):
        score += 0.30

    # ---------------------------------------------------------------
    # Technical context
    # ---------------------------------------------------------------

    context_hits = _technical_context_hits(
        evidence
    )

    score += min(
        context_hits * 0.08,
        0.24,
    )

    # ---------------------------------------------------------------
    # Quantitative evidence
    # ---------------------------------------------------------------

    if PERCENT_METRIC_PATTERN.search(text):
        score += 0.08

    # ---------------------------------------------------------------
    # Strong engineering technologies
    # ---------------------------------------------------------------

    if re.search(
        r"\b(?:api|ec2|s3|lambda|docker|kubernetes|"
        r"fastapi|flask|tensorflow|pytorch|"
        r"postgresql|mysql|mongodb|redis|"
        r"git|github|ci/cd)\b",
        text,
    ):
        score += 0.08

    return round(
        min(score, 1.0),
        2,
    )


# =====================================================================
# EVIDENCE RANKING
# =====================================================================

def _evidence_strength(
    source: str,
    evidence: str,
    skill: str,
) -> float:
    """
    Calculate deterministic ranking score for evidence.

    Implementation evidence receives a stronger score than technology
    declarations from the same section.
    """
    source_priority = EVIDENCE_SOURCE_PRIORITY.get(
        source,
        0,
    )

    quality = _evidence_quality(
        evidence,
        skill,
    )

    score = (
        source_priority * 10.0
        + quality * 5.0
    )

    if _is_technology_only_line(evidence):
        score -= 3.0

    if _has_technical_action(evidence):
        score += 1.5

    return score


def _rank_evidence(
    evidence_items: List[Dict[str, Any]],
    skill: str,
) -> List[Dict[str, Any]]:
    """
    Rank evidence from strongest to weakest.
    """
    return sorted(
        evidence_items,
        key=lambda item: (
            -_evidence_strength(
                str(item.get("source", "")),
                str(item.get("evidence", "")),
                skill,
            ),
            str(item.get("source", "")),
            str(item.get("evidence", "")),
        ),
    )


def _select_evidence(
    evidence_items: List[Dict[str, Any]],
    skill: str,
) -> List[Dict[str, Any]]:
    """
    Select the strongest evidence while preventing weak declarations
    from crowding out actual implementation evidence.

    Rules:

    1. Prefer non-technology evidence over technology declarations.

    2. Prefer stronger resume sections.

    3. If professional/project evidence exists, do not automatically
       add a weaker Skills-section declaration.

    4. Preserve independent stronger sources when useful.

    5. Deduplicate evidence using punctuation-insensitive comparison.
    """
    if not evidence_items:
        return []

    ranked = _rank_evidence(
        evidence_items,
        skill,
    )

    # Stable de-duplication of source/evidence pairs.
    unique_items: List[Dict[str, Any]] = []
    seen_pairs = set()

    for item in ranked:
        source = str(
            item.get("source", "")
        ).strip()

        evidence = _clean_evidence(
            str(
                item.get(
                    "evidence",
                    "",
                )
            )
        )

        if not source or not evidence:
            continue

        pair = (
            source,
            _evidence_dedupe_key(evidence),
        )

        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)

        unique_items.append(
            {
                "source": source,
                "evidence": evidence,
            }
        )

    if not unique_items:
        return []

    # ---------------------------------------------------------------
    # First determine whether actual implementation evidence exists.
    # ---------------------------------------------------------------

    implementation_items = [
        item
        for item in unique_items
        if not _is_technology_only_line(
            str(item.get("evidence", ""))
        )
    ]

    professional_items = [
        item
        for item in implementation_items
        if str(item.get("source", ""))
        in {
            "experience",
            "internship",
            "projects",
        }
    ]

    # ---------------------------------------------------------------
    # If actual professional/project evidence exists, use it as the
    # primary evidence pool.
    # ---------------------------------------------------------------

    if professional_items:
        pool = professional_items

        selected: List[Dict[str, Any]] = []
        seen_sources = set()
        seen_evidence = set()

        # Prefer independent professional/project sources.
        for item in pool:
            source = str(
                item.get("source", "")
            )

            evidence = str(
                item.get("evidence", "")
            )

            evidence_key = _evidence_dedupe_key(
                evidence
            )

            if source in seen_sources:
                continue

            if evidence_key in seen_evidence:
                continue

            selected.append(item)
            seen_sources.add(source)
            seen_evidence.add(evidence_key)

            if len(selected) >= MAX_EVIDENCE_PER_SKILL:
                break

        # If fewer than the maximum are available, fill with remaining
        # implementation evidence from the same pool.
        if len(selected) < MAX_EVIDENCE_PER_SKILL:
            for item in pool:
                if item in selected:
                    continue

                evidence_key = _evidence_dedupe_key(
                    str(
                        item.get(
                            "evidence",
                            "",
                        )
                    )
                )

                if evidence_key in seen_evidence:
                    continue

                selected.append(item)
                seen_evidence.add(evidence_key)

                if len(selected) >= MAX_EVIDENCE_PER_SKILL:
                    break

        return selected

    # ---------------------------------------------------------------
    # If there is no professional/project implementation evidence,
    # retain the strongest available evidence.
    # ---------------------------------------------------------------

    if implementation_items:
        selected: List[Dict[str, Any]] = []
        seen_evidence = set()

        for item in implementation_items:
            key = _evidence_dedupe_key(
                str(
                    item.get(
                        "evidence",
                        "",
                    )
                )
            )

            if not key or key in seen_evidence:
                continue

            seen_evidence.add(key)
            selected.append(item)

            if len(selected) >= MAX_EVIDENCE_PER_SKILL:
                break

        return selected

    # ---------------------------------------------------------------
    # Technology declarations are valid fallback evidence.
    # ---------------------------------------------------------------

    selected = []
    seen_evidence = set()

    for item in unique_items:
        key = _evidence_dedupe_key(
            str(
                item.get(
                    "evidence",
                    "",
                )
            )
        )

        if not key or key in seen_evidence:
            continue

        seen_evidence.add(key)
        selected.append(item)

        if len(selected) >= MAX_EVIDENCE_PER_SKILL:
            break

    return selected


# =====================================================================
# DEMONSTRATED SKILL DECISION
# =====================================================================

def _is_demonstrated_skill(
    sources: List[str],
    evidence: List[str],
    skill: str,
) -> bool:
    """
    Determine whether the resume provides enough evidence to call a
    skill demonstrated.
    """
    if not sources:
        return False

    source_set = set(sources)

    # ---------------------------------------------------------------
    # Professional/project evidence
    # ---------------------------------------------------------------

    if source_set & {
        "experience",
        "internship",
        "projects",
    }:
        return True

    # ---------------------------------------------------------------
    # Skills declaration
    # ---------------------------------------------------------------

    if "skills" in source_set:
        return True

    # ---------------------------------------------------------------
    # Summary evidence
    # ---------------------------------------------------------------

    if "summary" in source_set:
        quality = max(
            (
                _evidence_quality(
                    item,
                    skill,
                )
                for item in evidence
            ),
            default=0.0,
        )

        return (
            quality
            >= MIN_SUMMARY_EVIDENCE_QUALITY
        )

    # ---------------------------------------------------------------
    # Safe fallback
    # ---------------------------------------------------------------

    if "resume" in source_set:
        quality = max(
            (
                _evidence_quality(
                    item,
                    skill,
                )
                for item in evidence
            ),
            default=0.0,
        )

        return (
            quality
            >= MIN_FALLBACK_EVIDENCE_QUALITY
        )

    return False


# =====================================================================
# CONFIDENCE
# =====================================================================

def _confidence_from_sources(
    sources: List[str],
    evidence: List[str],
    skill: str,
) -> Tuple[str, float]:
    """
    Calculate evidence-based confidence.

    Confidence describes how strongly ResumeIQ can establish that the
    candidate demonstrated the skill.

    It does NOT mean actual proficiency level.
    """
    if not sources:
        return "None", 0.0

    normalized_sources = set(sources)

    professional_sources = (
        normalized_sources
        & {
            "experience",
            "internship",
            "projects",
        }
    )

    quality = max(
        (
            _evidence_quality(
                item,
                skill,
            )
            for item in evidence
        ),
        default=0.0,
    )

    # ---------------------------------------------------------------
    # Base confidence
    # ---------------------------------------------------------------

    if (
        "experience" in normalized_sources
        or "internship" in normalized_sources
    ):
        base_confidence = 0.88

    elif "projects" in normalized_sources:
        base_confidence = 0.82

    elif normalized_sources == {"skills"}:
        base_confidence = (
            SKILLS_SECTION_BASE_CONFIDENCE
        )

    elif normalized_sources == {"summary"}:
        base_confidence = 0.62

    elif normalized_sources == {"resume"}:
        base_confidence = 0.55

    else:
        base_confidence = max(
            SECTION_WEIGHTS.get(
                source,
                0.50,
            )
            for source in normalized_sources
        )

    # ---------------------------------------------------------------
    # Evidence quality adjustment
    # ---------------------------------------------------------------

    if professional_sources:
        base_confidence += min(
            max(
                quality - 0.50,
                0.0,
            )
            * 0.20,
            0.10,
        )

    elif normalized_sources == {"skills"}:
        base_confidence += min(
            max(
                quality - 0.30,
                0.0,
            )
            * 0.10,
            0.05,
        )

    # ---------------------------------------------------------------
    # Technology-only evidence
    # ---------------------------------------------------------------

    technology_only_evidence = (
        bool(evidence)
        and all(
            _is_technology_only_line(item)
            for item in evidence
        )
    )

    if technology_only_evidence:
        if (
            normalized_sources == {"projects"}
        ):
            base_confidence = min(
                base_confidence,
                0.69,
            )

        elif normalized_sources == {"skills"}:
            base_confidence = min(
                base_confidence,
                0.73,
            )

    # ---------------------------------------------------------------
    # Penalize weak project evidence.
    # ---------------------------------------------------------------

    if (
        "projects" in normalized_sources
        and quality < 0.50
        and professional_sources == {"projects"}
    ):
        base_confidence -= 0.08

    # ---------------------------------------------------------------
    # Multiple independent sections.
    # ---------------------------------------------------------------

    source_count_bonus = min(
        max(
            len(normalized_sources) - 1,
            0,
        )
        * 0.06,
        0.12,
    )

    # Multiple declarations should not artificially inflate confidence.
    if technology_only_evidence:
        source_count_bonus = min(
            source_count_bonus,
            0.04,
        )

    confidence = max(
        0.0,
        min(
            base_confidence
            + source_count_bonus,
            1.0,
        ),
    )

    if confidence >= 0.80:
        label = "Strong"

    elif confidence >= 0.60:
        label = "Moderate"

    else:
        label = "Weak"

    return (
        label,
        round(
            confidence,
            2,
        ),
    )


# =====================================================================
# CATEGORY OWNERSHIP
# =====================================================================

def _category_priority(
    category: str,
) -> Tuple[int, str]:
    """
    Return a deterministic category priority.

    Lower numeric value means higher priority.
    """
    try:
        priority = CATEGORY_PRIORITY.index(
            category
        )

    except ValueError:
        priority = len(
            CATEGORY_PRIORITY
        )

    return (
        priority,
        category,
    )


def _preferred_category(
    categories: List[str],
) -> str | None:
    """
    Select exactly one deterministic owner category for a skill.
    """
    valid_categories = [
        category
        for category in categories
        if category
    ]

    if not valid_categories:
        return None

    return min(
        set(valid_categories),
        key=_category_priority,
    )


def _deduplicate_categories(
    categories: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """
    Canonicalize and deterministically deduplicate category skills.

    A canonical skill is assigned to exactly one category globally.
    """
    skill_categories: Dict[str, List[str]] = {}

    for category, skills in categories.items():
        if not isinstance(
            skills,
            (list, tuple, set),
        ):
            continue

        for skill in skills:
            canonical = get_canonical_skill(
                skill
            )

            if not canonical:
                continue

            skill_categories.setdefault(
                canonical,
                [],
            ).append(category)

    result: Dict[str, List[str]] = {}

    for skill, skill_category_list in skill_categories.items():
        owner = _preferred_category(
            skill_category_list
        )

        if not owner:
            continue

        result.setdefault(
            owner,
            [],
        ).append(skill)

    for category in list(result):
        result[category] = sorted(
            set(result[category])
        )

        if not result[category]:
            del result[category]

    return result


# =====================================================================
# SKILL SCORE
# =====================================================================

def _calculate_skill_score(
    skills_found: List[str],
    skill_details: List[Dict[str, Any]],
    categories: Dict[str, List[str]],
) -> int:
    """
    Calculate the Skill Intelligence score.

    Components:

        Breadth             -> 35
        Evidence            -> 40
        Industry relevance  -> 15
        Category coverage   -> 10
    """
    if not skills_found:
        return 0

    confidence_weights = {
        "Strong": 1.00,
        "Moderate": 0.70,
        "Weak": 0.40,
    }

    source_weights = {
        "experience": 1.00,
        "internship": 1.00,
        "projects": 0.95,
        "summary": 0.70,
        "skills": 0.55,
        "resume": 0.40,
    }

    # ---------------------------------------------------------------
    # Breadth: 35 points
    # ---------------------------------------------------------------

    skill_count = len(
        set(skills_found)
    )

    breadth_points = (
        min(
            skill_count / 10.0,
            1.0,
        )
        * 35.0
    )

    # ---------------------------------------------------------------
    # Evidence: 40 points
    # ---------------------------------------------------------------

    evidence_scores: List[float] = []

    for detail in skill_details:
        confidence = str(
            detail.get(
                "confidence",
                "Weak",
            )
        )

        confidence_weight = (
            confidence_weights.get(
                confidence,
                0.40,
            )
        )

        try:
            evidence_quality = float(
                detail.get(
                    "evidence_quality",
                    0.0
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            evidence_quality = 0.0

        sources = detail.get(
            "sources",
            [],
        )

        if not isinstance(
            sources,
            list,
        ):
            sources = []

        source_strength = max(
            (
                source_weights.get(
                    str(source),
                    0.40,
                )
                for source in sources
            ),
            default=0.40,
        )

        source_bonus = min(
            max(
                len(set(sources)) - 1,
                0,
            )
            * 0.08,
            0.16,
        )

        contribution = (
            confidence_weight
            * (
                0.45
                + evidence_quality * 0.35
                + source_strength * 0.20
            )
        )

        contribution += source_bonus

        evidence_scores.append(
            min(
                contribution,
                1.0,
            )
        )

    average_evidence = (
        sum(evidence_scores)
        / len(evidence_scores)
        if evidence_scores
        else 0.0
    )

    evidence_points = (
        average_evidence
        * 40.0
    )

    # ---------------------------------------------------------------
    # Industry relevance: 15 points
    # ---------------------------------------------------------------

    industry_skill_set = {
        get_canonical_skill(skill)
        for skill in INDUSTRY_SKILLS
        if skill
    }

    demonstrated_skills = {
        get_canonical_skill(skill)
        for skill in skills_found
        if skill
    }

    demonstrated_industry_skills = (
        demonstrated_skills
        & industry_skill_set
    )

    industry_ratio = (
        len(demonstrated_industry_skills)
        / len(industry_skill_set)
        if industry_skill_set
        else 0.0
    )

    industry_points = (
        industry_ratio
        * 15.0
    )

    # ---------------------------------------------------------------
    # Category coverage: 10 points
    # ---------------------------------------------------------------

    category_count = len(
        categories
    )

    category_points = (
        min(
            category_count / 5.0,
            1.0,
        )
        * 10.0
    )

    # ---------------------------------------------------------------
    # Final score
    # ---------------------------------------------------------------

    raw_score = (
        breadth_points
        + evidence_points
        + industry_points
        + category_points
    )

    return int(
        round(
            max(
                0.0,
                min(
                    raw_score,
                    100.0,
                ),
            )
        )
    )


# =====================================================================
# MAIN ANALYZER
# =====================================================================

def analyze_skills(
    text: str,
    sections: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Analyze demonstrated technical skills.

    Public contract remains backward-compatible with v5.2/v5.5.
    """
    full_text = _normalize(text)

    normalized_sections: Dict[str, Any] = (
        sections
        if isinstance(
            sections,
            dict,
        )
        else {}
    )

    # =================================================================
    # 1. BUILD EVIDENCE SECTIONS
    # =================================================================

    evidence_sections = (
        _build_evidence_sections(
            normalized_sections
        )
    )

    # =================================================================
    # 2. SAFE FALLBACK
    # =================================================================

    if not evidence_sections:
        evidence_sections = (
            _build_safe_fallback(
                full_text,
                normalized_sections,
            )
        )

    skills_found: List[str] = []

    categories: Dict[
        str,
        List[str],
    ] = {}

    skill_details: List[
        Dict[str, Any]
    ] = []

    # =================================================================
    # 3. SCAN CENTRAL SKILL DATABASE
    # =================================================================

    for category, skills in CATEGORY_MAP.items():
        if not isinstance(
            skills,
            (list, tuple, set),
        ):
            continue

        category_detected: List[str] = []

        for skill in skills:
            if not skill:
                continue

            canonical = get_canonical_skill(
                skill
            )

            if not canonical:
                continue

            # ---------------------------------------------------------
            # Collect ALL useful evidence candidates.
            # ---------------------------------------------------------

            evidence_items: List[
                Dict[str, Any]
            ] = []

            for (
                section_name,
                section_text,
            ) in evidence_sections.items():

                # -----------------------------------------------------
                # Skills sections require a special match because a
                # category heading itself may contain a skill name.
                # -----------------------------------------------------

                if section_name == "skills":
                    candidates = (
                        _extract_evidence_candidates(
                            section_text,
                            canonical,
                            source="skills",
                        )
                    )

                else:
                    if not _contains_skill(
                        section_text,
                        canonical,
                    ):
                        continue

                    candidates = (
                        _extract_evidence_candidates(
                            section_text,
                            canonical,
                            source=section_name,
                        )
                    )

                if not candidates:
                    fallback = _extract_evidence(
                        section_text,
                        canonical,
                        source=section_name,
                    )

                    if fallback:
                        candidates = [
                            fallback
                        ]

                for snippet in candidates:
                    cleaned = _clean_evidence(
                        snippet
                    )

                    if not cleaned:
                        continue

                    evidence_items.append(
                        {
                            "source": section_name,
                            "evidence": cleaned,
                        }
                    )

            if not evidence_items:
                continue

            # ---------------------------------------------------------
            # Rank all evidence before selecting.
            # ---------------------------------------------------------

            ranked_evidence = _rank_evidence(
                evidence_items,
                canonical,
            )

            # ---------------------------------------------------------
            # Demonstrated-skill decision uses ALL available evidence.
            # ---------------------------------------------------------

            all_sources = sorted(
                {
                    str(
                        item.get(
                            "source",
                            "",
                        )
                    )
                    for item in ranked_evidence
                    if item.get("source")
                }
            )

            all_evidence = [
                str(
                    item.get(
                        "evidence",
                        "",
                    )
                )
                for item in ranked_evidence
                if item.get("evidence")
            ]

            if not _is_demonstrated_skill(
                all_sources,
                all_evidence,
                canonical,
            ):
                continue

            # ---------------------------------------------------------
            # Select evidence intelligently.
            # ---------------------------------------------------------

            selected_items = _select_evidence(
                ranked_evidence,
                canonical,
            )

            if not selected_items:
                continue

            selected_evidence: List[str] = []

            normalized_selected_items: List[
                Dict[str, Any]
            ] = []

            seen_selected_evidence = set()

            for item in selected_items:
                snippet = _clean_evidence(
                    str(
                        item.get(
                            "evidence",
                            "",
                        )
                    )
                )

                if not snippet:
                    continue

                # -----------------------------------------------------
                # Punctuation-insensitive de-duplication.
                # -----------------------------------------------------

                evidence_key = _evidence_dedupe_key(
                    snippet
                )

                if not evidence_key:
                    continue

                if evidence_key in seen_selected_evidence:
                    continue

                seen_selected_evidence.add(
                    evidence_key
                )

                # Preserve complete logical action sentences.
                snippet = _truncate_evidence(
                    snippet
                )

                selected_evidence.append(
                    snippet
                )

                normalized_selected_items.append(
                    {
                        "source": str(
                            item.get(
                                "source",
                                "",
                            )
                        ),
                        "evidence": snippet,
                    }
                )

                if (
                    len(selected_evidence)
                    >= MAX_EVIDENCE_PER_SKILL
                ):
                    break

            if not selected_evidence:
                continue

            # ---------------------------------------------------------
            # Sources correspond exactly to selected evidence.
            # ---------------------------------------------------------

            selected_sources = sorted(
                {
                    str(
                        item.get(
                            "source",
                            "",
                        )
                    )
                    for item in normalized_selected_items
                    if item.get("source")
                }
            )

            # ---------------------------------------------------------
            # Confidence.
            # ---------------------------------------------------------

            (
                confidence_label,
                confidence_score,
            ) = _confidence_from_sources(
                selected_sources,
                selected_evidence,
                canonical,
            )

            evidence_quality = round(
                max(
                    (
                        _evidence_quality(
                            item,
                            canonical,
                        )
                        for item in selected_evidence
                    ),
                    default=0.0,
                ),
                2,
            )

            skills_found.append(
                canonical
            )

            category_detected.append(
                canonical
            )

            skill_details.append(
                {
                    "name": canonical,
                    "category": category,
                    "confidence": confidence_label,
                    "confidence_score": confidence_score,
                    "sources": selected_sources,
                    "evidence": selected_evidence,
                    "evidence_quality": evidence_quality,
                }
            )

        if category_detected:
            categories[category] = sorted(
                set(category_detected)
            )

    # =================================================================
    # 4. GLOBAL DEDUPLICATION
    # =================================================================

    skills_found = sorted(
        {
            get_canonical_skill(skill)
            for skill in skills_found
            if skill
            and get_canonical_skill(skill)
        }
    )

    # =================================================================
    # 5. MERGE DUPLICATE SKILL DETAILS
    # =================================================================

    unique_details: Dict[
        str,
        Dict[str, Any],
    ] = {}

    for detail in skill_details:
        name = get_canonical_skill(
            detail.get(
                "name",
                "",
            )
        )

        if not name:
            continue

        existing = unique_details.get(
            name
        )

        if existing is None:
            initial_evidence: List[str] = []
            initial_seen = set()

            for evidence in detail.get(
                "evidence",
                [],
            ):
                evidence_text = _clean_evidence(
                    str(evidence)
                )

                key = _evidence_dedupe_key(
                    evidence_text
                )

                if not key or key in initial_seen:
                    continue

                initial_seen.add(key)

                evidence_text = _truncate_evidence(
                    evidence_text
                )

                initial_evidence.append(
                    evidence_text
                )

                if len(initial_evidence) >= MAX_EVIDENCE_PER_SKILL:
                    break

            initial_sources = sorted(
                set(
                    detail.get(
                        "sources",
                        [],
                    )
                )
            )

            unique_details[name] = {
                **detail,
                "name": name,
                "sources": initial_sources,
                "evidence": initial_evidence,
            }

            continue

        # -------------------------------------------------------------
        # Merge sources.
        # -------------------------------------------------------------

        existing_sources = list(
            existing.get(
                "sources",
                [],
            )
        )

        incoming_sources = list(
            detail.get(
                "sources",
                [],
            )
        )

        existing["sources"] = sorted(
            set(
                existing_sources
                + incoming_sources
            )
        )

        # -------------------------------------------------------------
        # Merge evidence.
        # -------------------------------------------------------------

        existing_evidence = list(
            existing.get(
                "evidence",
                [],
            )
        )

        incoming_evidence = list(
            detail.get(
                "evidence",
                [],
            )
        )

        merged_evidence: List[str] = []
        seen_merged_evidence = set()

        for evidence in (
            existing_evidence
            + incoming_evidence
        ):
            cleaned = _clean_evidence(
                str(evidence)
            )

            key = _evidence_dedupe_key(
                cleaned
            )

            if not key or key in seen_merged_evidence:
                continue

            seen_merged_evidence.add(key)

            cleaned = _truncate_evidence(
                cleaned
            )

            merged_evidence.append(cleaned)

            if len(merged_evidence) >= MAX_EVIDENCE_PER_SKILL:
                break

        # -------------------------------------------------------------
        # Rebuild source/evidence pairs where possible.
        #
        # The existing detail structure does not explicitly expose
        # source/evidence pairs, so we preserve the historical pairing
        # behavior without inventing a Cartesian relationship.
        # -------------------------------------------------------------

        merged_pairs: List[
            Dict[str, Any]
        ] = []

        for source, evidence in zip(
            existing_sources,
            existing_evidence,
        ):
            merged_pairs.append(
                {
                    "source": source,
                    "evidence": evidence,
                }
            )

        for source, evidence in zip(
            incoming_sources,
            incoming_evidence,
        ):
            merged_pairs.append(
                {
                    "source": source,
                    "evidence": evidence,
                }
            )

        if merged_pairs:
            # Remove punctuation-only duplicates before ranking.
            pair_unique: List[
                Dict[str, Any]
            ] = []

            seen_pair_keys = set()

            for pair in merged_pairs:
                source = str(
                    pair.get(
                        "source",
                        "",
                    )
                ).strip()

                evidence = _clean_evidence(
                    str(
                        pair.get(
                            "evidence",
                            "",
                        )
                    )
                )

                key = (
                    source,
                    _evidence_dedupe_key(
                        evidence
                    ),
                )

                if (
                    not source
                    or not evidence
                    or key in seen_pair_keys
                ):
                    continue

                seen_pair_keys.add(key)

                pair_unique.append(
                    {
                        "source": source,
                        "evidence": evidence,
                    }
                )

            ranked_merged = _rank_evidence(
                pair_unique,
                name,
            )

            reordered_evidence: List[str] = []
            reordered_sources: List[str] = []
            seen_reordered_evidence = set()

            for item in ranked_merged:
                snippet = _clean_evidence(
                    str(
                        item.get(
                            "evidence",
                            "",
                        )
                    )
                )

                source = str(
                    item.get(
                        "source",
                        "",
                    )
                ).strip()

                if not snippet or not source:
                    continue

                evidence_key = _evidence_dedupe_key(
                    snippet
                )

                if (
                    not evidence_key
                    or evidence_key in seen_reordered_evidence
                ):
                    continue

                seen_reordered_evidence.add(
                    evidence_key
                )

                snippet = _truncate_evidence(
                    snippet
                )

                reordered_evidence.append(
                    snippet
                )

                reordered_sources.append(
                    source
                )

                if (
                    len(reordered_evidence)
                    >= MAX_EVIDENCE_PER_SKILL
                ):
                    break

            if reordered_evidence:
                existing["evidence"] = (
                    reordered_evidence
                )

                existing["sources"] = sorted(
                    set(reordered_sources)
                )

            else:
                existing["evidence"] = (
                    merged_evidence
                )

        else:
            existing["evidence"] = (
                merged_evidence
            )

        # -------------------------------------------------------------
        # Recalculate confidence from actual merged evidence.
        # -------------------------------------------------------------

        (
            merged_label,
            merged_score,
        ) = _confidence_from_sources(
            existing.get(
                "sources",
                [],
            ),
            existing.get(
                "evidence",
                [],
            ),
            name,
        )

        existing["confidence"] = (
            merged_label
        )

        existing["confidence_score"] = (
            merged_score
        )

        existing["evidence_quality"] = round(
            max(
                (
                    _evidence_quality(
                        item,
                        name,
                    )
                    for item in existing.get(
                        "evidence",
                        [],
                    )
                ),
                default=0.0,
            ),
            2,
        )

    # =================================================================
    # 6. DEDUPLICATE CATEGORY OWNERSHIP
    # =================================================================

    categories = _deduplicate_categories(
        categories
    )

    # =================================================================
    # 7. ALIGN DETAIL CATEGORY WITH FINAL CATEGORY OWNERSHIP
    # =================================================================

    skill_to_category: Dict[
        str,
        str,
    ] = {}

    for category, category_skills in categories.items():
        for skill in category_skills:
            canonical = get_canonical_skill(
                skill
            )

            if canonical:
                skill_to_category[
                    canonical
                ] = category

    for detail in unique_details.values():
        name = get_canonical_skill(
            detail.get(
                "name",
                "",
            )
        )

        if not name:
            continue

        owner_category = skill_to_category.get(
            name
        )

        if owner_category:
            detail["category"] = (
                owner_category
            )

    # =================================================================
    # 8. FINAL DETAIL SORT
    # =================================================================

    skill_details = sorted(
        unique_details.values(),
        key=lambda item: (
            -float(
                item.get(
                    "confidence_score",
                    0.0,
                )
            ),
            -float(
                item.get(
                    "evidence_quality",
                    0.0,
                )
            ),
            str(
                item.get(
                    "name",
                    "",
                )
            ),
        ),
    )

    # =================================================================
    # 9. INDUSTRY SKILL GAPS
    # =================================================================

    missing_industry_skills = sorted(
        {
            get_canonical_skill(
                industry_skill
            )
            for industry_skill in INDUSTRY_SKILLS
            if industry_skill
            and get_canonical_skill(
                industry_skill
            ) not in skills_found
        }
    )

    # =================================================================
    # 10. SKILL SCORE
    # =================================================================

    skill_score = _calculate_skill_score(
        skills_found=skills_found,
        skill_details=skill_details,
        categories=categories,
    )

    # =================================================================
    # 11. CATEGORY STATISTICS
    # =================================================================

    category_count = len(
        categories
    )

    strongest_category = None

    if categories:
        strongest_category = max(
            categories.items(),
            key=lambda item: (
                len(item[1]),
                item[0],
            ),
        )[0]

    # =================================================================
    # 12. CONFIDENCE SUMMARY
    # =================================================================

    strong_count = sum(
        1
        for detail in skill_details
        if detail.get(
            "confidence"
        ) == "Strong"
    )

    moderate_count = sum(
        1
        for detail in skill_details
        if detail.get(
            "confidence"
        ) == "Moderate"
    )

    weak_count = sum(
        1
        for detail in skill_details
        if detail.get(
            "confidence"
        ) == "Weak"
    )

    # =================================================================
    # 13. STABLE RETURN CONTRACT
    # =================================================================

    return {
        "skill_score": skill_score,
        "total_skills": len(
            skills_found
        ),
        "skills_found": skills_found,
        "categories": categories,
        "missing_industry_skills": (
            missing_industry_skills
        ),
        "skill_details": skill_details,
        "category_count": category_count,
        "strongest_category": (
            strongest_category
        ),
        "confidence_summary": {
            "strong": strong_count,
            "moderate": moderate_count,
            "weak": weak_count,
        },
        "analysis_version": ANALYSIS_VERSION,
    }