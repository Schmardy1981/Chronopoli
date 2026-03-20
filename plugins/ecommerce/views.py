"""
Chronopoli E-Commerce Views

Handles Stripe checkout flow, webhook processing, and subscription management.
"""

import json
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    CoursePricingTier,
    PartnerPayout,
    Purchase,
    StripeWebhookEvent,
    TeamSubscription,
)
from .stripe_client import create_checkout_session, verify_webhook_signature

logger = logging.getLogger(__name__)


# ============================================================
# CHECKOUT FLOW
# ============================================================

@login_required
def checkout_start(request, course_key):
    """
    Start a Stripe Checkout Session for a course purchase.
    If the course is free, auto-enroll and skip Stripe.
    """
    pricing = get_object_or_404(CoursePricingTier, course_key=course_key)

    # Free courses: enroll directly
    if pricing.is_free:
        _enroll_user(request.user, course_key)
        return redirect(f"/courses/{course_key}/about")

    # Check if already purchased
    existing = Purchase.objects.filter(
        user=request.user, course_key=course_key, status="completed",
    ).first()
    if existing:
        return redirect(f"/courses/{course_key}/courseware")

    # Get partner Connect account if this is a partner course
    partner_connect_id = _get_partner_connect_id(course_key)

    lms_base = getattr(settings, "LMS_ROOT_URL", "https://learn.chronopoli.io")
    session = create_checkout_session(
        course_key=course_key,
        price_id=pricing.stripe_price_id,
        amount_usd=pricing.price_usd,
        user_email=request.user.email,
        success_url=f"{lms_base}/chronopoli/ecommerce/checkout/success/",
        cancel_url=f"{lms_base}/chronopoli/ecommerce/checkout/cancel/",
        partner_connect_account_id=partner_connect_id,
    )

    # Create pending purchase record
    Purchase.objects.update_or_create(
        user=request.user,
        course_key=course_key,
        defaults={
            "pricing_tier": pricing,
            "stripe_checkout_session_id": session["session_id"],
            "amount_usd": pricing.price_usd,
            "status": "pending",
        },
    )

    return redirect(session["url"])


@login_required
def checkout_success(request):
    """User lands here after successful Stripe payment."""
    session_id = request.GET.get("session_id", "")
    if session_id:
        purchase = Purchase.objects.filter(
            stripe_checkout_session_id=session_id,
        ).first()
        if purchase:
            return render(request, "chronopoli/ecommerce/success.html", {
                "purchase": purchase,
                "course_key": purchase.course_key,
            })
    return redirect("/dashboard")


@login_required
def checkout_cancel(request):
    """User cancelled the Stripe checkout."""
    return render(request, "chronopoli/ecommerce/cancel.html")


# ============================================================
# STRIPE WEBHOOK
# ============================================================

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    Verifies signature, processes payment events, enrolls users.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = verify_webhook_signature(payload, sig_header)
    except Exception as e:
        logger.warning("Stripe webhook signature verification failed: %s", e)
        return HttpResponseBadRequest("Invalid signature")

    # Idempotency: skip if already processed
    event_id = event.get("id", "")
    event_type = event.get("type", "")

    webhook_event, created = StripeWebhookEvent.objects.get_or_create(
        stripe_event_id=event_id,
        defaults={"event_type": event_type, "payload": event},
    )

    if not created and webhook_event.processed:
        return HttpResponse("Already processed", status=200)

    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(event["data"]["object"])
        elif event_type == "customer.subscription.updated":
            _handle_subscription_updated(event["data"]["object"])
        elif event_type == "customer.subscription.deleted":
            _handle_subscription_deleted(event["data"]["object"])

        webhook_event.processed = True
        webhook_event.save(update_fields=["processed"])
    except Exception as e:
        logger.exception("Error processing Stripe webhook %s: %s", event_id, e)
        webhook_event.error_message = str(e)
        webhook_event.save(update_fields=["error_message"])
        return HttpResponse("Processing error", status=500)

    return HttpResponse("OK", status=200)


