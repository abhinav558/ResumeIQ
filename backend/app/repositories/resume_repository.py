"""
ResumeIQ - Resume Repository.

Database operations for persistent, user-owned resumes.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume import Resume


def create_resume(
    db: Session,
    *,
    resume_id: str,
    user_id: str,
    name: str,
    resume_text: str,
    analysis_json: str,
) -> Resume:
    """Create and persist a new resume."""

    resume = Resume(
        id=resume_id,
        user_id=user_id,
        name=name.strip(),
        resume_text=resume_text,
        analysis_json=analysis_json,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def get_resume_by_id(
    db: Session,
    *,
    resume_id: str,
    user_id: str,
) -> Resume | None:
    """Retrieve a resume belonging to a specific user."""

    statement = select(Resume).where(
        Resume.id == resume_id,
        Resume.user_id == user_id,
    )

    return db.scalar(statement)


def get_resumes_by_user(
    db: Session,
    *,
    user_id: str,
) -> list[Resume]:
    """Retrieve all resumes belonging to a specific user."""

    statement = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.updated_at.desc())
    )

    return list(db.scalars(statement).all())


def update_resume(
    db: Session,
    *,
    resume: Resume,
    name: str | None = None,
    resume_text: str | None = None,
    analysis_json: str | None = None,
) -> Resume:
    """Update an existing resume."""

    if name is not None:
        resume.name = name.strip()

    if resume_text is not None:
        resume.resume_text = resume_text

    if analysis_json is not None:
        resume.analysis_json = analysis_json

    db.commit()
    db.refresh(resume)

    return resume


def delete_resume(
    db: Session,
    *,
    resume: Resume,
) -> None:
    """Delete an existing resume."""

    db.delete(resume)
    db.commit()