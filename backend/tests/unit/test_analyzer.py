"""
Tests for the ResumeIQ analysis orchestration layer.

These tests verify that analyzer.py:

- validates input
- extracts sections
- invokes all analysis engines
- combines engine results correctly
- calculates the final score
- generates recommendations
- calculates confidence dynamically
- does not use hard-coded confidence
- handles malformed engine responses safely
- produces a stable response contract
"""

from unittest.mock import patch

import pytest

from app.services.analyzer import analyze_resume


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

SAMPLE_RESUME = """
John Doe
AI/ML Engineer

SUMMARY
AI/ML engineer with experience building machine learning applications.

EDUCATION
B.Tech in Computer Science
Malla Reddy University
2022 - 2026
CGPA: 8.55

SKILLS
Python, TensorFlow, NumPy, Pandas, Scikit-learn, Flask, SQL, Git, GitHub

PROJECTS
EV Energy Prediction System

Developed a machine learning system for electric vehicles.
Implemented federated learning using TensorFlow.
Integrated blockchain for privacy.
Achieved 95% accuracy.
Technologies: Python, TensorFlow, Blockchain, Federated Learning

EXPERIENCE
AI/ML Project Experience

Developed and trained machine learning models.

CERTIFICATIONS
AWS Cloud Practitioner Essentials

ACHIEVEMENTS
Finalist in a national hackathon.
"""


MINIMAL_RESUME = """
John Doe

SKILLS
Python

EDUCATION
B.Tech
"""


# ---------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------

def test_analyze_resume_rejects_none():
    """None is not valid resume input."""

    with pytest.raises(ValueError):
        analyze_resume(None)


def test_analyze_resume_rejects_empty_string():
    """Empty resumes must be rejected."""

    with pytest.raises(ValueError):
        analyze_resume("")


def test_analyze_resume_rejects_whitespace_only():
    """Whitespace-only resumes must be rejected."""

    with pytest.raises(ValueError):
        analyze_resume("   \n\t   ")


def test_analyze_resume_rejects_non_string_input():
    """Analyzer must require textual resume input."""

    with pytest.raises(TypeError):
        analyze_resume(12345)


def test_analyze_resume_accepts_valid_text():
    """A normal textual resume should be accepted."""

    result = analyze_resume(
        MINIMAL_RESUME
    )

    assert isinstance(result, dict)


# ---------------------------------------------------------------------
# Response contract
# ---------------------------------------------------------------------

def test_analysis_returns_expected_top_level_fields():
    """Final response must expose the public analysis contract."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    required_fields = {
        "resume_intelligence_score",
        "rating",
        "score_breakdown",
        "confidence",
        "sections_detected",
        "ats_analysis",
        "skills_analysis",
        "project_analysis",
        "experience_analysis",
        "certifications",
        "education",
        "achievement_analysis",
        "recommendations",
    }

    assert required_fields.issubset(
        result.keys()
    )


def test_final_score_is_numeric():
    """Final intelligence score must be numeric."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    assert isinstance(
        result["resume_intelligence_score"],
        (int, float),
    )


def test_final_score_is_within_valid_range():
    """Final score must always remain between 0 and 100."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    assert 0 <= result[
        "resume_intelligence_score"
    ] <= 100


def test_confidence_is_numeric():
    """Confidence must be numeric."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    assert isinstance(
        result["confidence"],
        int,
    )


def test_confidence_is_within_valid_range():
    """Confidence must always remain between 0 and 100."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    assert 0 <= result[
        "confidence"
    ] <= 100


# ---------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------

def test_sections_are_detected():
    """Known resume sections should be detected."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    detected = result[
        "sections_detected"
    ]

    assert isinstance(
        detected,
        dict,
    )


# ---------------------------------------------------------------------
# Engine integration
# ---------------------------------------------------------------------

def test_all_analysis_engines_are_called():
    """
    Analyzer must orchestrate every analysis engine exactly once.
    """

    fake_sections = {
        "summary": "summary",
        "education": "education",
        "skills": "skills",
        "projects": "projects",
        "experience": "experience",
        "certifications": "certifications",
        "achievements": "achievements",
    }

    fake_skills = {
        "skill_score": 80
    }

    fake_projects = {
        "score": 70
    }

    fake_ats = {
        "ats_score": 75
    }

    fake_experience = {
        "experience_score": 60
    }

    fake_certifications = {
        "score": 50
    }

    fake_education = {
        "score": 90
    }

    fake_score = {
        "resume_intelligence_score": 70,
        "rating": "Good",
        "score_breakdown": {},
    }

    with (
        patch(
            "app.services.analyzer.extract_sections",
            return_value=fake_sections,
        ) as extract_sections,

        patch(
            "app.services.analyzer.detect_sections",
            return_value={},
        ),

        patch(
            "app.services.analyzer.analyze_skills",
            return_value=fake_skills,
        ) as analyze_skills,

        patch(
            "app.services.analyzer.analyze_projects",
            return_value=fake_projects,
        ) as analyze_projects,

        patch(
            "app.services.analyzer.analyze_ats",
            return_value=fake_ats,
        ) as analyze_ats,

        patch(
            "app.services.analyzer.analyze_experience",
            return_value=fake_experience,
        ) as analyze_experience,

        patch(
            "app.services.analyzer.analyze_certifications",
            return_value=fake_certifications,
        ) as analyze_certifications,

        patch(
            "app.services.analyzer.analyze_education",
            return_value=fake_education,
        ) as analyze_education,

        patch(
            "app.services.analyzer.calculate_score",
            return_value=fake_score,
        ) as calculate_score,

        patch(
            "app.services.analyzer.generate_recommendations",
            return_value=[],
        ),
    ):

        result = analyze_resume(
            SAMPLE_RESUME
        )

    extract_sections.assert_called_once()
    analyze_skills.assert_called_once()
    analyze_projects.assert_called_once()
    analyze_ats.assert_called_once()
    analyze_experience.assert_called_once()
    analyze_certifications.assert_called_once()
    analyze_education.assert_called_once()
    calculate_score.assert_called_once()

    assert result[
        "resume_intelligence_score"
    ] == 70


