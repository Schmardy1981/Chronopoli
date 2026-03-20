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
            name="TutorSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("district_code", models.CharField(blank=True, max_length=20)),
                ("course_key", models.CharField(blank=True, max_length=255)),
                ("title", models.CharField(default="New conversation", max_length=300)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("last_activity", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tutor_sessions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Tutor Session", "verbose_name_plural": "Tutor Sessions", "ordering": ["-last_activity"]},
        ),
        migrations.CreateModel(
            name="TutorMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("user", "User"), ("assistant", "Assistant")], max_length=10)),
                ("content", models.TextField()),
                ("sources", models.JSONField(default=list)),
                ("tokens_used", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="chronopoli_ai_tutor.tutorsession")),
            ],
            options={"verbose_name": "Tutor Message", "verbose_name_plural": "Tutor Messages", "ordering": ["session", "created_at"]},
        ),
    ]
