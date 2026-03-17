"""
Chronopoli AI Onboarding – Signals

Redirects new users to the onboarding questionnaire after registration.
"""
import logging

from django.dispatch import receiver

log = logging.getLogger(__name__)

try:
    from common.djangoapps.student.signals import REGISTER_USER
    HAVE_OPENEDX_SIGNALS = True
except ImportError:
    HAVE_OPENEDX_SIGNALS = False
    log.info("OpenEdX student signals not available – running outside OpenEdX context")


if HAVE_OPENEDX_SIGNALS:
    @receiver(REGISTER_USER)
    def handle_user_registration(sender, user, **kwargs):
        """
        When a new user registers, create their onboarding profile.
        The actual redirect to /chronopoli/onboarding/ is handled by
        middleware or the login redirect URL setting.
        """
        from .models import OnboardingProfile

        OnboardingProfile.objects.get_or_create(user=user)
        log.info("Created Chronopoli onboarding profile for user: %s", user.username)