# ---------------------------------------------------------------------
# Score aggregation
# ---------------------------------------------------------------------

def test_engine_scores_are_passed_to_scoring_engine():
    """
    Scores returned by individual engines must be passed to the
    scoring engine instead of being replaced or ignored.
    """

    fake_score = {
        "resume_intelligence_score": 75,
        "rating": "Good",
        "score_breakdown": {},
    }

    with (
        patch(
            "app.services.analyzer.analyze_skills",
            return_value={"skill_score": 81},
        ),

        patch(
            "app.services.analyzer.analyze_projects",
            return_value={"score": 62},
        ),

        patch(
            "app.services.analyzer.analyze_ats",
            return_value={"ats_score": 91},
        ),

        patch(
            "app.services.analyzer.analyze_experience",
            return_value={"experience_score": 70},
        ),

        patch(
            "app.services.analyzer.analyze_certifications",
            return_value={"score": 55},
        ),

        patch(
            "app.services.analyzer.analyze_education",
            return_value={"score": 95},
        ),

        patch(
            "app.services.analyzer.calculate_score",
            return_value=fake_score,
        ) as calculate_score,

        patch(
            "app.services.analyzer.generate_recommendations",
            return_value=[],
        ),
    ):

        analyze_resume(
            SAMPLE_RESUME
        )

    args = calculate_score.call_args.args

    assert args[0] == 81
    assert args[1] == 62
    assert args[2] == 70
    assert args[3] == 91
    assert args[4] == 55
    assert args[5] == 95


# ---------------------------------------------------------------------
# Achievement analysis
# ---------------------------------------------------------------------

def test_achievement_detection_uses_actual_achievement_signals():
    """Achievement keywords should contribute to achievement analysis."""

    result = analyze_resume(
        """
        John Doe

        ACHIEVEMENTS
        Winner of a national hackathon.
        Awarded first place in an AI competition.
        """
    )

    achievement = result[
        "achievement_analysis"
    ]

    assert achievement[
        "score"
    ] > 0

    assert achievement[
        "count"
    ] > 0


def test_percentage_alone_is_not_an_achievement():
    """
    Academic/project percentages must not automatically become
    achievement scores.
    """

    result = analyze_resume(
        """
        John Doe

        EDUCATION
        B.Tech - 89%

        PROJECTS
        Achieved 95% model accuracy.
        """
    )

    achievement = result[
        "achievement_analysis"
    ]

    assert achievement[
        "score"
    ] == 0


# ---------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------

def test_confidence_is_not_hard_coded_to_95():
    """
    Confidence must be derived from available analysis information,
    not permanently set to 95.
    """

    result = analyze_resume(
        MINIMAL_RESUME
    )

    assert result[
        "confidence"
    ] != 95


def test_richer_resume_can_produce_higher_confidence():
    """
    A structurally richer resume should have at least as much
    analysis confidence as a minimal resume.
    """

    minimal = analyze_resume(
        MINIMAL_RESUME
    )

    rich = analyze_resume(
        SAMPLE_RESUME
    )

    assert rich[
        "confidence"
    ] >= minimal[
        "confidence"
    ]


# ---------------------------------------------------------------------
# Malformed engine responses
# ---------------------------------------------------------------------

def test_none_engine_result_does_not_crash():
    """
    Analyzer should safely normalize an engine returning None.
    """

    with patch(
        "app.services.analyzer.analyze_skills",
        return_value=None,
    ):

        result = analyze_resume(
            SAMPLE_RESUME
        )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        "skills_analysis"
    ] == {}


def test_invalid_score_does_not_crash():
    """
    Malformed score values should not crash the controller.
    """

    with (
        patch(
            "app.services.analyzer.analyze_skills",
            return_value={
                "skill_score": "invalid"
            },
        ),

        patch(
            "app.services.analyzer.calculate_score",
            return_value={
                "resume_intelligence_score": 0,
                "rating": "Needs Improvement",
                "score_breakdown": {},
            },
        ),
    ):

        result = analyze_resume(
            SAMPLE_RESUME
        )

    assert isinstance(
        result,
        dict,
    )


# ---------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------

def test_recommendations_are_returned_as_list():
    """Recommendations must have a stable list-based contract."""

    result = analyze_resume(
        SAMPLE_RESUME
    )

    assert isinstance(
        result[
            "recommendations"
        ],
        list,
    )


# ---------------------------------------------------------------------
# Regression protection
# ---------------------------------------------------------------------

def test_analyzer_does_not_duplicate_project_results():
    """
    Analyzer must preserve the project engine's project count rather
    than inventing or duplicating projects.
    """

    result = analyze_resume(
        SAMPLE_RESUME
    )

    project_analysis = result[
        "project_analysis"
    ]

    projects = project_analysis.get(
        "projects",
        [],
    )

    assert isinstance(
        projects,
        list,
    )

    assert project_analysis.get(
        "project_count",
        len(projects),
    ) == len(projects)