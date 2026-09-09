import pytest

from app.models.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceStrength,
    EvidenceType,
)
from app.models.skill import SkillCategory, SkillProfile


def make_evidence(
    evidence_type=EvidenceType.DEMONSTRATED,
    strength=EvidenceStrength.STRONG,
):
    return Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=evidence_type,
        source=EvidenceSource.PROJECT,
        text="Developed a machine learning model using Python.",
        strength=strength,
        confidence=0.94,
    )


def test_valid_skill_profile():
    evidence = make_evidence()

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence,),
        strength=EvidenceStrength.STRONG,
        confidence=0.94,
    )

    assert skill.canonical_name == "Python"
    assert skill.category is SkillCategory.PROGRAMMING
    assert skill.evidence_count == 1
    assert skill.strength is EvidenceStrength.STRONG
    assert skill.confidence == 0.94


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_skill_name_is_rejected(name):
    with pytest.raises(ValueError, match="canonical_name"):
        SkillProfile(
            canonical_name=name,
            category=SkillCategory.PROGRAMMING,
        )


@pytest.mark.parametrize("confidence", [-0.01, 1.01, 2.0])
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValueError, match="confidence"):
        SkillProfile(
            canonical_name="Python",
            category=SkillCategory.PROGRAMMING,
            confidence=confidence,
        )


def test_empty_evidence_is_allowed():
    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
    )

    assert skill.evidence == ()
    assert skill.evidence_count == 0
    assert skill.is_demonstrated is False
    assert skill.is_verified is False


def test_declared_evidence_is_not_demonstrated():
    evidence = make_evidence(EvidenceType.DECLARED)

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence,),
    )

    assert skill.is_demonstrated is False
    assert skill.is_verified is False


def test_demonstrated_evidence_marks_skill_as_demonstrated():
    evidence = make_evidence(EvidenceType.DEMONSTRATED)

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence,),
    )

    assert skill.is_demonstrated is True
    assert skill.is_verified is False


def test_verified_evidence_marks_skill_as_verified():
    evidence = make_evidence(EvidenceType.VERIFIED)

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence,),
    )

    assert skill.is_demonstrated is True
    assert skill.is_verified is True


def test_multiple_evidence_items_are_supported():
    evidence_1 = make_evidence()
    evidence_2 = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DECLARED,
        source=EvidenceSource.SKILL_SECTION,
        text="Python",
        strength=EvidenceStrength.WEAK,
        confidence=0.99,
    )

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence_1, evidence_2),
    )

    assert skill.evidence_count == 2
    assert skill.is_demonstrated is True


def test_evidence_must_contain_evidence_objects():
    with pytest.raises(TypeError, match="Evidence instance"):
        SkillProfile(
            canonical_name="Python",
            category=SkillCategory.PROGRAMMING,
            evidence=("Python",),
        )


def test_evidence_collection_is_immutable():
    evidence = make_evidence()

    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
        evidence=(evidence,),
    )

    with pytest.raises(AttributeError):
        skill.canonical_name = "Java"


def test_default_strength_and_confidence_are_safe():
    skill = SkillProfile(
        canonical_name="Python",
        category=SkillCategory.PROGRAMMING,
    )

    assert skill.strength is EvidenceStrength.NONE
    assert skill.confidence == 0.0