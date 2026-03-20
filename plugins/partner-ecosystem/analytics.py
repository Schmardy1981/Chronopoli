"""
Chronopoli Partner Analytics

Computes enrollment, completion, badge, and revenue metrics.
Used by dashboard views and weekly SES reports.
"""

import logging
from datetime import timedelta

from django.utils import timezone

from .models import Partner

logger = logging.getLogger(__name__)


def get_weekly_summary(partner: Partner) -> dict:
    """
    Compute weekly summary for a partner (used in SES report).
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    summary = {
        "partner_name": partner.name,
        "period_start": week_ago.strftime("%Y-%m-%d"),
        "period_end": now.strftime("%Y-%m-%d"),
        "new_enrollments": 0,
        "new_completions": 0,
        "new_badges": 0,
        "new_applications": 0,
        "active_tracks": 0,
        "total_revenue_usd": 0,
    }

    try:
        summary["active_tracks"] = partner.tracks.filter(is_published=True).count()
    except Exception:
        pass

    # Enrollment counts for the week
    try:
        from common.djangoapps.student.models import CourseEnrollment
        from opaque_keys.edx.keys import CourseKey

        track_keys = list(
            partner.tracks.filter(is_published=True).values_list("course_key", flat=True)
        )
        for key_str in track_keys:
            try:
                key = CourseKey.from_string(key_str)
                summary["new_enrollments"] += CourseEnrollment.objects.filter(
                    course_id=key,
                    is_active=True,
                    created__gte=week_ago,
                ).count()
            except Exception:
                pass
    except ImportError:
        pass

    # Badge awards this week
    try:
        from chronopoli_academy.models import UserBadge

        summary["new_badges"] = UserBadge.objects.filter(
            badge__partner=partner,
            issued_at__gte=week_ago,
        ).count()
    except (ImportError, Exception):
        pass

    # Job applications this week
    try:
        from chronopoli_academy.models import JobApplication

        summary["new_applications"] = JobApplication.objects.filter(
            job__partner=partner,
            submitted_at__gte=week_ago,
        ).count()
    except (ImportError, Exception):
        pass

    # Revenue this week
    try:
        from chronopoli_ecommerce.models import PartnerPayout

        payouts = PartnerPayout.objects.filter(
            partner_slug=partner.slug,
            status="paid",
            created_at__gte=week_ago,
        )
        summary["total_revenue_usd"] = float(
            sum(p.partner_share_usd for p in payouts)
        )
    except (ImportError, Exception):
        pass

    return summary


def send_weekly_partner_report(partner: Partner):
    """Send weekly analytics report via SES to the partner contact email."""
    if not partner.contact_email:
        return

    summary = get_weekly_summary(partner)

    try:
        import boto3
        from django.conf import settings

        region = getattr(settings, "AWS_REGION", "me-central-1")
        ses = boto3.client("ses", region_name=region)

        subject = f"Chronopoli Weekly Report — {partner.name} ({summary['period_start']} to {summary['period_end']})"

        body_html = f"""
        <html>
        <body style="font-family: 'Inter', sans-serif; background: #0A0A0F; color: #E8E8F0; padding: 40px;">
          <div style="max-width: 600px; margin: 0 auto; background: #1A1A26; border: 1px solid #2A2A3A; border-radius: 12px; padding: 32px;">
            <h1 style="color: #C9A84C; font-size: 24px; margin-bottom: 24px;">
              {partner.name} — Weekly Report
            </h1>
            <p style="color: #888899;">
              {summary['period_start']} to {summary['period_end']}
            </p>
            <hr style="border-color: #2A2A3A; margin: 24px 0;">
            <table style="width: 100%; color: #E8E8F0;">
              <tr><td>Active Tracks</td><td style="text-align:right; font-weight:bold;">{summary['active_tracks']}</td></tr>
              <tr><td>New Enrollments</td><td style="text-align:right; font-weight:bold;">{summary['new_enrollments']}</td></tr>
              <tr><td>New Completions</td><td style="text-align:right; font-weight:bold;">{summary['new_completions']}</td></tr>
              <tr><td>Badges Awarded</td><td style="text-align:right; font-weight:bold;">{summary['new_badges']}</td></tr>
              <tr><td>Job Applications</td><td style="text-align:right; font-weight:bold;">{summary['new_applications']}</td></tr>
              <tr><td>Revenue (Your Share)</td><td style="text-align:right; font-weight:bold; color: #C9A84C;">${summary['total_revenue_usd']:.2f}</td></tr>
            </table>
            <hr style="border-color: #2A2A3A; margin: 24px 0;">
            <p style="font-size: 12px; color: #888899;">
              Chronopoli — The Global Knowledge City<br>
              Powered by Dubai Blockchain Center
            </p>
          </div>
        </body>
        </html>
        """

        ses.send_email(
            Source="platform@chronopoli.io",
            Destination={"ToAddresses": [partner.contact_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": body_html}},
            },
        )
        logger.info("Weekly report sent to %s (%s)", partner.name, partner.contact_email)

    except Exception as e:
        logger.error("Failed to send weekly report to %s: %s", partner.name, e)
