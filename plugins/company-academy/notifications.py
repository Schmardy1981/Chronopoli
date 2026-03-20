"""
Chronopoli Company Academy – Notifications

Sends email notifications via AWS SES when talent pipeline events occur.
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def notify_partner_hr(user, job, application):
    """
    Send an SES email to the partner's HR contact notifying them of a
    new auto-submitted application.

    Args:
        user: Django User instance (the applicant).
        job: PartnerJobPosting instance.
        application: JobApplication instance.
    """
    partner = job.partner

    # Prefer dedicated HR email, fall back to general contact
    recipient = getattr(partner, "hr_notification_email", "") or partner.contact_email
    if not recipient:
        logger.warning(
            "No contact email for partner '%s'; cannot send HR notification.",
            partner.name,
        )
        return

    aws_region = getattr(settings, "AWS_REGION", "eu-west-1")
    sender = getattr(
        settings,
        "CHRONOPOLI_NOTIFICATION_SENDER",
        "noreply@chronopoli.io",
    )

    subject = (
        f"[Chronopoli] New Application: {user.get_full_name() or user.username} "
        f"for {job.title}"
    )

    badge_names = []
    snapshot = application.credential_snapshot or {}
    badge_ids = snapshot.get("badge_ids", [])
    if badge_ids:
        from chronopoli_academy.models import Badge
        badge_names = list(
            Badge.objects.filter(pk__in=badge_ids).values_list("name", flat=True)
        )

    body_text = (
        f"Hello {partner.name} Team,\n\n"
        f"A new candidate has been auto-matched to your job posting on Chronopoli.\n\n"
        f"Position: {job.title}\n"
        f"Location: {job.location}\n\n"
        f"Candidate: {user.get_full_name() or user.username}\n"
        f"Email: {user.email}\n"
        f"Badges earned: {', '.join(badge_names) if badge_names else 'None'}\n"
        f"Pathway completed: {snapshot.get('pathway_title', 'N/A')}\n"
        f"District: {snapshot.get('district_code', 'N/A')}\n\n"
        f"Review this application in the Chronopoli admin panel.\n\n"
        f"Best regards,\nChronopoli Platform"
    )

    try:
        import boto3

        client = boto3.client("ses", region_name=aws_region)
        client.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                },
            },
        )
        logger.info(
            "HR notification sent to %s for job '%s'.",
            recipient,
            job.title,
        )
    except ImportError:
        logger.warning("boto3 not installed; HR notification not sent.")
    except Exception:
        logger.exception(
            "SES error sending HR notification to %s for job '%s'.",
            recipient,
            job.title,
        )
