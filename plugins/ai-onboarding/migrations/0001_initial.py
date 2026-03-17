"""
Initial migration for Chronopoli AI Onboarding.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OnboardingProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("onboarding_completed", models.BooleanField(default=False)),
                (
                    "onboarding_completed_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "user_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("regulator", "Regulator / Government"),
                            ("law_enforcement", "Law Enforcement / FIU"),
                            ("bank", "Bank / Financial Institution"),
                            ("exchange", "Crypto Exchange"),
                            ("enterprise", "Enterprise Leader"),
                            ("founder", "Founder / Startup"),
                            ("student", "Student / Professional"),
                            ("consultant", "Consultant / Advisor"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                ("primary_district", models.CharField(blank=True, max_length=20)),
                ("secondary_districts", models.JSONField(default=list)),
                (
                    "recommended_layer",
                    models.CharField(
                        choices=[
                            ("entry", "L1 \u2013 Entry"),
                            ("professional", "L2 \u2013 Professional"),
                            ("institutional", "L3 \u2013 Institutional"),
                            ("influence", "L4 \u2013 Influence"),
                        ],
                        default="entry",
                        max_length=20,
                    ),
                ),
                ("questionnaire_answers", models.JSONField(default=dict)),
                ("recommended_courses", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chronopoli_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Chronopoli Onboarding Profile",
                "verbose_name_plural": "Chronopoli Onboarding Profiles",
            },
        ),
    ]
