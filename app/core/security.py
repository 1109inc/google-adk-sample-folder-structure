"""
File: app/core/security.py
Purpose: Password hashing and JWT token utilities.

What this file does:
- Hashes plain-text passwords before saving them
- Verifies login passwords against stored hashes
- Creates access tokens for authenticated users
- Decodes and validates access tokens from incoming requests
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings


def hash_password(password: str) -> str:
    # bcrypt works with bytes, so we encode the incoming string first.
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Store the hash as a normal string in the database.
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # To verify a password, bcrypt compares the entered password to the
    # stored hash. We never decrypt the original password because hashing
    # is intentionally one-way.
    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # Copy the payload so we do not mutate the caller's original dict.
    to_encode = data.copy()

    # JWT tokens usually include an expiration ("exp") claim.
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    # Sign the JWT so the server can verify it later.
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    try:
        # If the token is tampered with, expired, or signed with the wrong
        # secret, jose will raise JWTError.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # Returning None makes it easy for the dependency layer to reject it.
        return None
