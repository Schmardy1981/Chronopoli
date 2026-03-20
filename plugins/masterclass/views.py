"""
Chronopoli Digital Twin / Master Class — Views
"""

import json
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import DigitalTwin, GeneratedQuestion, MasterclassSession, TwinDocument, TwinVideo

logger = logging.getLogger(__name__)


@login_required
def twin_list(request):
    """List all published digital twins."""
    twins = DigitalTwin.objects.filter(is_published=True).select_related("expert")
    return render(request, "chronopoli/masterclass/list.html", {"twins": twins})


@login_required
def twin_detail(request, pk):
    """Show a digital twin profile with videos, questions, and sessions."""
    twin = get_object_or_404(DigitalTwin, pk=pk)
    documents = twin.documents.all()
    questions = twin.questions.filter(is_approved=True).order_by("category", "order")
    videos = twin.videos.filter(status="ready")
    sessions = twin.sessions.order_by("-scheduled_at")[:5]

    return render(request, "chronopoli/masterclass/detail.html", {
        "twin": twin,
        "documents": documents,
        "questions": questions,
        "videos": videos,
        "sessions": sessions,
    })


@staff_member_required
def twin_create(request):
    """Create a new digital twin (staff only)."""
    if request.method == "POST":
        twin = DigitalTwin.objects.create(
            expert=request.user,
            name=request.POST.get("name", ""),
            title=request.POST.get("title", ""),
            district_code=request.POST.get("district_code", "CHRON-DA"),
            bio=request.POST.get("bio", ""),
        )
        return redirect("chronopoli_masterclass:detail", pk=twin.pk)

    return render(request, "chronopoli/masterclass/create.html")


@staff_member_required
@require_POST
def twin_upload_document(request, pk):
    """Upload a document for processing by Textract + Claude."""
    twin = get_object_or_404(DigitalTwin, pk=pk)
    title = request.POST.get("title", "Untitled Document")
    doc_type = request.POST.get("doc_type", "other")

    # In production: upload to S3 and trigger Celery task
    # For now: create the record with placeholder
    doc = TwinDocument.objects.create(
        twin=twin,
        title=title,
        doc_type=doc_type,
        s3_key=f"masterclass-docs/{twin.pk}/{title.replace(' ', '_')}.pdf",
    )

    # Trigger async processing
    try:
        from .tasks import process_document
        process_document.delay(doc.pk)
    except Exception as e:
        logger.warning("Could not enqueue document processing: %s", e)

    return redirect("chronopoli_masterclass:detail", pk=twin.pk)


@staff_member_required
@require_POST
def twin_generate_questions(request, pk):
    """Trigger AI question generation for a twin."""
    twin = get_object_or_404(DigitalTwin, pk=pk)

    try:
        from .tasks import generate_questions
        generate_questions.delay(twin.pk)
    except Exception as e:
        logger.warning("Could not enqueue question generation: %s", e)

    return redirect("chronopoli_masterclass:detail", pk=twin.pk)


@login_required
def session_detail(request, pk):
    """Show a masterclass session (live or recorded)."""
    session = get_object_or_404(MasterclassSession, pk=pk)
    return render(request, "chronopoli/masterclass/session.html", {
        "session": session,
        "twin": session.twin,
    })


@require_GET
def api_twin_detail(request, pk):
    """JSON detail for a digital twin."""
    twin = get_object_or_404(DigitalTwin, pk=pk, is_published=True)
    return JsonResponse({
        "id": twin.pk,
        "name": twin.name,
        "title": twin.title,
        "district_code": twin.district_code,
        "bio": twin.bio,
        "expertise_summary": twin.expertise_summary,
        "videos_count": twin.videos.filter(status="ready").count(),
        "sessions_count": twin.sessions.count(),
    })
