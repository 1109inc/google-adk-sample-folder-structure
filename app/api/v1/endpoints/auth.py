"""
File: app/api/v1/endpoints/auth.py
Purpose: Authentication and current-user endpoints.

What this file does:
- Registers new users
- Logs users in and returns JWT access tokens
- Returns the currently authenticated user's profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # Before creating a user, make sure the email is not already taken.
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create a new ORM object that represents one row in the users table.
    # We store a hashed password, never the plain password itself.
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )

    # Persist the user to the database.
    db.add(user)
    db.commit()
    db.refresh(user)

    # FastAPI will shape this ORM object into UserResponse automatically.
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Find the user record by email first.
    user = db.query(User).filter(User.email == payload.email).first()

    # Reject the request if the user does not exist or the password is wrong.
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Store the user id in the token subject claim ("sub").
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # get_current_user has already verified the token and loaded the user.
    return current_user
