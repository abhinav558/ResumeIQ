"""
Education Intelligence Engine - Production Version

Responsibilities:
- Extract education records from resume text
- Normalize degree / education levels
- Extract institution, field of study, dates, CGPA and percentage
- Merge fragmented education lines
- Repair malformed school/education records
- Deduplicate education records
- Preserve backward-compatible output aliases
"""

import re
from typing import Any


# ============================================================
# Patterns
# ============================================================

YEAR_PATTERN = re.compile(
    r"\b(20\d{2})\b"
)

YEAR_RANGE_PATTERN = re.compile(
    r"\b(20\d{2})\s*[-–—]\s*(20\d{2})\b"
)

CGPA_PATTERN = re.compile(
    r"\bcgpa\s*[:=|]?\s*(\d+(?:\.\d+)?)"
    r"(?:\s*/\s*10)?",
    re.IGNORECASE,
)

CGPA_REVERSE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:/10\s*)?\bcgpa\b",
    re.IGNORECASE,
)

PERCENTAGE_PATTERN = re.compile(
    r"\bpercentage\s*[:=|]?\s*(\d+(?:\.\d+)?)\s*%?",
    re.IGNORECASE,
)

PERCENTAGE_SYMBOL_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*%"
)

YEAR_ONLY_PATTERN = re.compile(
    r"^\s*20\d{2}(?:\s*[-–—]\s*20\d{2})?\s*$"
)

LABELED_CGPA_ONLY_PATTERN = re.compile(
    r"^\s*cgpa\s*[:=|]?\s*(\d+(?:\.\d+)?)"
    r"(?:\s*/\s*10)?\s*$",
    re.IGNORECASE,
)

LABELED_PERCENTAGE_ONLY_PATTERN = re.compile(
    r"^\s*percentage\s*[:=|]?\s*(\d+(?:\.\d+)?)"
    r"\s*%?\s*$",
    re.IGNORECASE,
)

STANDALONE_PERCENTAGE_PATTERN = re.compile(
    r"^\s*\d+(?:\.\d+)?\s*%\s*$"
)

STANDALONE_NUMBER_PATTERN = re.compile(
    r"^\s*\d+(?:\.\d+)?\s*$"
)


# ============================================================
# Basic normalization
# ============================================================

def _clean_line(line: str) -> str:
    """Normalize a single resume line."""

    line = str(line)

    line = (
        line.replace("\x00", " ")
        .replace("\x7f", " ")
        .replace("\x0b", " ")
        .replace("\x0c", " ")
    )

    # Normalize common bullet glyphs.
    line = re.sub(
        r"[\u2022\u25cf\uF0B7●▪◦‣►➢]",
        " ",
        line,
    )

    # Remove leading Markdown/list characters.
    line = re.sub(
        r"^[\s\-–—*•]+",
        "",
        line,
    )

    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    return line.strip()


def _normalize_key(value: Any) -> str:
    """Create a stable normalized comparison key."""

    if value is None:
        return ""

    value = str(value).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def _values_compatible(
    first: Any,
    second: Any,
) -> bool:
    """
    Return True when two optional values are compatible.

    Empty values do not provide contradictory evidence.
    """

    first_key = _normalize_key(first)
    second_key = _normalize_key(second)

    if not first_key or not second_key:
        return True

    return first_key == second_key


def _numeric_values_compatible(
    first: Any,
    second: Any,
) -> bool:
    """Compare optional numeric education values safely."""

    if first is None or first == "":
        return True

    if second is None or second == "":
        return True

    try:
        return abs(float(first) - float(second)) < 0.001
    except (TypeError, ValueError):
        return _normalize_key(first) == _normalize_key(second)


# ============================================================
# Extraction helpers
# ============================================================

def _extract_years(text: str) -> list[str]:
    """Extract unique years in appearance order."""

    years = YEAR_PATTERN.findall(str(text))

    result: list[str] = []

    for year in years:
        if year not in result:
            result.append(year)

    return result


def _extract_date_range(
    text: str,
) -> tuple[str | None, str | None]:
    """
    Extract the first meaningful education date range.

    Examples:
        2022 - 2026 -> 2022, 2026
        2020–2022   -> 2020, 2022
        2020        -> 2020, 2020
    """

    text = str(text)

    range_match = YEAR_RANGE_PATTERN.search(text)

    if range_match:
        return (
            range_match.group(1),
            range_match.group(2),
        )

    years = _extract_years(text)

    if not years:
        return None, None

    if len(years) >= 2:
        return (
            years[0],
            years[1],
        )

    return (
        years[0],
        years[0],
    )


def _valid_cgpa(value: float | None) -> float | None:
    """Validate CGPA against the conventional 0-10 range."""

    if value is None:
        return None

    if 0 <= value <= 10:
        return value

    return None


def _valid_percentage(value: float | None) -> float | None:
    """Validate percentage against the conventional 0-100 range."""

    if value is None:
        return None

    if 0 <= value <= 100:
        return value

    return None


