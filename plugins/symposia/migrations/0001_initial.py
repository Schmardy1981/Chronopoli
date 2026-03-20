"""
Initial migration for Chronopoli Symposia.
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
        # ----------------------------------------------------------
        # RoundTable
        # ----------------------------------------------------------
        migrations.CreateModel(
            name="RoundTable",
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
                ("slug", models.SlugField(unique=True)),
                ("district_codes", models.JSONField(default=list)),
                ("description", models.TextField()),
                ("agenda", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("open", "Open for Invitations"),
                            ("confirmed", "Confirmed"),
                            ("live", "Live"),
                            ("recording", "Recording"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("published", "Published"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("duration_mins", models.IntegerField(default=90)),
                ("ivs_channel_arn", models.CharField(blank=True, max_length=500)),
                ("ivs_stream_key", models.CharField(blank=True, max_length=500)),
                ("ivs_playback_url", models.CharField(blank=True, max_length=500)),
                ("ivs_recording_s3", models.CharField(blank=True, max_length=500)),
                ("sfn_execution_arn", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "initiator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="initiated_roundtables",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Round Table",
                "verbose_name_plural": "Round Tables",
                "ordering": ["-scheduled_at"],
            },
        ),
        # ----------------------------------------------------------
        # Invitation
        # ----------------------------------------------------------
        migrations.CreateModel(
            name="Invitation",
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
                ("invitee_email", models.EmailField(max_length=254)),
                ("invitee_name", models.CharField(max_length=200)),
                ("invitee_org", models.CharField(blank=True, max_length=200)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("panelist", "Panelist"),
                            ("moderator", "Moderator"),
                            ("observer", "Observer"),
                        ],
                        default="panelist",
                        max_length=20,
                    ),
                ),
                ("invite_token", models.CharField(max_length=64, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "invitee_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "round_table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitations",
                        to="chronopoli_symposia.roundtable",
                    ),
                ),
            ],
            options={
                "verbose_name": "Round Table Invitation",
                "verbose_name_plural": "Round Table Invitations",
                "ordering": ["-created_at"],
            },
        ),
        # ----------------------------------------------------------
        # RoundTableOutput
        # ----------------------------------------------------------
        migrations.CreateModel(
            name="RoundTableOutput",
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
                (
                    "output_type",
                    models.CharField(
                        choices=[
                            ("transcript", "Transcript"),
                            ("analysis", "Analysis"),
                            ("opinion_paper", "Opinion Paper"),
                            ("linkedin_post", "LinkedIn Post"),
                            ("instagram_carousel", "Instagram Carousel"),
                            ("video_script", "Video Script"),
                            ("partner_report", "Partner Report"),
                        ],
                        max_length=30,
                    ),
                ),
                ("s3_key", models.CharField(max_length=500)),
                ("content_preview", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("generated", "Generated"),
                            ("approved", "Approved"),
                            ("published", "Published"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("generated_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_outputs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "round_table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outputs",
                        to="chronopoli_symposia.roundtable",
                    ),
                ),
            ],
            options={
                "verbose_name": "Round Table Output",
                "verbose_name_plural": "Round Table Outputs",
                "ordering": ["round_table", "output_type"],
                "unique_together": {("round_table", "output_type")},
            },
        ),
        # ----------------------------------------------------------
        # PipelineRun
        # ----------------------------------------------------------
        migrations.CreateModel(
            name="PipelineRun",
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
                ("sfn_execution_arn", models.CharField(max_length=500)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("running", "Running"),
                            ("waiting_approval", "Waiting for Approval"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="running",
                        max_length=20,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "round_table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pipeline_runs",
                        to="chronopoli_symposia.roundtable",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pipeline Run",
                "verbose_name_plural": "Pipeline Runs",
                "ordering": ["-started_at"],
            },
        ),
    ]
