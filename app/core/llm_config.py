"""
File: app/core/llm_config.py
Purpose: Centralized model definitions for the agent system.

What this file does:
- Defines named LLM configurations in one place
- Sets up fallback chains for some models
- Exposes a helper for choosing the default model
"""

from google.adk.models.lite_llm import LiteLlm

# Native Gemini model identifiers used directly by ADK.
gemini_2_5_flash = "gemini-2.5-flash"
gemini_2_5_pro = "gemini-2.5-pro"


# LiteLLM-wrapped models. These can route through different providers and
# optionally fall back to alternatives if the primary model fails.

gpt_5_4_pro = LiteLlm(
    model="openai/gpt-5.4-pro",
    fallbacks=[
        "claude/claude-sonnet-4-6",
        "openai/gpt-4o",
        "gemini/gemini-2.5-flash",
    ],
)

gpt_4_1 = LiteLlm(
    model="openai/gpt-4.1",
    fallbacks=[
        "openai/gpt-4o-mini",
        "gemini/gemini-2.5-flash",
    ],
)

gpt_5 = LiteLlm(model="openai/gpt-5")
gpt_5_pro = LiteLlm(model="openai/gpt-5-pro")
gpt_5_1 = LiteLlm(model="openai/gpt-5.1")
gpt_5_2 = LiteLlm(model="openai/gpt-5.2")
gpt_5_3 = LiteLlm(model="openai/gpt-5.3")
gpt_5_4 = LiteLlm(model="openai/gpt-5.4")

gpt_4o = LiteLlm(model="openai/gpt-4o")

claude_opus_4_6 = LiteLlm(model="claude/claude-opus-4-6")
claude_sonnet_4_6 = LiteLlm(model="claude/claude-sonnet-4-6")

grok_3 = LiteLlm(model="grok/grok-3")
grok_4_20_multi_agent = LiteLlm(model="grok/grok-4.20-multi-agent-beta-0309")


def get_default_model():
    # Single place to define the preferred default model for agents.
    return gpt_5_4_pro


def handle_llm_exception(e: Exception):
    # Small helper for debugging/provider-failure fallback behavior.
    print(f"DEBUG: All models failed. Error: {e}")
    return "I'm sorry, our AI providers are currently at capacity. Please try again in a moment."
