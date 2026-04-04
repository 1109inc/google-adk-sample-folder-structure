"""
File: app/services/adk_service.py
Purpose: Build the ADK runner and its supporting services.

What this file does:
- Creates the chat session service
- Creates memory/artifact services used by the agent system
- Builds the shared runner used by the chat endpoint
"""

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from app.core.config import settings
from app.agents.orchestrator.agent import root_agent
import logging
logging.basicConfig(level=logging.INFO)
logging.info("BOOTING UP ALLYRA_HR_HUB ADK ENGINE...")

# 1. Session storage persists chat sessions in a database.
session_service = DatabaseSessionService(db_url=settings.SESSION_DB_URL)

# 2. Memory is kept in RAM for the running process.
memory_service = InMemoryMemoryService()

# 3. Artifacts are also kept in RAM for now.
artifact_service = InMemoryArtifactService()

# 4. The Runner is the main object that executes the agent for each request.
runner = Runner(
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
    artifact_service=artifact_service,
    app_name=settings.APP_NAME
)
