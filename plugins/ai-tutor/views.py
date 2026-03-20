"""
Chronopoli AI Tutor — Views

SSE streaming endpoint for real-time AI chat responses.
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_POST

from .bedrock_client import generate_streaming_response, retrieve_context
from .models import TutorMessage, TutorSession
from .prompts import build_system_prompt

logger = logging.getLogger(__name__)


@login_required
@require_POST
def tutor_chat(request):
    """
    Streaming SSE endpoint for AI Tutor queries.
    Returns Server-Sent Events for real-time response streaming.
    """
    data = json.loads(request.body)
    question = data.get("question", "").strip()
    session_id = data.get("session_id")
    course_key = data.get("course_key", "")

    if not question:
        return JsonResponse({"error": "Question is required"}, status=400)

    # Get or create session
    if session_id:
        try:
            session = TutorSession.objects.get(id=session_id, user=request.user)
        except TutorSession.DoesNotExist:
            session = _create_session(request.user, course_key)
    else:
        session = _create_session(request.user, course_key)

    # Save user message
    TutorMessage.objects.create(session=session, role="user", content=question)

    # Get user profile for personalization
    district_code, layer, user_type = _get_user_context(request.user)

    # Build system prompt
    system_prompt = build_system_prompt(
        district_code=district_code,
        layer=layer,
        user_type=user_type,
        course_key=course_key or session.course_key,
    )

    # Retrieve context from Knowledge Base
    context_chunks = retrieve_context(question)

    # Build conversation history (last 10 messages)
    history = TutorMessage.objects.filter(session=session).order_by("-created_at")[:10]
    messages = [
        {"role": m.role, "content": m.content} for m in reversed(history)
    ]

    # Extract source citations for saving
    sources = [
        {"uri": c["uri"], "score": c["score"]}
        for c in context_chunks
        if c.get("uri")
    ]

    def sse_stream():
        """Generator for Server-Sent Events."""
        full_response = ""

        # Send session ID first
        yield f"data: {json.dumps({'type': 'session', 'session_id': session.id})}\n\n"

        # Stream response chunks
        for chunk in generate_streaming_response(messages, system_prompt, context_chunks):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

        # Save assistant message
        TutorMessage.objects.create(
            session=session,
            role="assistant",
            content=full_response,
            sources=sources,
        )

        # Send done signal
        yield f"data: {json.dumps({'type': 'done', 'sources': sources})}\n\n"

    response = StreamingHttpResponse(sse_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@login_required
@require_GET
def tutor_history(request):
    """Return conversation history for a session."""
    session_id = request.GET.get("session_id")
    if not session_id:
        # Return list of user's sessions
        sessions = TutorSession.objects.filter(user=request.user)[:20]
        return JsonResponse({
            "sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "district_code": s.district_code,
                    "last_activity": s.last_activity.isoformat(),
                }
                for s in sessions
            ]
        })

    try:
        session = TutorSession.objects.get(id=session_id, user=request.user)
    except TutorSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    messages = TutorMessage.objects.filter(session=session).order_by("created_at")
    return JsonResponse({
        "session_id": session.id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    })


def _create_session(user, course_key=""):
    """Create a new tutor session with user context."""
    district_code, _, _ = _get_user_context(user)
    return TutorSession.objects.create(
        user=user,
        district_code=district_code,
        course_key=course_key,
    )


def _get_user_context(user):
    """Get district, layer, and user type from onboarding profile."""
    try:
        from chronopoli_onboarding.models import OnboardingProfile

        profile = OnboardingProfile.objects.get(user=user)
        return (
            profile.primary_district or "CHRON-DA",
            profile.recommended_layer or "entry",
            profile.user_type or "student",
        )
    except Exception:
        return "CHRON-DA", "entry", "student"
