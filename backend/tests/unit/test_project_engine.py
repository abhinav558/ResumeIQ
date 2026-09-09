import pytest

from app.services.project_engine import (
    clean_text,
    detect_technologies,
    calculate_complexity,
    calculate_impact,
    calculate_metrics,
    calculate_deployment,
    calculate_engineering,
    analyze_single_project,
    is_project_title,
    split_projects,
    project_quality,
    analyze_projects,
)


# ============================================================
# CLEANING
# ============================================================

def test_clean_text_normalizes_whitespace():
    text = "  Python\n\n   TensorFlow   Flask  "

    result = clean_text(text)

    assert result == "python tensorflow flask"


def test_clean_text_handles_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


# ============================================================
# TECHNOLOGY DETECTION
# ============================================================

def test_detect_technologies():
    text = """
    Developed using Python, TensorFlow, NumPy and Flask.
    """

    result = detect_technologies(clean_text(text))

    assert "python" in result
    assert "tensorflow" in result
    assert "numpy" in result
    assert "flask" in result


def test_detect_technologies_does_not_duplicate():
    text = "Python Python Python TensorFlow"

    result = detect_technologies(clean_text(text))

    assert result.count("python") == 1
    assert result.count("tensorflow") == 1


# ============================================================
# COMPLEXITY
# ============================================================

def test_complexity_detects_machine_learning():
    result = calculate_complexity(
        clean_text(
            "Built a machine learning prediction system"
        )
    )

    assert result["score"] > 0
    assert "machine learning" in result["features"]
    assert "prediction" in result["features"]


def test_complexity_detects_deep_learning():
    result = calculate_complexity(
        clean_text(
            "Developed a deep learning CNN classification model"
        )
    )

    assert result["score"] > 0
    assert "deep learning" in result["features"]
    assert "cnn" in result["features"]
    assert "classification" in result["features"]


def test_complexity_is_bounded():
    text = " ".join(
        [
            "machine learning",
            "deep learning",
            "neural network",
            "cnn",
            "transformer",
            "llm",
            "blockchain",
            "federated learning",
            "computer vision",
            "nlp",
            "prediction",
            "classification",
            "forecasting",
            "optimization",
            "automation",
        ]
    )

    result = calculate_complexity(text)

    assert 0 <= result["score"] <= 40


# ============================================================
# IMPACT
# ============================================================

def test_impact_detects_action_verbs():
    result = calculate_impact(
        clean_text(
            "Developed and implemented a machine learning model"
        )
    )

    assert result["score"] > 0
    assert "developed" in result["keywords"]
    assert "implemented" in result["keywords"]


def test_impact_is_bounded():
    text = """
    developed built designed implemented created optimized
    improved reduced increased achieved trained integrated
    """

    result = calculate_impact(clean_text(text))

    assert 0 <= result["score"] <= 25


# ============================================================
# METRICS
# ============================================================

def test_metrics_detect_percentage():
    result = calculate_metrics(
        clean_text(
            "Achieved 95% accuracy"
        )
    )

    assert "95%" in result["metrics_found"]
    assert result["score"] > 0


def test_metrics_detect_plus_values():
    result = calculate_metrics(
        clean_text(
            "Processed 1000+ records"
        )
    )

    assert "1000+" in result["metrics_found"]


def test_metrics_detect_counts():
    result = calculate_metrics(
        clean_text(
            "Trained using 500 images"
        )
    )

    assert any(
        "500" in metric
        for metric in result["metrics_found"]
    )


def test_metrics_do_not_treat_phone_number_as_metric():
    result = calculate_metrics(
        clean_text(
            "Contact: 8688190792"
        )
    )

    assert result["metrics_found"] == []


# ============================================================
# DEPLOYMENT
# ============================================================

def test_deployment_detects_flask():
    result = calculate_deployment(
        clean_text(
            "Deployed the prediction model using Flask"
        )
    )

    assert result["score"] > 0
    assert "flask" in result["features"]


def test_deployment_detects_api():
    result = calculate_deployment(
        clean_text(
            "Built a REST API for model inference"
        )
    )

    assert result["score"] > 0
    assert "api" in result["features"]


def test_deployment_detects_streamlit():
    result = calculate_deployment(
        clean_text(
            "Created a Streamlit deployment"
        )
    )

    assert result["score"] > 0
    assert "streamlit" in result["features"]


# ============================================================
# ENGINEERING
# ============================================================

def test_engineering_detects_git():
    result = calculate_engineering(
        clean_text(
            "Managed source code using Git and GitHub"
        )
    )

    assert result["score"] > 0
    assert "git" in result["features"]
    assert "github" in result["features"]


def test_engineering_detects_testing():
    result = calculate_engineering(
        clean_text(
            "Added unit testing and debugging"
        )
    )

    assert result["score"] > 0
    assert "testing" in result["features"]
    assert "debugging" in result["features"]


# ============================================================
# PROJECT TITLE DETECTION
# ============================================================

@pytest.mark.parametrize(
    "title",
    [
        "Python",
        "TensorFlow",
        "Flask",
        "GitHub",
        "Blockchain",
        "Machine Learning",
        "Deep Learning",
        "Technologies",
        "Skills",
    ],
)
def test_technology_names_are_not_project_titles(title):
    assert is_project_title(title) is False


@pytest.mark.parametrize(
    "title",
    [
        "EV Energy Prediction System",
        "Movie Recommendation System",
        "Crop Disease Detection",
        "Resume Intelligence Platform",
        "Student Management Application",
        "Facial Recognition System",
    ],
)
def test_real_project_titles_are_detected(title):
    assert is_project_title(title) is True


def test_bullet_lines_are_not_project_titles():
    assert (
        is_project_title(
            "- Developed a machine learning model"
        )
        is False
    )


