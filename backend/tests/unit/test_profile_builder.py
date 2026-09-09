from app.models.achievement import AchievementType
from app.models.certification import CertificationProfile
from app.models.education import EducationLevel
from app.models.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceStrength,
    EvidenceType,
)
from app.models.experience import ExperienceType
from app.models.metric import MetricType
from app.models.project import ProjectQuality
from app.models.skill import SkillCategory
from app.services.candidate.profile_builder import CandidateProfileBuilder


def test_build_empty_analysis():
    profile = CandidateProfileBuilder().build(
        {},
        candidate_id="candidate-1",
    )

    assert profile.candidate_id == "candidate-1"
    assert profile.skills == ()
    assert profile.projects == ()
    assert profile.experience == ()
    assert profile.education == ()
    assert profile.certifications == ()
    assert profile.achievements == ()
    assert profile.metrics == ()
    assert profile.evidence == ()
    assert profile.confidence == 0.0


def test_build_candidate_contact_information():
    analysis = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91 9876543210",
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe",
        "summary": "AI/ML Engineer",
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-1",
    )

    assert profile.name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.phone == "+91 9876543210"
    assert profile.linkedin == "https://linkedin.com/in/johndoe"
    assert profile.github == "https://github.com/johndoe"
    assert profile.summary == "AI/ML Engineer"


def test_build_contact_information_from_contact_object():
    analysis = {
        "contact": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "1234567890",
            "linkedin": "linkedin-url",
            "github": "github-url",
        }
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-2",
    )

    assert profile.name == "Jane Doe"
    assert profile.email == "jane@example.com"
    assert profile.phone == "1234567890"
    assert profile.linkedin == "linkedin-url"
    assert profile.github == "github-url"


def test_contact_object_takes_priority():
    analysis = {
        "name": "Old Name",
        "email": "old@example.com",
        "contact": {
            "name": "New Name",
            "email": "new@example.com",
        },
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-3",
    )

    assert profile.name == "New Name"
    assert profile.email == "new@example.com"


def test_build_skill_profile():
    analysis = {
        "skills_analysis": {
            "skill_details": [
                {
                    "canonical_name": "Python",
                    "category": "programming",
                    "strength": "strong",
                    "confidence": 0.95,
                    "evidence": [
                        {
                            "text": "Developed ML applications using Python",
                            "evidence_type": "demonstrated",
                            "source": "project",
                            "strength": "strong",
                            "confidence": 0.95,
                        }
                    ],
                }
            ]
        }
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-4",
    )

    assert len(profile.skills) == 1

    skill = profile.skills[0]

    assert skill.canonical_name == "Python"
    assert skill.category == SkillCategory.PROGRAMMING
    assert skill.strength == EvidenceStrength.STRONG
    assert skill.confidence == 0.95
    assert skill.evidence_count == 1
    assert skill.is_demonstrated is True


