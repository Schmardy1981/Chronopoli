"""
Chronopoli Partner Ecosystem – Django AppConfig
"""
from django.apps import AppConfig


class ChronopoliPartnersConfig(AppConfig):
    name = "chronopoli_partners"
    verbose_name = "Chronopoli Partner Ecosystem"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Register Celery tasks (send_all_weekly_reports) — autodiscovery only scans tasks.py
        import chronopoli_partners.analytics  # noqa: F401
