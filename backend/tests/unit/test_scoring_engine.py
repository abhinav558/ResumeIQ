import pytest

from app.services.scoring_engine import (
    WEIGHTS,
    calculate_score,
    generate_rating,
    generate_recommendations,
)


class TestGenerateRating:

    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (100, "Excellent"),
            (90, "Excellent"),
            (89.99, "Very Good"),
            (75, "Very Good"),
            (74.99, "Good"),
            (60, "Good"),
            (59.99, "Average"),
            (45, "Average"),
            (44.99, "Needs Improvement"),
            (0, "Needs Improvement"),
        ],
    )
    def test_rating_boundaries(self, score, expected):
        assert generate_rating(score) == expected


class TestCalculateScore:

    def test_perfect_resume_scores_100(self):
        result = calculate_score(
            skills=100,
            projects=100,
            experience=100,
            ats=100,
            certifications=100,
            education=100,
            achievements=100,
        )

        assert result["resume_intelligence_score"] == 100
        assert result["rating"] == "Excellent"

    def test_zero_scores_score_zero(self):
        result = calculate_score(
            skills=0,
            projects=0,
            experience=0,
            ats=0,
            certifications=0,
            education=0,
            achievements=0,
        )

        assert result["resume_intelligence_score"] == 0
        assert result["rating"] == "Needs Improvement"

    def test_weight_sum_is_one(self):
        assert sum(WEIGHTS.values()) == pytest.approx(1.0)

    def test_score_breakdown_preserves_component_scores(self):
        result = calculate_score(
            skills=90,
            projects=80,
            experience=70,
            ats=60,
            certifications=50,
            education=40,
            achievements=30,
        )

        assert result["score_breakdown"] == {
            "skills": 90,
            "projects": 80,
            "experience": 70,
            "ats": 60,
            "certifications": 50,
            "education": 40,
            "achievements": 30,
        }

    def test_weighted_score_is_calculated_correctly(self):
        result = calculate_score(
            skills=90,
            projects=80,
            experience=70,
            ats=60,
            certifications=50,
            education=40,
            achievements=30,
        )

        expected = (
            90 * WEIGHTS["skills"]
            + 80 * WEIGHTS["projects"]
            + 70 * WEIGHTS["experience"]
            + 60 * WEIGHTS["ats"]
            + 50 * WEIGHTS["certifications"]
            + 40 * WEIGHTS["education"]
            + 30 * WEIGHTS["achievements"]
        )

        assert result["resume_intelligence_score"] == round(expected, 2)

    def test_fresher_without_experience_is_not_crashed(self):
        result = calculate_score(
            skills=90,
            projects=70,
            experience=0,
            ats=80,
            certifications=60,
            education=100,
            achievements=0,
        )

        assert 0 <= result["resume_intelligence_score"] <= 100
        assert result["score_breakdown"]["experience"] == 0

    def test_input_values_are_not_mutated(self):
        values = {
            "skills": 90,
            "projects": 80,
            "experience": 0,
            "ats": 70,
            "certifications": 60,
            "education": 100,
            "achievements": 20,
        }

        original = values.copy()

        calculate_score(**values)

        assert values == original


class TestGenerateRecommendations:

    def test_low_project_score_generates_project_recommendation(self):
        result = generate_recommendations(
            {
                "skills": 90,
                "projects": 40,
                "experience": 0,
                "ats": 90,
                "certifications": 80,
                "education": 100,
                "achievements": 80,
            }
        )

        assert any("projects" in item.lower() for item in result)

    def test_low_ats_score_generates_ats_recommendation(self):
        result = generate_recommendations(
            {
                "skills": 90,
                "projects": 90,
                "experience": 0,
                "ats": 40,
                "certifications": 80,
                "education": 100,
                "achievements": 80,
            }
        )

        assert any("ats" in item.lower() for item in result)

    def test_low_experience_does_not_crash(self):
        result = generate_recommendations(
            {
                "skills": 90,
                "projects": 90,
                "experience": 0,
                "ats": 90,
                "certifications": 80,
                "education": 100,
                "achievements": 80,
            }
        )

        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_strong_resume_gets_positive_recommendation(self):
        result = generate_recommendations(
            {
                "skills": 90,
                "projects": 90,
                "experience": 90,
                "ats": 90,
                "certifications": 90,
                "education": 90,
                "achievements": 90,
            }
        )

        assert result == ["Resume is well optimized"]
def test_fresher_score_does_not_lose_experience_weight():
    result = calculate_score(
        skills=90,
        projects=70,
        experience=0,
        ats=80,
        certifications=60,
        education=100,
        achievements=0,
    )

    assert result["resume_intelligence_score"] > 50
    assert result["score_breakdown"]["experience"] == 0
    
def test_fresher_score_redistributes_missing_experience_weight():
    result = calculate_score(
        skills=100,
        projects=100,
        experience=0,
        ats=100,
        certifications=100,
        education=100,
        achievements=100,
    )

    assert result["resume_intelligence_score"] == 100
    assert result["score_breakdown"]["experience"] == 0
   