def test_build_project_profile():
    analysis = {
        "projects_analysis": [
            {
                "title": "ResumeIQ",
                "technologies": ["Python", "FastAPI", "React"],
                "actions": ["Built", "Integrated"],
                "metrics": ["95% accuracy"],
                "deployment": ["Streamlit"],
                "engineering": ["REST API"],
                "strengths": ["Production-oriented"],
                "score": 88,
                "quality": "excellent",
                "confidence": 0.92,
                "evidence": [
                    {
                        "text": "Built ResumeIQ using Python and FastAPI",
                        "evidence_type": "demonstrated",
                        "source": "project",
                        "strength": "strong",
                        "confidence": 0.92,
                    }
                ],
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-5",
    )

    assert len(profile.projects) == 1

    project = profile.projects[0]

    assert project.title == "ResumeIQ"
    assert project.technologies == (
        "Python",
        "FastAPI",
        "React",
    )
    assert project.actions == ("Built", "Integrated")
    assert project.metrics == ("95% accuracy",)
    assert project.deployment == ("Streamlit",)
    assert project.engineering == ("REST API",)
    assert project.score == 88
    assert project.quality == ProjectQuality.EXCELLENT
    assert project.confidence == 0.92
    assert project.evidence_count == 1


def test_project_quality_is_derived_when_missing():
    analysis = {
        "projects_analysis": [
            {
                "title": "Project A",
                "score": 75,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-6",
    )

    assert profile.projects[0].quality == ProjectQuality.GOOD


def test_build_experience_profile():
    analysis = {
        "experience_analysis": [
            {
                "title": "AI/ML Intern",
                "company": "Example Corp",
                "experience_type": "internship",
                "start_date": "2025-01",
                "end_date": "2025-06",
                "duration_months": 6,
                "is_current": False,
                "technologies": ["Python", "TensorFlow"],
                "achievements": ["Built prediction model"],
                "metrics": ["95% accuracy"],
                "confidence": 0.90,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-7",
    )

    experience = profile.experience[0]

    assert experience.title == "AI/ML Intern"
    assert experience.company == "Example Corp"
    assert experience.experience_type == ExperienceType.INTERNSHIP
    assert experience.start_date == "2025-01"
    assert experience.end_date == "2025-06"
    assert experience.duration_months == 6
    assert experience.is_current is False
    assert experience.technologies == ("Python", "TensorFlow")
    assert experience.achievements == ("Built prediction model",)
    assert experience.metrics == ("95% accuracy",)
    assert experience.confidence == 0.90


def test_build_education_profile():
    analysis = {
        "education_analysis": [
            {
                "degree": "B.Tech",
                "field_of_study": "Artificial Intelligence and Machine Learning",
                "institution": "Example University",
                "education_level": "bachelors",
                "start_date": "2022",
                "end_date": "2026",
                "cgpa": 8.8,
                "percentage": 88.0,
                "achievements": ["Academic excellence"],
                "confidence": 0.94,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-8",
    )

    education = profile.education[0]

    assert education.degree == "B.Tech"
    assert education.field_of_study == (
        "Artificial Intelligence and Machine Learning"
    )
    assert education.institution == "Example University"
    assert education.education_level == EducationLevel.BACHELORS
    assert education.start_date == "2022"
    assert education.end_date == "2026"
    assert education.cgpa == 8.8
    assert education.percentage == 88.0
    assert education.achievements == ("Academic excellence",)
    assert education.confidence == 0.94


def test_build_certification_profile():
    analysis = {
        "certifications_analysis": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "provider": "AWS",
                "issue_date": "2026-01",
                "credential_id": "ABC123",
                "credential_url": "https://example.com/credential",
                "skills": ["AWS", "Cloud"],
                "verified": True,
                "confidence": 0.98,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-9",
    )

    certification = profile.certifications[0]

    assert isinstance(certification, CertificationProfile)
    assert certification.name == "AWS Certified Cloud Practitioner"
    assert certification.provider == "AWS"
    assert certification.issue_date == "2026-01"
    assert certification.credential_id == "ABC123"
    assert certification.credential_url == (
        "https://example.com/credential"
    )
    assert certification.skills == ("AWS", "Cloud")
    assert certification.verified is True
    assert certification.confidence == 0.98


def test_build_achievement_profile():
    analysis = {
        "achievements": [
            {
                "title": "Hackathon Winner",
                "achievement_type": "hackathon",
                "organization": "Tech Club",
                "date": "2026",
                "description": "Won first place.",
                "metrics": ["1st place"],
                "skills": ["Python", "AI"],
                "confidence": 0.91,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-10",
    )

    achievement = profile.achievements[0]

    assert achievement.title == "Hackathon Winner"
    assert achievement.achievement_type == AchievementType.HACKATHON
    assert achievement.organization == "Tech Club"
    assert achievement.date == "2026"
    assert achievement.description == "Won first place."
    assert achievement.metrics == ("1st place",)
    assert achievement.skills == ("Python", "AI")
    assert achievement.confidence == 0.91


def test_build_metrics_from_strings():
    analysis = {
        "metrics": [
            "95% accuracy",
            "20% performance improvement",
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-11",
    )

    assert len(profile.metrics) == 2
    assert profile.metrics[0].value == "95% accuracy"
    assert profile.metrics[0].metric_type == MetricType.OTHER
    assert profile.metrics[0].confidence == 0.70


def test_build_structured_metrics():
    analysis = {
        "metrics": [
            {
                "value": "95%",
                "metric_type": "percentage",
                "description": "Model accuracy",
                "source_text": "Achieved 95% accuracy",
                "confidence": 0.96,
            }
        ]
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-12",
    )

    metric = profile.metrics[0]

    assert metric.value == "95%"
    assert metric.metric_type == MetricType.PERCENTAGE
    assert metric.description == "Model accuracy"
    assert metric.source_text == "Achieved 95% accuracy"
    assert metric.confidence == 0.96


def test_build_string_evidence():
    analysis = {
        "skills_analysis": {
            "skill_details": [
                {
                    "canonical_name": "Python",
                    "category": "programming",
                    "evidence": [
                        "Built applications using Python"
                    ],
                }
            ]
        }
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-13",
    )

    evidence = profile.skills[0].evidence[0]

    assert isinstance(evidence, Evidence)
    assert evidence.entity_type == "skill"
    assert evidence.entity_id == "Python"
    assert evidence.evidence_type == EvidenceType.DEMONSTRATED
    assert evidence.source == EvidenceSource.RESUME
    assert evidence.text == "Built applications using Python"
    assert evidence.strength == EvidenceStrength.MODERATE
    assert evidence.confidence == 0.70


def test_build_evidence_preserves_structured_values():
    analysis = {
        "skills_analysis": {
            "skill_details": [
                {
                    "canonical_name": "FastAPI",
                    "category": "backend",
                    "evidence": [
                        {
                            "entity_type": "skill",
                            "entity_id": "FastAPI",
                            "evidence_type": "verified",
                            "source": "project",
                            "text": "FastAPI used in deployed API",
                            "strength": "verified",
                            "confidence": 0.99,
                            "location": "Project: ResumeIQ",
                            "relationship": "implemented_with",
                        }
                    ],
                }
            ]
        }
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-14",
    )

    evidence = profile.skills[0].evidence[0]

    assert evidence.evidence_type == EvidenceType.VERIFIED
    assert evidence.source == EvidenceSource.PROJECT
    assert evidence.strength == EvidenceStrength.VERIFIED
    assert evidence.confidence == 0.99
    assert evidence.location == "Project: ResumeIQ"
    assert evidence.relationship == "implemented_with"


def test_candidate_evidence_is_deduplicated():
    shared_evidence = {
        "text": "Built ML application using Python",
        "evidence_type": "demonstrated",
        "source": "project",
        "strength": "strong",
        "confidence": 0.90,
    }

    analysis = {
        "skills_analysis": {
            "skill_details": [
                {
                    "canonical_name": "Python",
                    "category": "programming",
                    "evidence": [shared_evidence],
                }
            ]
        },
        "projects_analysis": [
            {
                "title": "ML Project",
                "evidence": [shared_evidence],
            }
        ],
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-15",
    )

    assert len(profile.evidence) == 2


def test_invalid_analysis_type_is_rejected():
    builder = CandidateProfileBuilder()

    try:
        builder.build(
            [],
            candidate_id="candidate-16",
        )
    except TypeError as exc:
        assert str(exc) == "analysis must be a dictionary"
    else:
        raise AssertionError("Expected TypeError")


def test_empty_candidate_id_is_rejected():
    builder = CandidateProfileBuilder()

    try:
        builder.build(
            {},
            candidate_id="   ",
        )
    except ValueError as exc:
        assert str(exc) == "candidate_id must not be empty"
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_items_are_ignored_safely():
    analysis = {
        "skills_analysis": {
            "skill_details": [
                None,
                "invalid",
                {},
                {
                    "canonical_name": "Python",
                    "category": "programming",
                },
            ]
        },
        "projects_analysis": [
            None,
            "invalid",
            {},
            {
                "title": "Valid Project",
            },
        ],
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-17",
    )

    assert len(profile.skills) == 1
    assert len(profile.projects) == 1
    assert profile.skills[0].canonical_name == "Python"
    assert profile.projects[0].title == "Valid Project"


def test_confidence_is_derived_from_profile_confidences():
    analysis = {
        "skills_analysis": {
            "skill_details": [
                {
                    "canonical_name": "Python",
                    "category": "programming",
                    "confidence": 0.80,
                },
                {
                    "canonical_name": "FastAPI",
                    "category": "backend",
                    "confidence": 1.00,
                },
            ]
        },
        "projects_analysis": [
            {
                "title": "ResumeIQ",
                "confidence": 0.90,
            }
        ],
    }

    profile = CandidateProfileBuilder().build(
        analysis,
        candidate_id="candidate-18",
    )

    assert profile.confidence == 0.9