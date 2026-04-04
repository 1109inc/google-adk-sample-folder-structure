"""
File: app/agents/callbacks.py
Purpose: Logging callbacks for agent/model/tool lifecycle events.

What this file does:
- Prints useful debug output before and after agent execution
- Logs prompts, responses, and tool calls
- Helps you understand what the ADK system is doing internally
"""

import logging
import json
from typing import Dict, Any
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

# Keep console logging simple and readable during development.
logging.basicConfig(level=logging.INFO, format='%(message)s')


def log_before_agent(callback_context: CallbackContext) -> types.Content | None:
    agent_name = callback_context.agent_name
    inv_id = callback_context.invocation_id
    user_query = callback_context.user_content
    
    # Safely convert state to dict for pretty printing/logging.
    state_data = callback_context.state.to_dict() if hasattr(callback_context.state, 'to_dict') else str(callback_context.state)

    print(f"\n{'='*20} AGENT ENTER: {agent_name} {'='*20}")
    print(f"ID: {inv_id}")
    print(f"Query: {user_query}")
    print(f"State: {state_data}")


def log_after_agent(callback_context: CallbackContext) -> types.Content | None:
    # Called after the agent finishes handling the request.
    print(f"{'='*20} AGENT EXIT: {callback_context.agent_name} {'='*20}\n")


def log_before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    agent_name = callback_context.agent_name
    
    # Extract the latest text chunk so the logs show what is being sent to the model.
    last_msg = "No text found"
    if llm_request.contents:
        last_part = llm_request.contents[-1].parts[0]
        last_msg = last_part.text if hasattr(last_part, 'text') else "[Non-text Part]"

    print(f"  [Model Request] Agent '{agent_name}' calling LLM...")
    print(f"  [Prompt Snippet]: {last_msg}...")


def log_after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    print(f"  [Model Response] Agent: {callback_context.agent_name}")
    
    if llm_response.content and llm_response.content.parts:
        part = llm_response.content.parts[0]
        
        # Distinguish between plain text output and a tool/function call.
        if hasattr(part, 'text') and part.text:
            print(f"    -> Text: {part.text}...")
        elif hasattr(part, 'function_call') and part.function_call:
            print(f"    -> Tool Call: {part.function_call.name}({part.function_call.args})")
    
    if llm_response.error_message:
        print(f"    -> ERROR: {llm_response.error_message}")
    return None


def log_before_tool(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Dict | None:
    # Log the tool name and arguments before execution.
    print(f"    [Tool Call] Executing: {tool.name}")
    print(f"    [Tool Args]: {args}")
    return None


def log_after_tool(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Dict | None:
    # Safely handle potential non-dict responses before printing.
    resp_str = tool_response if isinstance(tool_response, dict) else str(tool_response)
    print(f"    [Tool Result] {tool.name} returned:")
    print(f"    {resp_str}")
