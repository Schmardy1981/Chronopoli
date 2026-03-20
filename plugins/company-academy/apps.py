"""
Chronopoli Company Academy – Django app configuration.
"""
from django.apps import AppConfig


class ChronopoliAcademyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chronopoli_academy"
    verbose_name = "Chronopoli Company Academy"

    def ready(self):
        import chronopoli_academy.signals  # noqa: F401
