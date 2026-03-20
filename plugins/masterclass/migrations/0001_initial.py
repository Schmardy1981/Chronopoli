import uuid
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
            name="DigitalTwin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("title", models.CharField(max_length=300)),
                ("district_code", models.CharField(max_length=20)),
                ("bio", models.TextField()),
                ("expertise_summary", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("processing", "Processing"), ("review", "Review"), ("approved", "Approved"), ("archived", "Archived")], default="draft", max_length=20)),
                ("elevenlabs_voice_id", models.CharField(blank=True, max_length=100)),
                ("heygen_avatar_id", models.CharField(blank=True, max_length=100)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("expert", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="digital_twins", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Digital Twin", "verbose_name_plural": "Digital Twins", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="TwinDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("doc_type", models.CharField(choices=[("research_paper", "Research Paper"), ("policy_brief", "Policy Brief"), ("book_chapter", "Book Chapter"), ("presentation", "Presentation"), ("report", "Report"), ("other", "Other")], default="other", max_length=20)),
                ("s3_key", models.CharField(max_length=500)),
                ("extracted_text", models.TextField(blank=True)),
                ("analysis", models.JSONField(default=dict)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("twin", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="chronopoli_masterclass.digitaltwin")),
            ],
            options={"verbose_name": "Twin Document", "verbose_name_plural": "Twin Documents", "ordering": ["twin", "-uploaded_at"]},
        ),
        migrations.CreateModel(
            name="GeneratedQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("suggested_answer", models.TextField(blank=True)),
                ("category", models.CharField(choices=[("foundation", "Foundation"), ("deep_dive", "Deep Dive"), ("confrontational", "Confrontational"), ("audience", "Audience")], max_length=20)),
                ("order", models.IntegerField()),
                ("is_approved", models.BooleanField(default=False)),
                ("twin", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="chronopoli_masterclass.digitaltwin")),
            ],
            options={"verbose_name": "Generated Question", "verbose_name_plural": "Generated Questions", "ordering": ["twin", "category", "order"]},
        ),
        migrations.CreateModel(
            name="TwinVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("script_text", models.TextField()),
                ("heygen_video_id", models.CharField(blank=True, max_length=100)),
                ("s3_key", models.CharField(blank=True, max_length=500)),
                ("duration_seconds", models.IntegerField(default=0)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("generating", "Generating"), ("ready", "Ready"), ("failed", "Failed")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("twin", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="videos", to="chronopoli_masterclass.digitaltwin")),
            ],
            options={"verbose_name": "Twin Video", "verbose_name_plural": "Twin Videos", "ordering": ["twin", "-created_at"]},
        ),
        migrations.CreateModel(
            name="MasterclassSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                ("scheduled_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("live", "Live"), ("ended", "Ended"), ("published", "Published")], default="scheduled", max_length=20)),
                ("ivs_channel_arn", models.CharField(blank=True, max_length=500)),
                ("ivs_playback_url", models.CharField(blank=True, max_length=500)),
                ("recording_s3_key", models.CharField(blank=True, max_length=500)),
                ("symposia_roundtable_id", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("twin", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="chronopoli_masterclass.digitaltwin")),
            ],
            options={"verbose_name": "Masterclass Session", "verbose_name_plural": "Masterclass Sessions", "ordering": ["-scheduled_at"]},
        ),
    ]
