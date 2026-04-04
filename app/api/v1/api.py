"""
File: app/api/v1/api.py
Purpose: Combine version-1 API route groups.

What this file does:
- Creates a shared APIRouter for v1
- Mounts the auth and chat endpoint modules under their own prefixes
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth,chat

# Main router for API version 1.
api_router = APIRouter()

# Auth-related routes will live under /auth.
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Chat-related routes will live under /chat.
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
