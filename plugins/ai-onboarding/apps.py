"""
Chronopoli AI Onboarding – Django AppConfig
"""
from django.apps import AppConfig


class ChronopoliOnboardingConfig(AppConfig):
    name = "chronopoli_onboarding"
    verbose_name = "Chronopoli AI Onboarding"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import chronopoli_onboarding.signals  # noqa: F401
