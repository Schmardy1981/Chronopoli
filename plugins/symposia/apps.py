"""
Chronopoli Symposia – Django AppConfig

Phase 11: Round Table system for expert panels, live discussions,
and AI-powered content pipelines (transcript → analysis → social posts).
"""
from django.apps import AppConfig


class ChronopoliSymposiaConfig(AppConfig):
    name = "chronopoli_symposia"
    verbose_name = "Chronopoli Symposia"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import chronopoli_symposia.signals  # noqa: F401