def _handle_checkout_completed(session):
    """Process a completed checkout session — enroll the user."""
    session_id = session.get("id", "")
    purchase = Purchase.objects.filter(
        stripe_checkout_session_id=session_id,
    ).first()

    if not purchase:
        logger.warning("No purchase found for session %s", session_id)
        return

    purchase.stripe_payment_intent_id = session.get("payment_intent", "")
    purchase.status = "completed"
    purchase.completed_at = timezone.now()
    purchase.save(update_fields=[
        "stripe_payment_intent_id", "status", "completed_at",
    ])

    # Enroll user in OpenEdX course
    _enroll_user(purchase.user, purchase.course_key)
    purchase.enrolled = True
    purchase.save(update_fields=["enrolled"])

    # Create partner payout record if applicable
    _create_partner_payout(purchase)

    logger.info(
        "Purchase completed: user=%s course=%s amount=$%s",
        purchase.user.username, purchase.course_key, purchase.amount_usd,
    )


def _handle_subscription_updated(subscription):
    """Update team subscription status."""
    sub = TeamSubscription.objects.filter(
        stripe_subscription_id=subscription.get("id", ""),
    ).first()
    if sub:
        sub.status = subscription.get("status", "active")
        sub.save(update_fields=["status", "updated_at"])


def _handle_subscription_deleted(subscription):
    """Cancel team subscription."""
    sub = TeamSubscription.objects.filter(
        stripe_subscription_id=subscription.get("id", ""),
    ).first()
    if sub:
        sub.status = "canceled"
        sub.save(update_fields=["status", "updated_at"])


# ============================================================
# SUBSCRIPTIONS
# ============================================================

@login_required
def subscription_list(request):
    """Show team subscriptions for the current user's organization."""
    subscriptions = TeamSubscription.objects.filter(
        contact_email=request.user.email,
    )
    return render(request, "chronopoli/ecommerce/subscriptions.html", {
        "subscriptions": subscriptions,
    })


# ============================================================
# API ENDPOINTS
# ============================================================

@require_GET
def api_course_pricing(request, course_key):
    """Return pricing info for a course."""
    try:
        pricing = CoursePricingTier.objects.get(course_key=course_key)
        return JsonResponse({
            "course_key": pricing.course_key,
            "layer": pricing.layer,
            "price_usd": str(pricing.price_usd),
            "is_free": pricing.is_free,
            "district_code": pricing.district_code,
        })
    except CoursePricingTier.DoesNotExist:
        return JsonResponse({"is_free": True, "price_usd": "0"})


# ============================================================
# HELPERS
# ============================================================

def _enroll_user(user, course_key):
    """
    Enroll a user in an OpenEdX course via the enrollment API.
    Falls back gracefully if enrollment module is not available.
    """
    try:
        from common.djangoapps.student.models import CourseEnrollment
        from opaque_keys.edx.keys import CourseKey as OpaqueKey

        key = OpaqueKey.from_string(course_key)
        CourseEnrollment.enroll(user, key, mode="honor")
        logger.info("Enrolled %s in %s", user.username, course_key)
    except ImportError:
        logger.warning("OpenEdX enrollment module not available — skipping enrollment")
    except Exception as e:
        logger.error("Enrollment failed for %s in %s: %s", user.username, course_key, e)


def _get_partner_connect_id(course_key):
    """
    Look up the Stripe Connect account ID for the partner who owns this course.
    Returns empty string if no partner or no Connect account.
    """
    try:
        from chronopoli_partners.models import Partner, PartnerTrack

        track = PartnerTrack.objects.select_related("partner").filter(
            course_key=course_key,
            partner__is_active=True,
        ).first()
        if track and hasattr(track.partner, "stripe_connect_account_id"):
            return getattr(track.partner, "stripe_connect_account_id", "")
    except ImportError:
        pass
    return ""


def _create_partner_payout(purchase):
    """
    Create a PartnerPayout record for the 70/30 revenue split.
    Called after a successful purchase of a partner course.
    """
    connect_id = _get_partner_connect_id(purchase.course_key)
    if not connect_id:
        return

    try:
        from chronopoli_partners.models import PartnerTrack

        track = PartnerTrack.objects.select_related("partner").filter(
            course_key=purchase.course_key,
        ).first()
        if not track:
            return

        total = purchase.amount_usd
        partner_share = (total * Decimal("0.70")).quantize(Decimal("0.01"))
        platform_share = total - partner_share

        PartnerPayout.objects.create(
            partner_slug=track.partner.slug,
            stripe_connect_account_id=connect_id,
            course_key=purchase.course_key,
            buyer_email=purchase.user.email,
            total_amount_usd=total,
            partner_share_usd=partner_share,
            platform_share_usd=platform_share,
        )
    except Exception as e:
        logger.error("Failed to create partner payout: %s", e)
