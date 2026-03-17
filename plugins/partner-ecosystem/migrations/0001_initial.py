"""
Initial migration for Chronopoli Partner Ecosystem.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Partner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("tier", models.CharField(choices=[("founding", "Founding Partner"), ("strategic", "Strategic Partner"), ("content", "Content Partner"), ("institutional", "Institutional Partner")], default="content", max_length=20)),
                ("description", models.TextField(blank=True)),
                ("logo_url", models.URLField(blank=True)),
                ("website_url", models.URLField(blank=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("openedx_org_code", models.CharField(max_length=50, unique=True)),
                ("districts", models.JSONField(default=list, help_text="List of district codes, e.g. ['CHRON-DA', 'CHRON-COMP']")),
                ("is_active", models.BooleanField(default=True)),
                ("onboarded_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Knowledge Partner",
                "verbose_name_plural": "Knowledge Partners",
                "ordering": ["tier", "name"],
            },
        ),
        migrations.CreateModel(
            name="PartnerTrack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=300)),
                ("slug", models.SlugField(max_length=100)),
                ("district_code", models.CharField(help_text="District code, e.g. CHRON-DA", max_length=20)),
                ("description", models.TextField(blank=True)),
                ("course_key", models.CharField(blank=True, max_length=255)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("partner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tracks", to="chronopoli_partners.partner")),
            ],
            options={
                "verbose_name": "Partner Track",
                "verbose_name_plural": "Partner Tracks",
                "unique_together": {("partner", "slug")},
            },
        ),
    ]
