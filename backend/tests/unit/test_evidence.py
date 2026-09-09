import pytest

from app.models.evidence import (
    Evidence,
    EvidenceSource,
    EvidenceStrength,
    EvidenceType,
)


def test_valid_evidence_creation():
    evidence = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DEMONSTRATED,
        source=EvidenceSource.PROJECT,
        text="Developed a machine learning model using Python.",
        location="Project → Crop Disease Prediction",
        strength=EvidenceStrength.STRONG,
        confidence=0.94,
        relationship="USED_WITH",
    )

    assert evidence.entity_type == "skill"
    assert evidence.entity_id == "python"
    assert evidence.evidence_type is EvidenceType.DEMONSTRATED
    assert evidence.source is EvidenceSource.PROJECT
    assert evidence.strength is EvidenceStrength.STRONG
    assert evidence.confidence == 0.94


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("entity_type", ""),
        ("entity_type", "   "),
        ("entity_id", ""),
        ("entity_id", "   "),
        ("text", ""),
        ("text", "   "),
    ],
)
def test_required_text_fields_reject_empty_values(field, value):
    values = {
        "entity_type": "skill",
        "entity_id": "python",
        "evidence_type": EvidenceType.DEMONSTRATED,
        "source": EvidenceSource.PROJECT,
        "text": "Used Python to build a model.",
    }

    values[field] = value

    with pytest.raises(ValueError):
        Evidence(**values)


@pytest.mark.parametrize("confidence", [-0.01, 1.01, 2.0, -1.0])
def test_confidence_must_be_between_zero_and_one(confidence):
    with pytest.raises(ValueError, match="confidence"):
        Evidence(
            entity_type="skill",
            entity_id="python",
            evidence_type=EvidenceType.DEMONSTRATED,
            source=EvidenceSource.PROJECT,
            text="Used Python to build a model.",
            confidence=confidence,
        )


@pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
def test_valid_confidence_values_are_accepted(confidence):
    evidence = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DEMONSTRATED,
        source=EvidenceSource.PROJECT,
        text="Used Python to build a model.",
        confidence=confidence,
    )

    assert evidence.confidence == confidence


def test_optional_fields_default_to_none():
    evidence = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DECLARED,
        source=EvidenceSource.SKILL_SECTION,
        text="Python",
    )

    assert evidence.location is None
    assert evidence.relationship is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("location", ""),
        ("location", "   "),
        ("relationship", ""),
        ("relationship", "   "),
    ],
)
def test_optional_text_fields_reject_blank_values(field, value):
    values = {
        "entity_type": "skill",
        "entity_id": "python",
        "evidence_type": EvidenceType.DECLARED,
        "source": EvidenceSource.SKILL_SECTION,
        "text": "Python",
    }

    values[field] = value

    with pytest.raises(ValueError):
        Evidence(**values)


def test_evidence_is_immutable():
    evidence = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DEMONSTRATED,
        source=EvidenceSource.PROJECT,
        text="Used Python to build a model.",
        confidence=0.9,
    )

    with pytest.raises(AttributeError):
        evidence.confidence = 1.0


def test_enum_values_are_stable_strings():
    assert EvidenceType.DECLARED.value == "declared"
    assert EvidenceType.DEMONSTRATED.value == "demonstrated"
    assert EvidenceType.VERIFIED.value == "verified"

    assert EvidenceStrength.NONE.value == "none"
    assert EvidenceStrength.WEAK.value == "weak"
    assert EvidenceStrength.MODERATE.value == "moderate"
    assert EvidenceStrength.STRONG.value == "strong"
    assert EvidenceStrength.VERIFIED.value == "verified"


def test_evidence_defaults_are_safe():
    evidence = Evidence(
        entity_type="skill",
        entity_id="python",
        evidence_type=EvidenceType.DECLARED,
        source=EvidenceSource.RESUME,
        text="Python",
    )

    assert evidence.strength is EvidenceStrength.WEAK
    assert evidence.confidence == 0.0