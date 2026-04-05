"""
File: app/tools/state_tools.py
Purpose: Simple ADK tools for controlled session/user state updates.

What this file does:
- Exposes a `set_user_state` tool the agent can call
- Lets the agent update user-scoped preference keys
- Blocks writes to auth-owned identity fields
- Updates ADK-managed state through ToolContext so changes persist correctly
"""

from google.adk.tools import ToolContext


# These identity fields should remain owned by the auth/database layer.
PROTECTED_STATE_KEYS = {
    "user:name",
    "user:email",
}


def set_user_state(key: str, value: str, tool_context: ToolContext) -> dict[str, str]:
    """Set an allowed state key to a new string value.

    Use this tool for user-scoped preferences such as nickname, language,
    response style, tone, or other conversational settings.
    """
    if not key.startswith("user:"):
        return {
            "status": "error",
            "message": "Only user-scoped keys with the 'user:' prefix are allowed.",
        }

    if key in PROTECTED_STATE_KEYS:
        return {
            "status": "error",
            "message": f"Key '{key}' is managed by auth/database and cannot be changed with this tool.",
        }

    tool_context.state[key] = value
    return {
        "status": "success",
        "message": f"State updated: {key} = {value}",
    }
