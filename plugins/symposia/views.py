"""
Chronopoli Symposia – Django Views

Handles Round Table listing, detail, scheduling, and output approval.
"""

import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_GET, require_POST

from .models import RoundTable, Invitation, RoundTableOutput, PipelineRun

logger = logging.getLogger(__name__)


# ============================================================
# PUBLIC / AUTHENTICATED VIEWS
# ============================================================

@login_required
def roundtable_list(request):
    """
    List all Round Tables visible to the authenticated user.
    Shows upcoming, live, and completed sessions.
    """
    roundtables = RoundTable.objects.exclude(status="draft").select_related("initiator")

    status_filter = request.GET.get("status")
    if status_filter:
        roundtables = roundtables.filter(status=status_filter)

    district_filter = request.GET.get("district")
    if district_filter:
        roundtables = roundtables.filter(district_codes__contains=district_filter)

    return render(request, "chronopoli/symposia/list.html", {
        "roundtables": roundtables,
        "status_filter": status_filter or "",
        "district_filter": district_filter or "",
    })


@login_required
def roundtable_detail(request, slug):
    """
    Detail view for a single Round Table showing invitations, agenda,
    IVS playback (if live/recorded), and generated outputs.
    """
    rt = get_object_or_404(
        RoundTable.objects.select_related("initiator"),
        slug=slug,
    )
    invitations = rt.invitations.select_related("invitee_user").all()
    outputs = rt.outputs.select_related("approved_by").all()
    pipeline_runs = rt.pipeline_runs.all()[:5]

    return render(request, "chronopoli/symposia/detail.html", {
        "rt": rt,
        "invitations": invitations,
        "outputs": outputs,
        "pipeline_runs": pipeline_runs,
        "is_initiator": request.user == rt.initiator,
    })


# ============================================================
# STAFF VIEWS
# ============================================================

@staff_member_required
def roundtable_schedule(request):
    """
    Create and schedule a new Round Table session.
    POST only — renders back to the list on success.
    """
    if request.method != "POST":
        return redirect("chronopoli_symposia:list")

    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)

    description = request.POST.get("description", "").strip()
    agenda = request.POST.get("agenda", "").strip()
    district_codes_raw = request.POST.get("district_codes", "")
    scheduled_at = request.POST.get("scheduled_at")
    duration_mins = int(request.POST.get("duration_mins", 90))

    # Parse district codes from comma-separated string
    district_codes = [
        code.strip()
        for code in district_codes_raw.split(",")
        if code.strip()
    ]

    slug = slugify(title)
    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while RoundTable.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    rt = RoundTable.objects.create(
        title=title,
        slug=slug,
        initiator=request.user,
        district_codes=district_codes,
        description=description,
        agenda=agenda,
        status="open",
        scheduled_at=scheduled_at if scheduled_at else None,
        duration_mins=duration_mins,
    )

    logger.info("Round Table created: %s (slug=%s) by %s", rt.title, rt.slug, request.user.username)
    return redirect("chronopoli_symposia:detail", slug=rt.slug)


@staff_member_required
def approval_view(request):
    """
    Staff dashboard showing all outputs awaiting approval.
    """
    pending_outputs = (
        RoundTableOutput.objects
        .filter(status="generated")
        .select_related("round_table")
        .order_by("-generated_at")
    )

    return render(request, "chronopoli/symposia/approve.html", {
        "pending_outputs": pending_outputs,
    })


# ============================================================
# API ENDPOINTS
# ============================================================

@require_POST
@staff_member_required
def api_approve_output(request, output_id):
    """
    Approve or reject a specific Round Table output.
    POST body: {"action": "approve"} or {"action": "reject"}
    """
    output = get_object_or_404(RoundTableOutput, pk=output_id)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    action = body.get("action")
    if action not in ("approve", "reject"):
        return JsonResponse({"error": "action must be 'approve' or 'reject'"}, status=400)

    now = timezone.now()

    if action == "approve":
        output.status = "approved"
        output.approved_by = request.user
        output.approved_at = now
        output.save()
        logger.info("Output %s approved by %s", output.pk, request.user.username)
    else:
        output.status = "rejected"
        output.save()
        logger.info("Output %s rejected by %s", output.pk, request.user.username)

    return JsonResponse({
        "id": output.pk,
        "status": output.status,
        "output_type": output.output_type,
        "round_table": output.round_table.title,
    })


@require_GET
@login_required
def api_roundtable_status(request, slug):
    """
    Return the current status of a Round Table as JSON.
    Useful for front-end polling during live sessions.
    """
    rt = get_object_or_404(RoundTable, slug=slug)

    invitations_data = [
        {
            "name": inv.invitee_name,
            "org": inv.invitee_org,
            "role": inv.role,
            "status": inv.status,
        }
        for inv in rt.invitations.all()
    ]

    outputs_data = [
        {
            "id": out.pk,
            "type": out.output_type,
            "status": out.status,
            "preview": out.content_preview[:200] if out.content_preview else "",
        }
        for out in rt.outputs.all()
    ]

    return JsonResponse({
        "title": rt.title,
        "slug": rt.slug,
        "status": rt.status,
        "scheduled_at": rt.scheduled_at.isoformat() if rt.scheduled_at else None,
        "duration_mins": rt.duration_mins,
        "district_codes": rt.district_codes,
        "ivs_playback_url": rt.ivs_playback_url if rt.status in ("live", "recording") else "",
        "invitations": invitations_data,
        "outputs": outputs_data,
    })
