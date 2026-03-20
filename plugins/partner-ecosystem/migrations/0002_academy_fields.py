"""
Add academy-related fields to the Partner model.

New fields: subdomain, stripe_connect_account_id, brand_primary_color,
brand_secondary_color, custom_logo_url, academy_enabled, hr_notification_email.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chronopoli_partners", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="subdomain",
            field=models.SlugField(
                blank=True,
                max_length=100,
                unique=True,
                null=True,
                help_text="Subdomain for the partner academy, e.g. 'ripple' for ripple.chronopoli.io",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="stripe_connect_account_id",
            field=models.CharField(
                blank=True,
                max_length=255,
                help_text="Stripe Connect account ID for revenue sharing.",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="brand_primary_color",
            field=models.CharField(
                blank=True,
                max_length=7,
                default="#D4AF37",
                help_text="Hex color for primary brand, e.g. #D4AF37",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="brand_secondary_color",
            field=models.CharField(
                blank=True,
                max_length=7,
                default="#1A1A2E",
                help_text="Hex color for secondary brand, e.g. #1A1A2E",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="custom_logo_url",
            field=models.URLField(
                blank=True,
                help_text="URL for the partner's custom academy logo.",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="academy_enabled",
            field=models.BooleanField(
                default=False,
                help_text="Whether this partner has an active academy subdomain.",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="hr_notification_email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                help_text="Email address for talent pipeline HR notifications.",
            ),
        ),
    ]
