"""
File: app/main.py
Purpose: Application entry point.

What this file does:
- Creates the FastAPI app
- Loads shared settings
- Registers startup/shutdown behavior
- Adds middleware such as CORS
- Mounts all API routes under the versioned API prefix
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Centralized app settings loaded from .env via pydantic-settings.
from app.core.config import settings

# The versioned API router that combines auth/chat endpoints.
from app.api.v1.api import api_router

# SQLAlchemy metadata + engine used to create DB tables on startup.
from app.core.db import Base, engine

# Create the FastAPI application object. This is the main app instance that
# the ASGI server (for example uvicorn) will run.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI Backend",
)


@app.on_event("startup")
def on_startup():
    # Create tables for all SQLAlchemy models that inherit from Base.
    # This is convenient for small projects, though larger apps usually
    # use migrations instead of create_all().
    Base.metadata.create_all(bind=engine)
    print("Application startup complete")


@app.on_event("shutdown")
def on_shutdown():
    # Placeholder shutdown hook for future cleanup work.
    print("Application shutdown complete")


# CORS tells browsers which frontend origins are allowed to call this API.
# Without this, a frontend on another origin (like localhost:3000) may be
# blocked by the browser even if the backend itself is running fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount all versioned API routes under the configured prefix, such as /api/v1.
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    # A tiny public route that helps confirm the server is alive.
    return {
        "message": "API is running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    # A minimal health endpoint commonly used by monitors or deployments.
    return {"status": "ok"}
