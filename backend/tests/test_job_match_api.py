"""
ResumeIQ - Job Match API Integration Tests.

Verifies that the FastAPI /resume/match endpoint correctly:
- accepts a resume upload
- accepts a job description
- calls the production job matcher
- returns the expected response contract
- handles invalid requests safely
"""

from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# =====================================================================
# TEST DATA
# =====================================================================

RESUME_TEXT = """
Abhinav
AI/ML Engineer

Skills:
Python, Java, SQL, FastAPI, React, Docker, Git,
Machine Learning, TensorFlow, Pandas, NumPy.

Experience:
1 year of experience.

Projects:
Built a machine learning application using Python and FastAPI.
Developed REST APIs and deployed applications using Docker.
"""


JOB_DESCRIPTION = """
We are looking for a Software Engineer.

Requirements:
Python
FastAPI
SQL
Docker
React
Machine Learning
TensorFlow

Experience:
1 year of experience.
"""


# =====================================================================
# HELPERS
# =====================================================================

def _create_resume_file():
    """
    Create an in-memory resume file for API testing.
    """

    return {
        "file": (
            "resume.txt",
            BytesIO(
                RESUME_TEXT.encode("utf-8")
            ),
            "text/plain",
        )
    }


# =====================================================================
# SUCCESS CASE
# =====================================================================

def test_job_match_endpoint_returns_valid_response():
    """
    Verify successful resume-to-job matching.
    """

    response = client.post(
        "/resume/match",
        files=_create_resume_file(),
        data={
            "job_description": JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    # ---------------------------------------------------------------
    # Core response
    # ---------------------------------------------------------------

    assert "match_score" in data
    assert "match_level" in data
    assert "application_readiness" in data

    assert 0 <= data["match_score"] <= 100

    # ---------------------------------------------------------------
    # Skills
    # ---------------------------------------------------------------

    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "critical_missing_skills" in data

    assert isinstance(
        data["matched_skills"],
        list,
    )

    assert isinstance(
        data["missing_skills"],
        list,
    )

    # ---------------------------------------------------------------
    # Categories
    # ---------------------------------------------------------------

    assert "resume_categories" in data
    assert "job_categories" in data
    assert "category_coverage" in data

    # ---------------------------------------------------------------
    # Requirements
    # ---------------------------------------------------------------

    assert "requirements" in data
    assert "requirement_priorities" in data
    assert "requirement_weights" in data
    assert "requirement_priority_counts" in data
    assert "requirement_coverage" in data

    coverage = data["requirement_coverage"]

    assert "matched" in coverage
    assert "total" in coverage
    assert "percentage" in coverage
    assert "weighted_score" in coverage

    # ---------------------------------------------------------------
    # Experience
    # ---------------------------------------------------------------

    assert "experience_requirements" in data
    assert "resume_experience_years" in data
    assert "experience_gap" in data

    # ---------------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------------

    assert "suggestions" in data
    assert "suggestion" in data

    assert isinstance(
        data["suggestions"],
        list,
    )


# =====================================================================
# EMPTY JOB DESCRIPTION
# =====================================================================

def test_job_match_requires_job_description():
    """
    Verify that an empty job description is rejected.
    """

    response = client.post(
        "/resume/match",
        files=_create_resume_file(),
        data={
            "job_description": "",
        },
    )

    assert response.status_code == 400


# =====================================================================
# EMPTY RESUME
# =====================================================================

def test_job_match_rejects_empty_resume():
    """
    Verify that an empty resume file is rejected.
    """

    response = client.post(
        "/resume/match",
        files={
            "file": (
                "resume.txt",
                BytesIO(b""),
                "text/plain",
            )
        },
        data={
            "job_description": JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 400


# =====================================================================
# UNSUPPORTED FILE
# =====================================================================

def test_job_match_rejects_unsupported_file_type():
    """
    Verify unsupported resume formats are rejected.
    """

    response = client.post(
        "/resume/match",
        files={
            "file": (
                "resume.exe",
                BytesIO(b"fake resume"),
                "application/octet-stream",
            )
        },
        data={
            "job_description": JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 400