"""
Chronopoli Discourse SSO – OpenEdX acts as Identity Provider (IDP).

When a user clicks "Community" in OpenEdX, Discourse redirects them to
this endpoint. We validate the SSO payload, attach user info, and
redirect back to Discourse — the user is logged in automatically.

Protocol: https://meta.discourse.org/t/discourseconnect-official-single-sign-on-for-discourse-sso/13045
"""

import base64
import hashlib
import hmac
import urllib.parse
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect

logger = logging.getLogger(__name__)


def _get_sso_secret():
    return getattr(settings, "DISCOURSE_SSO_SECRET", "")


def _get_discourse_url():
    return getattr(settings, "DISCOURSE_BASE_URL", "https://community.chronopoli.io")


@login_required
def discourse_sso(request):
    """
    Handle Discourse SSO handshake.

    1. Discourse sends user here with `sso` (base64 payload) and `sig` (HMAC)
    2. We verify the signature
    3. We build a return payload with user info from OpenEdX
    4. We redirect back to Discourse with the signed payload
    """
    sso_secret = _get_sso_secret()
    if not sso_secret:
        logger.error("DISCOURSE_SSO_SECRET not configured")
        return HttpResponseBadRequest("SSO not configured")

    # Get payload and signature from Discourse
    payload = request.GET.get("sso", "")
    signature = request.GET.get("sig", "")

    if not payload or not signature:
        return HttpResponseBadRequest("Missing SSO parameters")

    # Verify HMAC-SHA256 signature
    expected_sig = hmac.new(
        sso_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        logger.warning("Discourse SSO signature mismatch for user %s", request.user.username)
        return HttpResponseBadRequest("Invalid SSO signature")

    # Decode the payload to get the nonce
    decoded = base64.b64decode(payload).decode("utf-8")
    params = urllib.parse.parse_qs(decoded)
    nonce = params.get("nonce", [None])[0]

    if not nonce:
        return HttpResponseBadRequest("Missing nonce in SSO payload")

    # Build return payload with OpenEdX user info
    user = request.user
    user_params = {
        "nonce": nonce,
        "email": user.email,
        "external_id": str(user.id),
        "username": user.username,
        "name": user.get_full_name() or user.username,
        "admin": "true" if user.is_staff else "false",
        "moderator": "true" if user.is_staff else "false",
    }

    # Add avatar URL if available
    try:
        from common.djangoapps.student.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        if profile.profile_image_uploaded_at:
            lms_base = getattr(settings, "LMS_ROOT_URL", "")
            user_params["avatar_url"] = (
                f"{lms_base}/api/profile_images/{user.username}/upload"
            )
    except Exception:
        pass

    # Add district group if onboarding is complete
    try:
        from chronopoli_onboarding.models import OnboardingProfile
        onboarding = OnboardingProfile.objects.get(user=user)
        if onboarding.primary_district:
            district_group = {
                "CHRON-AI": "ai-district",
                "CHRON-DA": "digital-assets-district",
                "CHRON-GOV": "governance-district",
                "CHRON-COMP": "compliance-district",
                "CHRON-INV": "investigation-district",
                "CHRON-RISK": "risk-trust-district",
                "CHRON-ET":   "emerging-tech-district",
            }.get(onboarding.primary_district, "")
            if district_group:
                user_params["add_groups"] = district_group
    except Exception:
        pass

    # Encode and sign the return payload
    return_payload = urllib.parse.urlencode(user_params)
    encoded_payload = base64.b64encode(return_payload.encode("utf-8")).decode("utf-8")
    return_sig = hmac.new(
        sso_secret.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Redirect back to Discourse
    discourse_url = _get_discourse_url()
    redirect_url = (
        f"{discourse_url}/session/sso_login"
        f"?sso={urllib.parse.quote(encoded_payload)}"
        f"&sig={return_sig}"
    )

    logger.info("Discourse SSO login for user %s → %s", user.username, discourse_url)
    return HttpResponseRedirect(redirect_url)
