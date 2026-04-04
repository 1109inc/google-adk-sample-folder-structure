"""
File: app/api/v1/endpoints/chat.py
Purpose: Authenticated chat endpoint for the agent system.

What this file does:
- Requires a logged-in user
- Builds personalized context from that user
- Reuses or creates an AI session
- Sends the message to the ADK runner
- Returns the final model reply plus some metadata
"""

import asyncio
from typing import Optional
import time
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

from app.api.deps import get_current_user

from app.services.adk_service import runner, session_service
from app.core.config import settings
from app.models.user import User
router = APIRouter()


def build_user_context_message(user: User) -> str:
    # Convert selected user fields into a short text block that the agent
    # can use for light personalization.
    context_lines = ["Authenticated user details:"]

    if user.full_name:
        context_lines.append(f"- Name: {user.full_name}")
    if user.email:
        context_lines.append(f"- Email: {user.email}")

    context_lines.append("")
    context_lines.append(
        "Use these details only when they help personalize the response."
    )

    return "\n".join(context_lines)


@router.get("/")
async def chat(
    message: str = Query(...),
    session_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    # Use the authenticated user's DB id as the chat user id so sessions
    # belong to the real logged-in user.
    user_id = str(current_user.id)

    # Build the final user message that will be sent to the agent.
    user_context = build_user_context_message(current_user)
    personalized_message = f"{user_context}\n\nUser message:\n{message}"

    active_session_id = session_id

    # If the client provided a session id, try to reuse it for continuity.
    # If that session is missing/invalid, silently start a new one instead.
    if active_session_id:
        try:
            await session_service.get_session(
                app_name=settings.APP_NAME,
                user_id=user_id,
                session_id=active_session_id,
            )
        except Exception:
            active_session_id = None

    if not active_session_id:
        # Create a brand-new chat session for this user.
        new_session = await session_service.create_session(
            user_id=user_id,
            app_name=settings.APP_NAME,
        )
        active_session_id = new_session.id

    content = types.Content(
        role="user",
        parts=[types.Part(text=personalized_message)],
    )

    # Track duration and usage metadata for the response payload.
    start_time = time.perf_counter()
    final_text = ""
    usage_metadata = None

    # Run the message through the ADK runner and wait for the final response.
    async for event in runner.run_async(
        user_id=user_id,
        session_id=active_session_id,
        new_message=content,
    ):
        # Only keep the final response event so the endpoint returns one
        # completed answer rather than a stream of partial chunks.
        if getattr(event, "is_final_response", None) and event.is_final_response():
            if event.content and event.content.parts:
                parts_text = [part.text for part in event.content.parts if part.text]
                if parts_text:
                    final_text = "".join(parts_text)
            usage_metadata = getattr(event, "usage_metadata", None)

    # Guard against a blank final response.
    if not final_text:
        final_text = "Task completed, but no text response was generated."

    duration = time.perf_counter() - start_time

    # Return the model reply plus useful metadata for the client.
    return {
        "reply": final_text,
        "session_id": active_session_id,
        "total_tokens": usage_metadata.total_token_count if usage_metadata else 0,
        "time_taken_sec": round(duration, 3),
    }


# The SSE streaming version below is kept commented out as an alternate
# implementation for future real-time streaming responses.
# async def sse_stream_generator(user_query: str, session_id: str, user_id: str):
#     content = types.Content(
#         role="user",
#         parts=[types.Part(text=user_query)],
#     )

#     run_config = RunConfig(streaming_mode=StreamingMode.SSE)

#     try:
#         buffered_chunk = None

#         async for event in runner.run_async(
#             user_id=user_id,
#             session_id=session_id,
#             new_message=content,
#             run_config=run_config,
#         ):
#             if event.content and event.content.parts:
#                 for part in event.content.parts:
#                     if part.text:
#                         if buffered_chunk is not None:
#                             # for char in buffered_chunk:
#                                 # safe_char = char.replace("\n", "<br>")
#                                 yield f"data: {buffered_chunk}\n\n"
#                                 # await asyncio.sleep(0.01)

#                         buffered_chunk = part.text

#         yield "data: [DONE]\n\n"

#     except Exception as e:
#         yield f"data: ERROR: {str(e)}\n\n"


# @router.get("/")
# async def chat(
#     message: str = Query(...),
#     current_user: User = Depends(get_current_user),
# ):
#     # Use the authenticated user's database ID so each user gets their own
#     # chat session ownership instead of sharing a hardcoded placeholder ID.
#     user_id = str(current_user.id)

#     # Inject a small profile block into each request so the assistant can
#     # personalize replies for the logged-in user.
#     user_context = build_user_context_message(
#         user_name=current_user.full_name,
#         user_email=current_user.email,
#     )
#     personalized_message = f"{user_context}\n\nUser message:\n{message}"

#     # Create a fresh ADK session for the currently authenticated user.
#     new_session = await session_service.create_session(
#         user_id=user_id,
#         app_name=settings.APP_NAME,
#     )
#     active_session_id = new_session.id

#     return StreamingResponse(
#         sse_stream_generator(personalized_message, active_session_id, user_id),
#         media_type="text/event-stream",
#     )
