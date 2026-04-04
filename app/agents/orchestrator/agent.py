"""
File: app/agents/orchestrator/agent.py
Purpose: Define the main ADK agent used by the application.

What this file does:
- Creates the root agent object
- Chooses the model/instruction set
- Attaches logging callbacks for debugging and visibility
"""

from google.adk.agents.llm_agent import Agent
from app.agents.callbacks import (log_before_agent,log_after_agent,log_before_tool,log_after_tool,log_before_model,log_after_model)
from app.core.llm_config import get_default_model

# The root agent is the primary assistant that the chat endpoint calls.
root_agent = Agent(
    # This is the currently selected model for the agent.
    model="gemini-2.5-flash",

    # Internal identifier for the agent.
    name='root_agent',

    # Short human-readable description.
    description=""""
        You are the User agent.
        """,

    # Main behavioral instruction/prompt for the assistant.
    instruction="""
        You are the primary AI assistant.
        Help the user clearly, accurately, and professionally.
        Personalize responses when useful based on the user context provided in the chat request.
        Stay grounded in the user's request and do not make up user details.
    """,

    # Callbacks print helpful logs before/after agent/model/tool events.
    before_agent_callback=log_before_agent,
    after_agent_callback=log_after_agent,
    before_tool_callback=log_before_tool,
    after_tool_callback=log_after_tool,
    before_model_callback=log_before_model,
    after_model_callback=log_after_model,
)
