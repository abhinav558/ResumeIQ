"""
ResumeIQ - User Repository.

Database operations for persistent user accounts.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    *,
    user_id: str,
    name: str,
    email: str,
    password_hash: str,
) -> User:
    """Create and persist a new user."""

    user = User(
        id=user_id,
        name=name,
        email=email.lower().strip(),
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """Retrieve a user by normalized email address."""

    statement = select(User).where(
        User.email == email.lower().strip()
    )

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: str,
) -> User | None:
    """Retrieve a user by ID."""

    statement = select(User).where(
        User.id == user_id
    )

    return db.scalar(statement)