def _extract_cgpa(text: str) -> float | None:
    """
    Extract CGPA.

    Supported forms:
        CGPA: 8.55
        CGPA 8.55
        8.55 CGPA
        CGPA: 9.3/10
    """

    text = str(text)

    match = CGPA_PATTERN.search(text)

    if match:
        try:
            return _valid_cgpa(
                float(match.group(1))
            )
        except (TypeError, ValueError):
            pass

    match = CGPA_REVERSE_PATTERN.search(text)

    if match:
        try:
            return _valid_cgpa(
                float(match.group(1))
            )
        except (TypeError, ValueError):
            pass

    return None


def _extract_percentage(text: str) -> float | None:
    """
    Extract percentage.

    Supported forms:
        Percentage: 89
        Percentage: 89%
        89%
    """

    text = str(text)

    match = PERCENTAGE_PATTERN.search(text)

    if match:
        try:
            value = _valid_percentage(
                float(match.group(1))
            )
            if value is not None:
                return value
        except (TypeError, ValueError):
            pass

    match = PERCENTAGE_SYMBOL_PATTERN.search(text)

    if match:
        try:
            return _valid_percentage(
                float(match.group(1))
            )
        except (TypeError, ValueError):
            pass

    return None


def _extract_standalone_numeric_metadata(
    line: str,
    education_level: str,
) -> tuple[float | None, float | None]:
    """
    Handle numeric-only metadata conservatively.

    Examples:
        9.3  -> CGPA for school/academic records
        89   -> percentage for intermediate records

    We intentionally do NOT interpret arbitrary numeric lines
    as scores unless the surrounding record identifies the
    education level.
    """

    text = str(line).strip()

    if not STANDALONE_NUMBER_PATTERN.fullmatch(text):
        return None, None

    try:
        value = float(text)
    except (TypeError, ValueError):
        return None, None

    # CGPA is conventionally <= 10.
    if 0 <= value <= 10:
        if education_level in {
            "school",
            "bachelor",
            "master",
            "intermediate",
            "other",
        }:
            return value, None

    # A number > 10 is much more likely to be percentage.
    if 10 < value <= 100:
        if education_level in {
            "intermediate",
            "school",
            "bachelor",
            "master",
            "other",
        }:
            return None, value

    return None, None


# ============================================================
# Education level / degree
# ============================================================

def _detect_education_level(
    text: str,
) -> str:
    lower = str(text).lower()

    if any(
        token in lower
        for token in (
            "ph.d",
            "phd",
            "doctorate",
        )
    ):
        return "doctorate"

    if any(
        token in lower
        for token in (
            "master",
            "m.tech",
            "m.e.",
            "m.e ",
            "m.sc",
            "msc",
            "mca",
            "mba",
            "postgraduate",
        )
    ):
        return "master"

    if any(
        token in lower
        for token in (
            "bachelor",
            "b.tech",
            "b.e.",
            "b.e ",
            "b.sc",
            "bsc",
            "bca",
            "undergraduate",
        )
    ):
        return "bachelor"

    if any(
        token in lower
        for token in (
            "intermediate",
            "12th",
            "higher secondary",
            "junior college",
        )
    ):
        return "intermediate"

    if any(
        token in lower
        for token in (
            "secondary school",
            "high school",
            "10th",
            "ssc",
            "school",
        )
    ):
        return "school"

    return "other"


def _extract_degree(
    line: str,
) -> str | None:

    patterns = [
        (
            r"\bbachelor\s+of\s+technology\b",
            "Bachelor of Technology",
        ),
        (
            r"\bbachelor\s+of\s+engineering\b",
            "Bachelor of Engineering",
        ),
        (
            r"\bb\.?\s*tech\b",
            "Bachelor of Technology",
        ),
        (
            r"\bb\.?\s*e\.?\b",
            "Bachelor of Engineering",
        ),
        (
            r"\bbachelor(?:\s+degree)?\b",
            "Bachelor",
        ),
        (
            r"\bmaster\s+of\s+technology\b",
            "Master of Technology",
        ),
        (
            r"\bm\.?\s*tech\b",
            "Master of Technology",
        ),
        (
            r"\bmaster(?:\s+degree)?\b",
            "Master",
        ),
        (
            r"\bintermediate(?:\s+education)?\b",
            "Intermediate Education",
        ),
        (
            r"\bhigher\s+secondary(?:\s+education)?\b",
            "Higher Secondary Education",
        ),
        (
            r"\bsecondary\s+school(?:\s+education)?\b",
            "Secondary School Education",
        ),
    ]

    for pattern, value in patterns:
        if re.search(
            pattern,
            str(line),
            re.IGNORECASE,
        ):
            return value

    return None


# ============================================================
# Field of study
# ============================================================