def test_long_description_is_not_project_title():
    text = (
        "Developed a privacy preserving machine learning system "
        "using federated learning and blockchain technology "
        "for electric vehicle energy prediction"
    )

    assert is_project_title(text) is False


# ============================================================
# PROJECT SPLITTING
# ============================================================

def test_split_projects_returns_one_project():
    text = """
    EV Energy Prediction System

    Developed a machine learning system for electric vehicles.

    Implemented federated learning using TensorFlow.

    Integrated blockchain for privacy.

    Technologies: Python, TensorFlow, Blockchain
    """

    result = split_projects(text)

    assert len(result) == 1


def test_split_projects_returns_two_projects():
    text = """
    EV Energy Prediction System

    Developed an energy prediction system using federated learning.

    Movie Recommendation System

    Built a recommendation engine using Python and machine learning.
    """

    result = split_projects(text)

    assert len(result) == 2


def test_split_projects_returns_three_projects():
    text = """
    EV Energy Prediction System

    Built an energy prediction model.

    Movie Recommendation System

    Built a movie recommendation platform.

    Crop Disease Detection

    Developed a crop disease classification system.
    """

    result = split_projects(text)

    assert len(result) == 3


def test_split_projects_does_not_create_projects_from_technologies():
    text = """
    EV Energy Prediction System

    Python
    TensorFlow
    NumPy
    Flask

    Developed a prediction model.
    """

    result = split_projects(text)

    assert len(result) == 1


def test_split_projects_does_not_create_project_from_prediction():
    text = """
    EV Energy Prediction System

    Prediction

    Developed a prediction model for electric vehicles.
    """

    result = split_projects(text)

    assert len(result) == 1


def test_split_projects_handles_bullet_descriptions():
    text = """
    Crop Disease Detection

    - Developed a CNN model for crop disease classification.
    - Trained the model using TensorFlow.
    - Built a Flask API for prediction.
    """

    result = split_projects(text)

    assert len(result) == 1
    assert "cnn" in result[0].lower()
    assert "tensorflow" in result[0].lower()
    assert "flask" in result[0].lower()


def test_split_projects_removes_empty_entries():
    result = split_projects(
        """
        EV Energy Prediction System


        """
    )

    assert isinstance(result, list)


# ============================================================
# SINGLE PROJECT ANALYSIS
# ============================================================

def test_analyze_single_project_returns_complete_structure():
    project = """
    EV Energy Prediction System

    Developed a machine learning prediction system.

    Implemented federated learning using TensorFlow.

    Integrated blockchain for privacy.

    Achieved 95% accuracy.

    Deployed using Flask.

    Managed source code using GitHub.
    """

    result = analyze_single_project(project)

    assert isinstance(result, dict)

    assert "score" in result
    assert "technologies" in result
    assert "complexity" in result
    assert "impact" in result
    assert "metrics" in result
    assert "deployment" in result
    assert "engineering" in result
    assert "strengths" in result


def test_analyze_single_project_score_is_bounded():
    project = """
    Developed a machine learning deep learning CNN prediction
    system using Python TensorFlow NumPy Pandas Flask Docker AWS
    blockchain federated learning GitHub.

    Achieved 95% accuracy.

    Deployed using Flask REST API.

    Added unit testing and debugging.
    """

    result = analyze_single_project(project)

    assert 0 <= result["score"] <= 100


# ============================================================
# QUALITY
# ============================================================

@pytest.mark.parametrize(
    "score, expected",
    [
        (90, "Excellent"),
        (85, "Excellent"),
        (70, "Good"),
        (69, "Average"),
        (50, "Average"),
        (49, "Basic"),
        (0, "Basic"),
    ],
)
def test_project_quality(score, expected):
    assert project_quality(score) == expected


# ============================================================
# MAIN PROJECT ANALYZER
# ============================================================

def test_analyze_projects_handles_invalid_input():
    result = analyze_projects(None)

    assert result["score"] == 0
    assert result["project_count"] == 0
    assert result["projects"] == []


def test_analyze_projects_handles_missing_projects():
    result = analyze_projects({})

    assert result["score"] == 0
    assert result["project_count"] == 0
    assert result["projects"] == []


def test_analyze_projects_returns_one_real_project():
    sections = {
        "projects": """
        EV Energy Prediction System

        Developed a machine learning prediction system.

        Implemented federated learning using TensorFlow.

        Integrated blockchain for privacy.

        Achieved 95% accuracy.

        Technologies: Python, TensorFlow, Blockchain
        """
    }

    result = analyze_projects(sections)

    assert result["project_count"] == 1
    assert len(result["projects"]) == 1
    assert result["score"] >= 0


def test_analyze_projects_returns_two_real_projects():
    sections = {
        "projects": """
        EV Energy Prediction System

        Developed a machine learning prediction system.

        Movie Recommendation System

        Built a recommendation engine using Python.
        """
    }

    result = analyze_projects(sections)

    assert result["project_count"] == 2
    assert len(result["projects"]) == 2


def test_analyze_projects_is_deterministic():
    sections = {
        "projects": """
        EV Energy Prediction System

        Developed a machine learning prediction system.

        Implemented federated learning using TensorFlow.

        Achieved 95% accuracy.

        Technologies: Python, TensorFlow
        """
    }

    first = analyze_projects(sections)
    second = analyze_projects(sections)

    assert first == second


def test_analyze_projects_has_technology_summary():
    sections = {
        "projects": """
        EV Energy Prediction System

        Developed using Python and TensorFlow.

        Movie Recommendation System

        Built using Python and Scikit-Learn.
        """
    }

    result = analyze_projects(sections)

    assert "technologies" in result
    assert isinstance(result["technologies"], list)