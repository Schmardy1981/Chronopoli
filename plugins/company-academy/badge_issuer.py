"""
Chronopoli Company Academy – Badge Issuer

Implements Open Badges 2.0 assertion creation and validation.
https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/index.html
"""
import logging
import uuid

from django.db import IntegrityError
from django.utils import timezone

from chronopoli_academy.models import Badge, UserBadge

logger = logging.getLogger(__name__)

OB2_CONTEXT = "https://w3id.org/openbadges/v2"


def build_assertion_json(user, badge):
    """
    Build a valid Open Badges 2.0 Assertion JSON-LD dictionary.

    Args:
        user: Django User instance (the recipient).
        badge: Badge model instance.

    Returns:
        dict: OB2-compliant assertion.
    """
    assertion_uid = str(uuid.uuid4())
    issued_on = timezone.now().isoformat()

    assertion = {
        "@context": OB2_CONTEXT,
        "type": "Assertion",
        "id": f"urn:uuid:{assertion_uid}",
        "recipient": {
            "type": "email",
            "identity": f"sha256${_sha256(user.email)}",
            "hashed": True,
        },
        "badge": {
            "type": "BadgeClass",
            "id": f"https://chronopoli.io/badges/{badge.slug}",
            "name": badge.name,
            "description": badge.description,
            "image": badge.image_url or "https://chronopoli.io/static/badges/default.png",
            "criteria": {
                "narrative": badge.criteria_text,
            },
            "issuer": {
                "type": "Issuer",
                "id": badge.issuer_url,
                "name": badge.issuer_name,
                "url": badge.issuer_url,
            },
        },
        "issuedOn": issued_on,
        "verification": {
            "type": "hosted",
        },
    }

    if badge.criteria_url:
        assertion["badge"]["criteria"]["id"] = badge.criteria_url

    return assertion


def award_badge(user, badge, pathway=None):
    """
    Award a badge to a user, creating a UserBadge with OB2 assertion JSON.

    If the user already has this badge, this is a no-op (returns existing award).

    Args:
        user: Django User instance.
        badge: Badge model instance.
        pathway: Optional LearningPathway instance.

    Returns:
        UserBadge instance.
    """
    existing = UserBadge.objects.filter(user=user, badge=badge).first()
    if existing:
        logger.debug(
            "User %s already has badge '%s'; skipping.",
            user.username,
            badge.name,
        )
        return existing

    assertion = build_assertion_json(user, badge)

    try:
        user_badge = UserBadge.objects.create(
            user=user,
            badge=badge,
            pathway=pathway,
            evidence_url=f"https://chronopoli.io/academy/badge/{badge.slug}",
            assertion_json=assertion,
        )
        logger.info(
            "Badge '%s' awarded to %s (assertion %s).",
            badge.name,
            user.username,
            user_badge.assertion_uid,
        )
        return user_badge
    except IntegrityError:
        # Race condition — badge already awarded between check and create
        logger.debug(
            "Duplicate badge award for %s / '%s'; returning existing.",
            user.username,
            badge.name,
        )
        return UserBadge.objects.get(user=user, badge=badge)


def verify_assertion(assertion_json):
    """
    Validate the structure of an Open Badges 2.0 assertion.

    Args:
        assertion_json: dict to validate.

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    if not isinstance(assertion_json, dict):
        return False, ["Assertion must be a JSON object."]

    if assertion_json.get("@context") != OB2_CONTEXT:
        errors.append(f"Missing or invalid @context (expected {OB2_CONTEXT}).")

    if assertion_json.get("type") != "Assertion":
        errors.append("Missing or invalid type (expected 'Assertion').")

    if "id" not in assertion_json:
        errors.append("Missing 'id' field.")

    recipient = assertion_json.get("recipient")
    if not isinstance(recipient, dict):
        errors.append("Missing or invalid 'recipient' object.")
    else:
        if "identity" not in recipient:
            errors.append("Missing 'recipient.identity'.")
        if "type" not in recipient:
            errors.append("Missing 'recipient.type'.")

    badge_obj = assertion_json.get("badge")
    if not isinstance(badge_obj, dict):
        errors.append("Missing or invalid 'badge' object.")
    else:
        for field in ("name", "description", "issuer"):
            if field not in badge_obj:
                errors.append(f"Missing 'badge.{field}'.")

    if "issuedOn" not in assertion_json:
        errors.append("Missing 'issuedOn' field.")

    return (len(errors) == 0, errors)


def _sha256(value):
    """SHA-256 hash of a string, returned as hex digest."""
    import hashlib
    return hashlib.sha256(value.lower().strip().encode("utf-8")).hexdigest()
