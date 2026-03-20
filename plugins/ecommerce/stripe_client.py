"""
Chronopoli Stripe Client

Thin wrapper around the Stripe Python SDK.
All Stripe keys are read from Django settings (injected by Tutor plugin via SSM).
"""

import logging
from decimal import Decimal

from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy import — stripe may not be installed in dev
_stripe = None


def _get_stripe():
    global _stripe
    if _stripe is None:
        import stripe
        stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        _stripe = stripe
    return _stripe


def create_checkout_session(
    course_key: str,
    price_id: str,
    amount_usd: Decimal,
    user_email: str,
    success_url: str,
    cancel_url: str,
    partner_connect_account_id: str = "",
) -> dict:
    """
    Create a Stripe Checkout Session for a course purchase.
    If partner_connect_account_id is provided, sets up a 70/30 split.

    Returns: {"session_id": "cs_xxx", "url": "https://checkout.stripe.com/..."}
    """
    stripe = _get_stripe()

    params = {
        "mode": "payment",
        "customer_email": user_email,
        "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url,
        "metadata": {"course_key": course_key},
    }

    if price_id:
        params["line_items"] = [{"price": price_id, "quantity": 1}]
    else:
        params["line_items"] = [{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(amount_usd * 100),
                "product_data": {"name": f"Chronopoli Course: {course_key}"},
            },
            "quantity": 1,
        }]

    # 70/30 revenue split via Stripe Connect
    if partner_connect_account_id:
        partner_share = int(amount_usd * 70)  # 70% in cents
        params["payment_intent_data"] = {
            "transfer_data": {
                "destination": partner_connect_account_id,
                "amount": partner_share,
            },
        }

    session = stripe.checkout.Session.create(**params)
    logger.info("Stripe checkout session created: %s for %s", session.id, course_key)
    return {"session_id": session.id, "url": session.url}


def create_team_subscription(
    customer_email: str,
    organization_name: str,
    seats: int,
    price_per_seat_usd: Decimal,
) -> dict:
    """
    Create a Stripe Customer + Subscription for a corporate team.

    Returns: {"customer_id": "cus_xxx", "subscription_id": "sub_xxx"}
    """
    stripe = _get_stripe()

    customer = stripe.Customer.create(
        email=customer_email,
        name=organization_name,
        metadata={"organization": organization_name},
    )

    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(price_per_seat_usd * 100),
                "recurring": {"interval": "year"},
                "product_data": {"name": f"Chronopoli Team — {organization_name}"},
            },
            "quantity": seats,
        }],
        metadata={"organization": organization_name, "seats": str(seats)},
    )

    logger.info(
        "Team subscription created: %s for %s (%d seats)",
        subscription.id, organization_name, seats,
    )
    return {"customer_id": customer.id, "subscription_id": subscription.id}


def verify_webhook_signature(payload: bytes, sig_header: str) -> dict:
    """
    Verify Stripe webhook signature and return parsed event.

    Returns: Stripe Event object or raises ValueError.
    """
    stripe = _get_stripe()
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

    event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    return event
