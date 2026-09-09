"""
ResumeIQ - Authentication Security.

JWT creation/validation and password hashing.
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

SECRET_KEY = os.getenv(
    "RESUMEIQ_SECRET_KEY",
    "development-only-change-this-secret-key",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


# ------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its hash."""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# ------------------------------------------------------------------
# JWT
# ------------------------------------------------------------------

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    The subject is normally the user's ID.
    """

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> str | None:
    """
    Decode and validate a JWT.

    Returns the user ID when valid.
    Returns None when invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if not subject:
            return None

        return str(subject)

    except JWTError:
        return None