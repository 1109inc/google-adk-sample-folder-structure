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
from app.core.llm_config import (gemini_2_5_flash, gemini_2_5_pro, gpt_5_4_pro, gpt_4_1, gpt_5, gpt_5_pro, gpt_5_1, gpt_5_2, gpt_5_3, gpt_5_4, gpt_4o, claude_opus_4_6, claude_sonnet_4_6, grok_3, grok_4_20_multi_agent)
from app.tools.state_tools import set_user_state
# The root agent is the primary assistant that the chat endpoint calls.
root_agent = Agent(
    # This is the currently selected model for the agent.
    model=gemini_2_5_flash,

    # Internal identifier for the agent.
    name='root_agent',

    # Short human-readable description.
    description="""
        You are the User agent.
        """,

    # Main behavioral instruction/prompt for the assistant.
    instruction="""
        You are the primary AI assistant.
        Help the user clearly, accurately, and professionally.
        The following user profile fields may be available in session state:
        - Name: {user:name}
        - Email: {user:email}
        - Nickname: {user:nickname?}
        - Preferred language: {user:preferred_language?}
        Personalize responses only when those details are relevant to the user's request.
        If the user clearly asks to change a persistent preference or profile-like
        setting, use the set_user_state tool to update user-scoped state such as:
        - user:nickname
        - user:preferred_language
        - user:tone
        - user:response_style
        Do not use set_user_state to modify user:name or user:email because those are
        managed by the authentication/database layer.
        Only use set_user_state for explicit preference/profile updates, not jokes,
        hypotheticals, examples, or temporary roleplay.
        Stay grounded in the user's request and do not make up user details.
    """,
    tools=[set_user_state],

    # Callbacks print helpful logs before/after agent/model/tool events.
    before_agent_callback=log_before_agent,
    after_agent_callback=log_after_agent,
    before_tool_callback=log_before_tool,
    after_tool_callback=log_after_tool,
    before_model_callback=log_before_model,
    after_model_callback=log_after_model,
)
