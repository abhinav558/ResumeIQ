from app.services.job_matcher import (
    extract_keywords,
    compare_resume_job,
)


def test_extract_keywords_finds_known_skills():
    text = """
    Python developer with experience in machine learning,
    TensorFlow, SQL, Docker and AWS.
    """

    result = extract_keywords(text)

    assert "python" in result
    assert "machine learning" in result
    assert "tensorflow" in result
    assert "sql" in result
    assert "docker" in result
    assert "aws" in result


def test_extract_keywords_is_case_insensitive():
    text = "PYTHON, TensorFlow, Docker"

    result = extract_keywords(text)

    assert "python" in result
    assert "tensorflow" in result
    assert "docker" in result


def test_compare_resume_job_finds_matches():
    resume = """
    Python developer with experience in SQL and TensorFlow.
    """

    job = """
    Looking for Python, SQL, TensorFlow and Docker experience.
    """

    result = compare_resume_job(
        resume,
        job
    )

    assert result["match_score"] == 75
    assert "python" in result["matched_skills"]
    assert "sql" in result["matched_skills"]
    assert "tensorflow" in result["matched_skills"]
    assert "docker" in result["missing_skills"]


def test_compare_resume_job_with_no_job_keywords():
    resume = "Python developer"

    job = "We are looking for a motivated candidate."

    result = compare_resume_job(
        resume,
        job
    )

    assert result["match_score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []


def test_compare_resume_job_empty_resume():
    resume = ""

    job = """
    Python SQL Docker
    """

    result = compare_resume_job(
        resume,
        job
    )

    assert result["match_score"] == 0
    assert result["matched_skills"] == []
def test_categorize_keywords():
    from app.services.job_matcher import categorize_keywords

    result = categorize_keywords(
        [
            "python",
            "machine learning",
            "tensorflow",
            "sql",
            "docker",
        ]
    )

    assert "Programming" in result
    assert "AI/ML" in result
    assert "Database" in result
    assert "DevOps" in result

    assert "python" in result["Programming"]
    assert "machine learning" in result["AI/ML"]
    assert "tensorflow" in result["AI/ML"]
    assert "sql" in result["Database"]
    assert "docker" in result["DevOps"]


def test_compare_resume_job_returns_categories():
    resume = """
    Python developer with machine learning,
    TensorFlow and SQL experience.
    """

    job = """
    Looking for Python, machine learning,
    TensorFlow, SQL and Docker.
    """

    result = compare_resume_job(
        resume,
        job
    )

    assert "resume_categories" in result
    assert "job_categories" in result

    assert "Programming" in result["resume_categories"]
    assert "AI/ML" in result["resume_categories"]
    assert "Database" in result["resume_categories"]


def test_compare_resume_job_detects_missing_category_skill():
    resume = """
    Python developer with machine learning
    and TensorFlow experience.
    """

    job = """
    Looking for Python, machine learning,
    TensorFlow, Docker and Kubernetes.
    """

    result = compare_resume_job(
        resume,
        job
    )

    assert "docker" in result["missing_skills"]
    assert "kubernetes" in result["missing_skills"]


def test_compare_resume_job_preserves_exact_skill_matching():
    resume = "Experienced Python developer with MySQL."

    job = "Looking for Python and SQL."

    result = compare_resume_job(
        resume,
        job
    )

    assert "python" in result["matched_skills"]

    # SQL should not match merely because MySQL is present.
    assert "sql" in result["missing_skills"]


def test_compare_resume_job_returns_useful_suggestion():
    resume = "Python developer"

    job = "Python developer with Docker and AWS experience."

    result = compare_resume_job(
        resume,
        job
    )

    assert isinstance(
        result["suggestion"],
        str
    )

    assert len(result["suggestion"]) > 0
def test_compare_resume_job_returns_category_coverage():
    resume = """
    Python developer with machine learning, TensorFlow,
    SQL, FastAPI and Docker experience.
    """

    job = """
    Looking for Python, machine learning, TensorFlow,
    SQL, FastAPI and Docker experience.
    """

    result = compare_resume_job(
        resume,
        job,
    )

    assert "category_coverage" in result

    assert isinstance(
        result["category_coverage"],
        dict,
    )

    assert result["category_coverage"]["Programming"] == 100


def test_compare_resume_job_detects_critical_missing_skills():
    resume = """
    Python developer with SQL and TensorFlow experience.
    """

    job = """
    Required: Python, SQL, TensorFlow and Docker.
    """

    result = compare_resume_job(
        resume,
        job,
    )

    assert "critical_missing_skills" in result

    assert isinstance(
        result["critical_missing_skills"],
        list,
    )


def test_compare_resume_job_returns_match_level():
    resume = """
    Python developer with SQL, TensorFlow,
    Docker and AWS experience.
    """

    job = """
    Looking for Python, SQL, TensorFlow,
    Docker and AWS experience.
    """

    result = compare_resume_job(
        resume,
        job,
    )

    assert "match_level" in result

    assert result["match_level"] in {
        "Excellent",
        "Strong",
        "Moderate",
        "Weak",
        "No Match",
    }


def test_compare_resume_job_score_is_bounded():
    resume = """
    Python SQL TensorFlow Docker AWS
    """

    job = """
    Python SQL TensorFlow Docker AWS
    """

    result = compare_resume_job(
        resume,
        job,
    )

    assert 0 <= result["match_score"] <= 100