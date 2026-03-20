"""
Initial migration for Chronopoli Company Academy.

Creates all 6 models: LearningPathway, PathwayStep, Badge, UserBadge,
PartnerJobPosting, JobApplication.
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chronopoli_partners", "0001_initial"),
    ]

    operations = [
        # ── LearningPathway ──────────────────────────────────────────
        migrations.CreateModel(
            name="LearningPathway",
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
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField()),
                ("description", models.TextField()),
                ("district_code", models.CharField(max_length=20)),
                ("estimated_hours", models.IntegerField(default=0)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("entry", "Entry"),
                            ("professional", "Professional"),
                            ("advanced", "Advanced"),
                        ],
                        default="entry",
                        max_length=20,
                    ),
                ),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pathways",
                        to="chronopoli_partners.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Learning Pathway",
                "verbose_name_plural": "Learning Pathways",
                "ordering": ["partner", "title"],
                "unique_together": {("partner", "slug")},
            },
        ),
        # ── PathwayStep ──────────────────────────────────────────────
        migrations.CreateModel(
            name="PathwayStep",
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
                ("order", models.IntegerField()),
                ("course_key", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=300)),
                ("is_required", models.BooleanField(default=True)),
                (
                    "pathway",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="chronopoli_academy.learningpathway",
                    ),
                ),
            ],
            options={
                "ordering": ["pathway", "order"],
                "unique_together": {("pathway", "order")},
            },
        ),
        # ── Badge ────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Badge",
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
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField()),
                ("image_url", models.URLField(blank=True)),
                ("criteria_url", models.URLField(blank=True)),
                ("criteria_text", models.TextField(blank=True)),
                (
                    "issuer_name",
                    models.CharField(default="Chronopoli", max_length=200),
                ),
                (
                    "issuer_url",
                    models.URLField(default="https://chronopoli.io"),
                ),
                (
                    "pathway",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="badges",
                        to="chronopoli_academy.learningpathway",
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="chronopoli_partners.partner",
                    ),
                ),
                ("district_code", models.CharField(blank=True, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Badge",
                "verbose_name_plural": "Badges",
                "ordering": ["name"],
            },
        ),
        # ── UserBadge ────────────────────────────────────────────────
        migrations.CreateModel(
            name="UserBadge",
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
                ("evidence_url", models.URLField(blank=True)),
                (
                    "assertion_uid",
                    models.UUIDField(default=uuid.uuid4, unique=True),
                ),
                ("assertion_json", models.JSONField(default=dict)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chronopoli_badges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "badge",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="awards",
                        to="chronopoli_academy.badge",
                    ),
                ),
                (
                    "pathway",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="chronopoli_academy.learningpathway",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "badge")},
            },
        ),
        # ── PartnerJobPosting ────────────────────────────────────────
        migrations.CreateModel(
            name="PartnerJobPosting",
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
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField()),
                ("location", models.CharField(max_length=200)),
                (
                    "required_badges",
                    models.ManyToManyField(
                        blank=True, to="chronopoli_academy.badge"
                    ),
                ),
                ("required_district", models.CharField(blank=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expires_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_postings",
                        to="chronopoli_partners.partner",
                    ),
                ),
            ],
            options={
                "ordering": ["-posted_at"],
            },
        ),
        # ── JobApplication ───────────────────────────────────────────
        migrations.CreateModel(
            name="JobApplication",
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
                ("auto_submitted", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "Submitted"),
                            ("reviewed", "Reviewed"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                        ],
                        default="submitted",
                        max_length=20,
                    ),
                ),
                ("credential_snapshot", models.JSONField(default=dict)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="chronopoli_academy.partnerjobposting",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chronopoli_applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-submitted_at"],
                "unique_together": {("job", "user")},
            },
        ),
    ]
