"""
Chronopoli Company Academy – Views

Renders partner-branded academy pages and provides JSON API endpoints
for badge and pathway progress data.
"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from chronopoli_academy.models import (
    Badge,
    LearningPathway,
    PartnerJobPosting,
    PathwayStep,
    UserBadge,
)

logger = logging.getLogger(__name__)


def academy_home(request):
    """
    Partner academy homepage. If accessed via partner subdomain, shows only
    that partner's pathways and jobs. Otherwise shows all published pathways.
    """
    partner = getattr(request, "partner", None)

    if partner:
        pathways = LearningPathway.objects.filter(
            partner=partner, is_published=True
        ).select_related("partner")
        jobs = PartnerJobPosting.objects.filter(
            partner=partner, is_active=True
        )
    else:
        pathways = LearningPathway.objects.filter(
            is_published=True
        ).select_related("partner")
        jobs = PartnerJobPosting.objects.filter(is_active=True)

    return render(request, "chronopoli/academy/home.html", {
        "partner": partner,
        "pathways": pathways,
        "jobs": jobs[:10],
    })


def pathway_detail(request, slug):
    """
    Shows a single pathway with its steps and user progress.
    """
    partner = getattr(request, "partner", None)
    filters = {"slug": slug, "is_published": True}
    if partner:
        filters["partner"] = partner

    pathway = get_object_or_404(LearningPathway, **filters)
    steps = pathway.steps.all()

    # Compute user progress
    completed_courses = set()
    if request.user.is_authenticated:
        # Attempt to check completions via OpenEdX enrollments API
        try:
            from lms.djangoapps.courseware.courses import get_course_by_id
            from opaque_keys.edx.keys import CourseKey
            from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

            for step in steps:
                try:
                    course_key = CourseKey.from_string(step.course_key)
                    grade = CourseGradeFactory().read(request.user, course_key=course_key)
                    if grade and grade.passed:
                        completed_courses.add(step.course_key)
                except Exception:
                    pass
        except ImportError:
            logger.debug("OpenEdX grade API not available; skipping progress check.")

    total_required = steps.filter(is_required=True).count()
    completed_required = sum(
        1 for s in steps.filter(is_required=True)
        if s.course_key in completed_courses
    )
    progress_pct = int((completed_required / total_required * 100)) if total_required else 0

    badges = pathway.badges.all()

    return render(request, "chronopoli/academy/pathway.html", {
        "partner": partner,
        "pathway": pathway,
        "steps": steps,
        "completed_courses": completed_courses,
        "progress_pct": progress_pct,
        "badges": badges,
    })


def badge_detail(request, slug):
    """
    Shows badge info, criteria, and whether the current user has earned it.
    """
    badge = get_object_or_404(Badge, slug=slug)
    user_has_badge = False
    if request.user.is_authenticated:
        user_has_badge = UserBadge.objects.filter(
            user=request.user, badge=badge
        ).exists()

    return render(request, "chronopoli/academy/badge.html", {
        "badge": badge,
        "user_has_badge": user_has_badge,
    })


def job_list(request):
    """
    Lists open job postings. Filtered by partner if on academy subdomain.
    """
    partner = getattr(request, "partner", None)
    if partner:
        jobs = PartnerJobPosting.objects.filter(partner=partner, is_active=True)
    else:
        jobs = PartnerJobPosting.objects.filter(is_active=True)

    return render(request, "chronopoli/academy/jobs.html", {
        "partner": partner,
        "jobs": jobs,
    })


@login_required
def api_user_badges(request):
    """
    JSON API: returns the authenticated user's earned badges.
    """
    awards = UserBadge.objects.filter(user=request.user).select_related("badge")
    data = [
        {
            "badge_name": ub.badge.name,
            "badge_slug": ub.badge.slug,
            "assertion_uid": str(ub.assertion_uid),
            "issued_at": ub.issued_at.isoformat(),
            "evidence_url": ub.evidence_url,
            "image_url": ub.badge.image_url,
        }
        for ub in awards
    ]
    return JsonResponse({"badges": data})


@login_required
def api_pathway_progress(request, pathway_id):
    """
    JSON API: returns progress for a specific pathway.
    """
    pathway = get_object_or_404(LearningPathway, pk=pathway_id)
    steps = pathway.steps.all()

    completed_courses = set()
    try:
        from opaque_keys.edx.keys import CourseKey
        from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

        for step in steps:
            try:
                course_key = CourseKey.from_string(step.course_key)
                grade = CourseGradeFactory().read(request.user, course_key=course_key)
                if grade and grade.passed:
                    completed_courses.add(step.course_key)
            except Exception:
                pass
    except ImportError:
        pass

    step_data = [
        {
            "order": s.order,
            "title": s.title,
            "course_key": s.course_key,
            "is_required": s.is_required,
            "completed": s.course_key in completed_courses,
        }
        for s in steps
    ]

    total_required = sum(1 for s in step_data if s["is_required"])
    completed_required = sum(1 for s in step_data if s["is_required"] and s["completed"])

    return JsonResponse({
        "pathway_id": pathway.pk,
        "pathway_title": pathway.title,
        "steps": step_data,
        "total_required": total_required,
        "completed_required": completed_required,
        "progress_pct": int((completed_required / total_required * 100)) if total_required else 0,
    })
