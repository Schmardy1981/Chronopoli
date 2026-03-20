"""
Chronopoli Company Academy – Talent Pipeline

Automatically matches learners to partner job postings based on earned
badges and district credentials, and can auto-submit applications.
"""
import logging

from django.utils import timezone

from chronopoli_academy.models import (
    JobApplication,
    PartnerJobPosting,
    UserBadge,
)

logger = logging.getLogger(__name__)


def get_user_badges(user):
    """
    Return the set of Badge IDs earned by the user.

    Args:
        user: Django User instance.

    Returns:
        set[int]: Badge primary keys.
    """
    return set(
        UserBadge.objects.filter(user=user).values_list("badge_id", flat=True)
    )


def match_jobs(user_badge_ids):
    """
    Find active job postings where the user holds all required badges.

    Args:
        user_badge_ids: set of Badge PKs the user has earned.

    Returns:
        QuerySet of matching PartnerJobPosting instances.
    """
    now = timezone.now()
    active_jobs = PartnerJobPosting.objects.filter(
        is_active=True,
    ).filter(
        # Not expired
        models_Q_expires_null_or_future(now)
    ).prefetch_related("required_badges")

    matched = []
    for job in active_jobs:
        required = set(job.required_badges.values_list("pk", flat=True))
        # Jobs with no required badges match anyone; otherwise check subset
        if not required or required <= user_badge_ids:
            matched.append(job.pk)

    return PartnerJobPosting.objects.filter(pk__in=matched)


def models_Q_expires_null_or_future(now):
    """
    Build a Q filter for jobs that are not expired.
    """
    from django.db.models import Q
    return Q(expires_at__isnull=True) | Q(expires_at__gt=now)


def check_and_apply(user, pathway):
    """
    After a user completes a pathway, find matching job postings from the
    pathway's partner and auto-submit applications.

    Args:
        user: Django User instance.
        pathway: LearningPathway instance that was just completed.
    """
    user_badge_ids = get_user_badges(user)
    if not user_badge_ids:
        return

    # Find matching jobs from the pathway's partner
    now = timezone.now()
    partner_jobs = PartnerJobPosting.objects.filter(
        partner=pathway.partner,
        is_active=True,
    ).filter(
        models_Q_expires_null_or_future(now)
    ).prefetch_related("required_badges")

    for job in partner_jobs:
        required = set(job.required_badges.values_list("pk", flat=True))
        if required and not (required <= user_badge_ids):
            continue

        # Check district match
        if job.required_district and job.required_district != pathway.district_code:
            continue

        # Avoid duplicate applications
        if JobApplication.objects.filter(job=job, user=user).exists():
            logger.debug(
                "User %s already applied to job '%s'; skipping.",
                user.username,
                job.title,
            )
            continue

        # Build credential snapshot
        snapshot = {
            "badge_ids": list(user_badge_ids),
            "pathway_title": pathway.title,
            "pathway_id": pathway.pk,
            "district_code": pathway.district_code,
        }

        application = JobApplication.objects.create(
            job=job,
            user=user,
            auto_submitted=True,
            credential_snapshot=snapshot,
        )
        logger.info(
            "Auto-submitted application for user %s to job '%s' (app %s).",
            user.username,
            job.title,
            application.pk,
        )

        # Notify partner HR
        try:
            from chronopoli_academy.notifications import notify_partner_hr
            notify_partner_hr(user, job, application)
        except Exception:
            logger.exception(
                "Failed to notify partner HR for job '%s'.", job.title
            )
