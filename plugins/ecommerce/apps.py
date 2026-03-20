from django.apps import AppConfig


class ChronopoliEcommerceConfig(AppConfig):
    name = "chronopoli_ecommerce"
    verbose_name = "Chronopoli E-Commerce"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import chronopoli_ecommerce.signals  # noqa: F401
