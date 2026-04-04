"""
File: app/schemas/auth.py
Purpose: Pydantic schemas for auth-related requests and responses.

What this file does:
- Validates incoming JSON bodies for signup/login
- Defines the shape of token responses
- Defines the safe user fields returned to clients
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    # Expected request body for signup.
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    # Expected request body for login.
    email: EmailStr
    password: str


class Token(BaseModel):
    # Response returned after successful login.
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    # Safe user fields returned to the frontend.
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        # Allow Pydantic to build this response model from ORM objects.
        from_attributes = True