def _extract_field_of_study(
    line: str,
) -> str | None:

    text = str(line)

    patterns = [
        (
            r"\b(?:in|majored?\s+in)\s+(.+?)"
            r"(?=\s+(?:cgpa|percentage|20\d{2})\b|$)"
        ),
        (
            r"\bfield\s+of\s+study\s*[:|-]\s*(.+?)"
            r"(?=\s+(?:cgpa|percentage|20\d{2})\b|$)"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            field = match.group(1).strip(
                " ,|-:"
            )

            if field:
                return field

    # Common parenthetical form:
    # B.Tech (Computer Science and Engineering)
    degree_match = _extract_degree(text)

    if degree_match:
        remainder = re.sub(
            re.escape(degree_match),
            "",
            text,
            count=1,
            flags=re.IGNORECASE,
        )

        parenthetical = re.search(
            r"\(([^()]+)\)",
            remainder,
        )

        if parenthetical:
            field = parenthetical.group(1).strip()

            if (
                field
                and not re.fullmatch(
                    r"(?:cgpa|percentage)",
                    field,
                    re.IGNORECASE,
                )
            ):
                return field

    return None


# ============================================================
# Institution handling
# ============================================================

def _clean_institution(
    value: str | None,
) -> str | None:

    if not value:
        return None

    value = str(value).strip()

    # Remove score metadata.
    value = re.sub(
        r"\s*[-|:]\s*"
        r"(?:cgpa|percentage)\s*[:|]?\s*"
        r"\d+(?:\.\d+)?%?"
        r"(?:\s*/\s*10)?",
        "",
        value,
        flags=re.IGNORECASE,
    )

    # Remove trailing year/range after separator.
    value = re.sub(
        r"\s*[-|:]\s*"
        r"20\d{2}"
        r"(?:\s*[-–—]\s*20\d{2})?"
        r"\s*$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    # Remove standalone trailing year/range.
    value = re.sub(
        r"\s+20\d{2}"
        r"(?:\s*[-–—]\s*20\d{2})?"
        r"\s*$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    value = value.strip(
        " |-:"
    )

    return value or None


def _is_generic_institution(
    institution: str | None,
) -> bool:

    normalized = _normalize_key(
        institution
    )

    return normalized in {
        "",
        "school",
        "college",
        "university",
        "institution",
        "institute",
        "education",
        "secondary school education",
        "intermediate education",
        "higher secondary education",
    }


def _is_malformed_institution(
    institution: str | None,
    degree: str | None,
) -> bool:

    if not institution:
        return False

    normalized_institution = _normalize_key(
        institution
    )

    normalized_degree = _normalize_key(
        degree
    )

    if not normalized_institution:
        return True

    malformed_patterns = (
        r"^secondary\s+school\s+education\s*\|\s*20\d{2}$",
        r"^secondary\s+school\s*\|\s*20\d{2}$",
        r"^intermediate\s+education\s*\|\s*20\d{2}$",
        r"^higher\s+secondary\s+education\s*\|\s*20\d{2}$",
        r"^secondary\s+school\s+education$",
        r"^intermediate\s+education$",
        r"^higher\s+secondary\s+education$",
    )

    for pattern in malformed_patterns:
        if re.match(
            pattern,
            str(institution).strip(),
            re.IGNORECASE,
        ):
            return True

    if (
        normalized_degree
        and normalized_degree in normalized_institution
        and re.search(
            r"\b20\d{2}\b",
            str(institution),
        )
    ):
        return True

    return False


def _looks_like_real_institution(
    line: str,
) -> bool:
    """
    Determine whether a line likely contains an actual
    institution name.
    """

    lower = str(line).lower()

    institution_tokens = (
        "university",
        "college",
        "school",
        "institute",
    )

    if not any(
        token in lower
        for token in institution_tokens
    ):
        return False

    cleaned = _clean_institution(line)

    if not cleaned:
        return False

    return not _is_generic_institution(
        cleaned
    )


# ============================================================
# Education-line classification
# ============================================================

def _is_education_line(
    line: str,
) -> bool:

    lower = str(line).lower()

    terms = (
        "university",
        "college",
        "school",
        "institute",
        "bachelor",
        "b.tech",
        "b tech",
        "b.e",
        "b e",
        "b.sc",
        "bsc",
        "bca",
        "master",
        "m.tech",
        "m tech",
        "mca",
        "mba",
        "intermediate",
        "secondary",
        "higher secondary",
        "education",
        "undergraduate",
        "postgraduate",
    )

    return any(
        term in lower
        for term in terms
    )


def _is_metadata_line(
    line: str,
    current_lines: list[str] | None = None,
) -> bool:
    """
    Identify metadata lines.

    Important:
    Numeric-only values are treated as metadata ONLY when
    there is already an education context. This prevents
    arbitrary numbers elsewhere in a resume from becoming
    education scores.
    """

    text = str(line).strip()

    if not text:
        return False

    if YEAR_ONLY_PATTERN.fullmatch(text):
        return True

    if LABELED_CGPA_ONLY_PATTERN.fullmatch(text):
        return True

    if LABELED_PERCENTAGE_ONLY_PATTERN.fullmatch(text):
        return True

    if STANDALONE_PERCENTAGE_PATTERN.fullmatch(text):
        return True

    if CGPA_PATTERN.search(text):
        return True

    if CGPA_REVERSE_PATTERN.search(text):
        return True

    if PERCENTAGE_PATTERN.search(text):
        return True

    if current_lines:
        combined = " ".join(current_lines)
        level = _detect_education_level(combined)

        if STANDALONE_NUMBER_PATTERN.fullmatch(text):
            cgpa, percentage = (
                _extract_standalone_numeric_metadata(
                    text,
                    level,
                )
            )

            return (
                cgpa is not None
                or percentage is not None
            )

    return False


def _contains_new_education_record(
    line: str,
) -> bool:
    """
    A new education record is usually indicated by an actual
    institution or an explicit degree/education level.
    """

    if _looks_like_real_institution(line):
        return True

    if _extract_degree(line):
        return True

    return False


# ============================================================
# Entry construction
# ============================================================

def _find_institution(
    current_lines: list[str],
    degree: str | None,
) -> str | None:
    """
    Extract the best institution candidate.
    """

    # First preference: explicit institution names.
    for candidate in current_lines:
        if _looks_like_real_institution(candidate):
            institution = _clean_institution(candidate)

            if institution:
                return institution

    # Second preference: text surrounding a degree.
    for candidate in current_lines:
        candidate_degree = _extract_degree(candidate)

        if not candidate_degree:
            continue

        possible = re.sub(
            re.escape(candidate_degree),
            "",
            candidate,
            count=1,
            flags=re.IGNORECASE,
        )

        possible = re.sub(
            r"\b(?:in|at)\b",
            "",
            possible,
            count=1,
            flags=re.IGNORECASE,
        )

        # Remove parenthesized field of study.
        possible = re.sub(
            r"\([^)]*\)",
            "",
            possible,
        )

        possible = _clean_institution(
            possible
        )

        if (
            possible
            and not _is_generic_institution(possible)
            and not _is_malformed_institution(
                possible,
                degree,
            )
        ):
            return possible

    return None


def _build_entry(
    current_lines: list[str],
) -> dict[str, Any] | None:

    if not current_lines:
        return None

    combined = " ".join(
        current_lines
    )

    level = _detect_education_level(
        combined
    )

    degree = _extract_degree(
        combined
    )

    field_of_study = _extract_field_of_study(
        combined
    )

    cgpa = _extract_cgpa(
        combined
    )

    percentage = _extract_percentage(
        combined
    )

    # Handle numeric-only metadata attached to the block.
    if cgpa is None or percentage is None:
        for line in current_lines:
            line_cgpa, line_percentage = (
                _extract_standalone_numeric_metadata(
                    line,
                    level,
                )
            )

            if (
                cgpa is None
                and line_cgpa is not None
            ):
                cgpa = line_cgpa

            if (
                percentage is None
                and line_percentage is not None
            ):
                percentage = line_percentage

    start_date, end_date = _extract_date_range(
        combined
    )

    institution = _find_institution(
        current_lines,
        degree,
    )

    # Do not generate garbage records.
    if (
        not institution
        and not degree
        and level == "other"
    ):
        return None

    if degree:
        canonical_degree = degree
    elif level == "intermediate":
        canonical_degree = (
            "Intermediate Education"
        )
    elif level == "school":
        canonical_degree = (
            "Secondary School Education"
        )
    elif level == "master":
        canonical_degree = "Master"
    elif level == "bachelor":
        canonical_degree = "Bachelor"
    else:
        canonical_degree = "Education"

    if (
        institution
        and _is_malformed_institution(
            institution,
            canonical_degree,
        )
    ):
        institution = None

    return {
        "degree": canonical_degree,
        "field_of_study": field_of_study,
        "field": field_of_study,
        "institution": institution,
        "education_level": level,
        "level": level,
        "start_date": start_date,
        "end_date": end_date,
        "year": (
            f"{start_date}–{end_date}"
            if start_date and end_date
            else (
                start_date
                or end_date
            )
        ),
        "cgpa": cgpa,
        "percentage": percentage,
    }


# ============================================================
# Entry extraction
# ============================================================

def _build_entries(
    text: str,
) -> list[dict[str, Any]]:
    """
    Build education records from lines.

    The parser is intentionally record-oriented:

        Institution
        Degree
        Score
        Dates

    becomes one record.

    When another real institution appears, the current record
    is flushed before starting the next one.
    """

    lines = [
        _clean_line(line)
        for line in str(text).splitlines()
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    entries: list[dict[str, Any]] = []
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_lines

        if not current_lines:
            return

        entry = _build_entry(
            current_lines
        )

        if entry:
            entries.append(entry)

        current_lines = []

    for line in lines:

        # ----------------------------------------------------
        # Metadata belongs to the current education record.
        # ----------------------------------------------------
        if _is_metadata_line(
            line,
            current_lines,
        ):
            if current_lines:
                current_lines.append(line)
            continue

        # ----------------------------------------------------
        # Real institution starts a new record.
        #
        # This is the most important boundary:
        #
        # ABV Junior College
        # ...
        # Vikas Grammar High School
        #
        # must produce TWO different records.
        # ----------------------------------------------------
        if _looks_like_real_institution(line):

            if current_lines:
                flush_current()

            current_lines.append(line)
            continue

        # ----------------------------------------------------
        # Explicit degree / education-level line.
        # ----------------------------------------------------
        if _contains_new_education_record(line):

            if current_lines:
                current_entry = _build_entry(
                    current_lines
                )

                current_has_institution = (
                    current_entry is not None
                    and _has_real_institution(
                        current_entry
                    )
                )

                # A degree after an institution belongs to that
                # record, e.g.:
                #
                # Malla Reddy University
                # Bachelor of Technology ...
                #
                # But if the current record already has a degree
                # and another degree arrives, start a new record.
                current_has_degree = (
                    current_entry is not None
                    and bool(
                        current_entry.get("degree")
                    )
                )

                if (
                    current_has_institution
                    and current_has_degree
                ):
                    flush_current()

            current_lines.append(line)
            continue

        # ----------------------------------------------------
        # Continuation / field line.
        # ----------------------------------------------------
        if current_lines:
            if (
                re.search(
                    r"\bin\b",
                    line,
                    re.IGNORECASE,
                )
                or _extract_field_of_study(line)
                or re.search(
                    r"\b(?:technology|engineering|science)\b",
                    line,
                    re.IGNORECASE,
                )
            ):
                current_lines.append(line)
            else:
                # A non-education line means the education
                # record has ended.
                flush_current()

    flush_current()

    return entries


# ============================================================
# Merge / repair
# ============================================================

def _merge_entries(
    primary: dict[str, Any],
    secondary: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge two records without overwriting useful primary data.
    """

    merged = dict(primary)

    # --------------------------------------------------------
    # Institution
    # --------------------------------------------------------

    primary_institution = merged.get(
        "institution"
    )

    secondary_institution = secondary.get(
        "institution"
    )

    primary_institution_good = (
        primary_institution
        and not _is_generic_institution(
            primary_institution
        )
        and not _is_malformed_institution(
            primary_institution,
            merged.get("degree"),
        )
    )

    secondary_institution_good = (
        secondary_institution
        and not _is_generic_institution(
            secondary_institution
        )
        and not _is_malformed_institution(
            secondary_institution,
            secondary.get("degree"),
        )
    )

    if (
        not primary_institution_good
        and secondary_institution_good
    ):
        merged["institution"] = (
            secondary_institution
        )

    # --------------------------------------------------------
    # Degree
    # --------------------------------------------------------

    if (
        (
            not merged.get("degree")
            or _normalize_key(
                merged.get("degree")
            ) == "education"
        )
        and secondary.get("degree")
    ):
        merged["degree"] = secondary["degree"]

    # --------------------------------------------------------
    # Education level
    # --------------------------------------------------------

    if (
        (
            not merged.get("education_level")
            or _normalize_key(
                merged.get("education_level")
            ) == "other"
        )
        and secondary.get("education_level")
    ):
        merged["education_level"] = (
            secondary["education_level"]
        )

    if (
        not merged.get("level")
        and merged.get("education_level")
    ):
        merged["level"] = merged[
            "education_level"
        ]

    if (
        not merged.get("education_level")
        and merged.get("level")
    ):
        merged["education_level"] = merged[
            "level"
        ]

    # --------------------------------------------------------
    # Optional fields
    # --------------------------------------------------------

    for key in (
        "field_of_study",
        "field",
        "start_date",
        "end_date",
        "year",
        "cgpa",
        "percentage",
    ):
        if (
            merged.get(key) in (None, "")
            and secondary.get(key) is not None
        ):
            merged[key] = secondary[key]

    # Keep field aliases synchronized.
    if (
        not merged.get("field")
        and merged.get("field_of_study")
    ):
        merged["field"] = merged[
            "field_of_study"
        ]

    if (
        not merged.get("field_of_study")
        and merged.get("field")
    ):
        merged["field_of_study"] = merged[
            "field"
        ]

    # --------------------------------------------------------
    # Repair dates.
    # --------------------------------------------------------

    if (
        (
            not merged.get("start_date")
            or not merged.get("end_date")
        )
        and merged.get("year")
    ):
        start, end = _extract_date_range(
            str(merged["year"])
        )

        if (
            not merged.get("start_date")
            and start
        ):
            merged["start_date"] = start

        if (
            not merged.get("end_date")
            and end
        ):
            merged["end_date"] = end

    if (
        not merged.get("end_date")
        and merged.get("start_date")
    ):
        merged["end_date"] = merged[
            "start_date"
        ]

    if (
        merged.get("start_date")
        and merged.get("end_date")
    ):
        merged["year"] = (
            f"{merged['start_date']}–"
            f"{merged['end_date']}"
        )

    return merged


def _has_real_institution(
    entry: dict[str, Any],
) -> bool:

    institution = entry.get(
        "institution"
    )

    return bool(
        institution
        and not _is_generic_institution(
            institution
        )
        and not _is_malformed_institution(
            institution,
            entry.get("degree"),
        )
    )


def _same_education_level(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:

    first_level = _normalize_key(
        first.get("education_level")
        or first.get("level")
    )

    second_level = _normalize_key(
        second.get("education_level")
        or second.get("level")
    )

    if (
        not first_level
        or not second_level
    ):
        return True

    return first_level == second_level


def _same_degree(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:

    first_degree = _normalize_key(
        first.get("degree")
    )

    second_degree = _normalize_key(
        second.get("degree")
    )

    if (
        not first_degree
        or not second_degree
    ):
        return True

    if first_degree == second_degree:
        return True

    degree_groups = (
        {
            "bachelor",
            "bachelor of technology",
            "bachelor of engineering",
        },
        {
            "master",
            "master of technology",
        },
        {
            "intermediate education",
            "higher secondary education",
        },
        {
            "secondary school education",
        },
    )

    for group in degree_groups:
        if (
            first_degree in group
            and second_degree in group
        ):
            return True

    return False


def _dates_compatible(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    """
    Dates are compatible when:

    - either side has no dates
    - exact start/end values match
    - one side is a single-year record and the other record
      contains that same year
    """

    first_start = first.get(
        "start_date"
    )
    first_end = first.get(
        "end_date"
    )

    second_start = second.get(
        "start_date"
    )
    second_end = second.get(
        "end_date"
    )

    if not first_start or not second_start:
        return True

    if not first_end or not second_end:
        return True

    # Exact range match.
    if (
        str(first_start) == str(second_start)
        and str(first_end) == str(second_end)
    ):
        return True

    # Single-year record may be a fragment of a full record.
    first_single = (
        str(first_start) == str(first_end)
    )

    second_single = (
        str(second_start) == str(second_end)
    )

    if first_single:
        return (
            str(first_start) == str(second_start)
            or str(first_start) == str(second_end)
        )

    if second_single:
        return (
            str(second_start) == str(first_start)
            or str(second_start) == str(first_end)
        )

    return False


def _scores_compatible(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:

    return (
        _numeric_values_compatible(
            first.get("cgpa"),
            second.get("cgpa"),
        )
        and _numeric_values_compatible(
            first.get("percentage"),
            second.get("percentage"),
        )
    )


def _education_records_compatible(
    first: dict[str, Any],
    second: dict[str, Any],
) -> bool:
    """
    Conservative compatibility test.

    Two education records should merge only when there is strong
    evidence that they represent the same qualification.

    In particular:

        Intermediate + 89%
        Secondary School + 9.3 CGPA

    MUST NOT merge.
    """

    first_has_institution = _has_real_institution(
        first
    )

    second_has_institution = _has_real_institution(
        second
    )

    # --------------------------------------------------------
    # Different real institutions can NEVER merge.
    # --------------------------------------------------------

    if (
        first_has_institution
        and second_has_institution
    ):
        first_institution = _normalize_key(
            first.get("institution")
        )

        second_institution = _normalize_key(
            second.get("institution")
        )

        if first_institution != second_institution:
            return False

    # --------------------------------------------------------
    # Education levels must not conflict.
    # --------------------------------------------------------

    if not _same_education_level(
        first,
        second,
    ):
        return False

    # --------------------------------------------------------
    # Degrees must not conflict.
    # --------------------------------------------------------

    if not _same_degree(
        first,
        second,
    ):
        return False

    # --------------------------------------------------------
    # Dates must not conflict.
    # --------------------------------------------------------

    if not _dates_compatible(
        first,
        second,
    ):
        return False

    # --------------------------------------------------------
    # Scores must not conflict.
    # --------------------------------------------------------

    if not _scores_compatible(
        first,
        second,
    ):
        return False

    # --------------------------------------------------------
    # Strongest case: same real institution.
    # --------------------------------------------------------

    if (
        first_has_institution
        and second_has_institution
    ):
        return True

    # --------------------------------------------------------
    # One side is an institution-bearing record and the other
    # is a compatible fragment.
    # --------------------------------------------------------

    if (
        first_has_institution
        or second_has_institution
    ):
        return True

    # --------------------------------------------------------
    # Neither side has an institution.
    #
    # Require explicit matching degree/level plus meaningful
    # shared metadata.
    # --------------------------------------------------------

    first_degree = _normalize_key(
        first.get("degree")
    )

    second_degree = _normalize_key(
        second.get("degree")
    )

    first_level = _normalize_key(
        first.get("education_level")
        or first.get("level")
    )

    second_level = _normalize_key(
        second.get("education_level")
        or second.get("level")
    )

    same_degree = (
        bool(first_degree)
        and bool(second_degree)
        and _same_degree(first, second)
    )

    same_level = (
        bool(first_level)
        and bool(second_level)
        and first_level == second_level
    )

    shared_metadata = (
        (
            first.get("start_date")
            and second.get("start_date")
        )
        or (
            first.get("end_date")
            and second.get("end_date")
        )
        or (
            first.get("cgpa") is not None
            and second.get("cgpa") is not None
        )
        or (
            first.get("percentage") is not None
            and second.get("percentage") is not None
        )
    )

    return bool(
        (same_degree or same_level)
        and shared_metadata
    )


def _repair_malformed_school_entries(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Repair malformed school/intermediate fragments.

    Never merge records across education levels.
    """

    repaired: list[dict[str, Any]] = []

    for entry in entries:

        if _has_real_institution(entry):
            repaired.append(entry)
            continue

        candidate_index = None

        # Prefer nearest compatible preceding record.
        for index in range(
            len(repaired) - 1,
            -1,
            -1,
        ):
            candidate = repaired[index]

            if not _has_real_institution(candidate):
                continue

            if _education_records_compatible(
                candidate,
                entry,
            ):
                candidate_index = index
                break

        if candidate_index is not None:
            repaired[candidate_index] = _merge_entries(
                repaired[candidate_index],
                entry,
            )
            continue

        # A non-institution record can remain legitimate if it
        # explicitly identifies a qualification.
        degree = entry.get("degree")

        if (
            degree
            and not _is_malformed_institution(
                entry.get("institution"),
                degree,
            )
        ):
            repaired.append(entry)

    return repaired


# ============================================================
# Deduplication
# ============================================================

def _deduplicate_entries(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Deduplicate records while preserving the richest data.

    Merging is deliberately conservative.
    """

    unique: list[dict[str, Any]] = []

    for entry in entries:

        merged_index = None

        for index, existing in enumerate(unique):

            if not _education_records_compatible(
                existing,
                entry,
            ):
                continue

            existing_has_institution = (
                _has_real_institution(existing)
            )

            entry_has_institution = (
                _has_real_institution(entry)
            )

            existing_institution = _normalize_key(
                existing.get("institution")
            )

            entry_institution = _normalize_key(
                entry.get("institution")
            )

            # Both real institutions must match.
            if (
                existing_has_institution
                and entry_has_institution
                and existing_institution
                != entry_institution
            ):
                continue

            # Same real institution is strong evidence.
            if (
                existing_has_institution
                and entry_has_institution
                and existing_institution
                == entry_institution
            ):
                merged_index = index
                break

            # One side is a fragment.
            if (
                existing_has_institution
                != entry_has_institution
            ):
                merged_index = index
                break

            # Neither has an institution.
            existing_degree = _normalize_key(
                existing.get("degree")
            )

            entry_degree = _normalize_key(
                entry.get("degree")
            )

            existing_level = _normalize_key(
                existing.get("education_level")
                or existing.get("level")
            )

            entry_level = _normalize_key(
                entry.get("education_level")
                or entry.get("level")
            )

            same_degree = (
                bool(existing_degree)
                and bool(entry_degree)
                and _same_degree(
                    existing,
                    entry,
                )
            )

            same_level = (
                bool(existing_level)
                and bool(entry_level)
                and existing_level == entry_level
            )

            shared_metadata = (
                (
                    existing.get("start_date")
                    and entry.get("start_date")
                )
                or (
                    existing.get("end_date")
                    and entry.get("end_date")
                )
                or (
                    existing.get("cgpa") is not None
                    and entry.get("cgpa") is not None
                )
                or (
                    existing.get("percentage") is not None
                    and entry.get("percentage") is not None
                )
            )

            if (
                (same_degree or same_level)
                and shared_metadata
            ):
                merged_index = index
                break

        if merged_index is not None:
            unique[merged_index] = _merge_entries(
                unique[merged_index],
                entry,
            )
        else:
            unique.append(entry)

    return unique


# ============================================================
# Alias lists
# ============================================================

def _format_numeric_value(
    value: Any,
) -> str:

    try:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return str(number).rstrip("0").rstrip(".")

    except (
        TypeError,
        ValueError,
    ):
        return str(value)


def _build_alias_lists(
    entries: list[dict[str, Any]],
) -> tuple[
    list[str],
    list[str],
    list[str],
    list[str],
    list[list[str]],
]:

    degrees: list[str] = []
    institutions: list[str] = []
    cgpa: list[str] = []
    percentage: list[str] = []
    timeline: list[list[str]] = []

    for entry in entries:

        degree = entry.get("degree")

        if (
            degree
            and degree not in degrees
        ):
            degrees.append(degree)

        institution = entry.get(
            "institution"
        )

        if (
            institution
            and not _is_generic_institution(
                institution
            )
            and institution not in institutions
        ):
            institutions.append(institution)

        value = entry.get("cgpa")

        if value is not None:
            formatted = _format_numeric_value(
                value
            )

            if formatted not in cgpa:
                cgpa.append(formatted)

        value = entry.get("percentage")

        if value is not None:
            formatted = _format_numeric_value(
                value
            )

            if formatted not in percentage:
                percentage.append(formatted)

        start_date = entry.get(
            "start_date"
        )

        end_date = entry.get(
            "end_date"
        )

        if (
            start_date
            and end_date
        ):
            pair = [
                str(start_date),
                str(end_date),
            ]

            if pair not in timeline:
                timeline.append(pair)

    return (
        degrees,
        institutions,
        cgpa,
        percentage,
        timeline,
    )


# ============================================================
# Final entry normalization
# ============================================================

def _finalize_entry(
    entry: dict[str, Any],
) -> dict[str, Any]:
    """
    Ensure every education record has internally consistent
    aliases and dates.
    """

    normalized = dict(entry)

    # Field aliases.
    if (
        not normalized.get("field")
        and normalized.get("field_of_study")
    ):
        normalized["field"] = normalized[
            "field_of_study"
        ]

    if (
        not normalized.get("field_of_study")
        and normalized.get("field")
    ):
        normalized["field_of_study"] = normalized[
            "field"
        ]

    # Level aliases.
    if (
        not normalized.get("education_level")
        and normalized.get("level")
    ):
        normalized["education_level"] = normalized[
            "level"
        ]

    if (
        not normalized.get("level")
        and normalized.get("education_level")
    ):
        normalized["level"] = normalized[
            "education_level"
        ]

    # Validate scores.
    if normalized.get("cgpa") is not None:
        try:
            normalized["cgpa"] = _valid_cgpa(
                float(normalized["cgpa"])
            )
        except (TypeError, ValueError):
            normalized["cgpa"] = None

    if normalized.get("percentage") is not None:
        try:
            normalized["percentage"] = _valid_percentage(
                float(normalized["percentage"])
            )
        except (TypeError, ValueError):
            normalized["percentage"] = None

    # Date repair.
    if (
        (
            not normalized.get("start_date")
            or not normalized.get("end_date")
        )
        and normalized.get("year")
    ):
        start, end = _extract_date_range(
            str(normalized["year"])
        )

        if (
            not normalized.get("start_date")
            and start
        ):
            normalized["start_date"] = start

        if (
            not normalized.get("end_date")
            and end
        ):
            normalized["end_date"] = end

    if (
        normalized.get("start_date")
        and not normalized.get("end_date")
    ):
        normalized["end_date"] = normalized[
            "start_date"
        ]

    if (
        normalized.get("start_date")
        and normalized.get("end_date")
    ):
        normalized["year"] = (
            f"{normalized['start_date']}–"
            f"{normalized['end_date']}"
        )

    return normalized


# ============================================================
# Public analyzer
# ============================================================

def analyze_education(
    text: str,
) -> dict[str, Any]:
    """
    Analyze the education section of a resume.

    Returns the established ResumeIQ education schema.
    """

    if not text or not str(text).strip():
        return {
            "score": 0,
            "education_found": False,
            "entries": [],
            "details": [],
            "education": [],
            "degree": [],
            "institutions": [],
            "cgpa": [],
            "percentage": [],
            "timeline": [],
            "education_score": 0,
            "count": 0,
        }

    text = str(text)

    # --------------------------------------------------------
    # Extraction pipeline
    # --------------------------------------------------------

    entries = _build_entries(text)

    entries = _repair_malformed_school_entries(
        entries
    )

    entries = _deduplicate_entries(
        entries
    )

    entries = [
        _finalize_entry(entry)
        for entry in entries
    ]

    (
        degree,
        institutions,
        cgpa,
        percentage,
        timeline,
    ) = _build_alias_lists(entries)

    lower = text.lower()

    # --------------------------------------------------------
    # Fallback CGPA extraction
    # --------------------------------------------------------

    if not cgpa:
        raw_cgpa: list[str] = []

        for pattern in (
            CGPA_PATTERN,
            CGPA_REVERSE_PATTERN,
        ):
            for match in pattern.findall(lower):
                value = (
                    match
                    if isinstance(match, str)
                    else match[0]
                )

                try:
                    numeric = _valid_cgpa(
                        float(value)
                    )
                except (TypeError, ValueError):
                    continue

                if numeric is None:
                    continue

                formatted = _format_numeric_value(
                    numeric
                )

                if formatted not in raw_cgpa:
                    raw_cgpa.append(formatted)

        cgpa = raw_cgpa

    # --------------------------------------------------------
    # Fallback percentage extraction
    # --------------------------------------------------------

    if not percentage:
        raw_percentage: list[str] = []

        for pattern in (
            PERCENTAGE_PATTERN,
            PERCENTAGE_SYMBOL_PATTERN,
        ):
            for match in pattern.findall(lower):
                value = (
                    match
                    if isinstance(match, str)
                    else match[0]
                )

                try:
                    numeric = _valid_percentage(
                        float(value)
                    )
                except (TypeError, ValueError):
                    continue

                if numeric is None:
                    continue

                formatted = _format_numeric_value(
                    numeric
                )

                if formatted not in raw_percentage:
                    raw_percentage.append(formatted)

        percentage = raw_percentage

    # --------------------------------------------------------
    # Fallback timeline extraction
    # --------------------------------------------------------

    if not timeline:
        years = _extract_years(text)

        if len(years) >= 2:
            for index in range(
                0,
                len(years) - 1,
                2,
            ):
                pair = [
                    years[index],
                    years[index + 1],
                ]

                if pair not in timeline:
                    timeline.append(pair)

        elif len(years) == 1:
            pair = [
                years[0],
                years[0],
            ]

            if pair not in timeline:
                timeline.append(pair)

    # ========================================================
    # Scoring
    # ========================================================

    score = 0

    has_bachelor = any(
        entry.get("education_level")
        == "bachelor"
        for entry in entries
    ) or (
        "bachelor" in lower
        or "b.tech" in lower
        or "b.e" in lower
    )

    if has_bachelor:
        score += 40

    if (
        "computer science" in lower
        or "artificial intelligence" in lower
    ):
        score += 20

    strong_cgpa = False

    for entry in entries:
        value = entry.get("cgpa")

        if value is None:
            continue

        try:
            if float(value) >= 8:
                strong_cgpa = True
                break
        except (
            TypeError,
            ValueError,
        ):
            continue

    if not strong_cgpa:
        for value in cgpa:
            try:
                if float(value) >= 8:
                    strong_cgpa = True
                    break
            except (
                TypeError,
                ValueError,
            ):
                continue

    if strong_cgpa:
        score += 20

    if percentage:
        score += 10

    if timeline:
        score += 10

    final_score = min(
        score,
        100,
    )

    return {
        "score": final_score,
        "education_score": final_score,
        "education_found": (
            bool(entries)
            or bool(lower.strip())
        ),
        "entries": entries,
        "details": entries,
        "education": entries,
        "count": len(entries),
        "degree": degree,
        "institutions": institutions,
        "cgpa": cgpa,
        "percentage": percentage,
        "timeline": timeline,
    }


__all__ = [
    "analyze_education",
]