"""
Chronopoli Digital Twin / Master Class Models

Experts upload documents → AI extracts knowledge → clones voice →
generates avatar → runs live masterclass sessions.
"""

import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DigitalTwin(models.Model):
    """An AI digital twin of an expert, built from their documents and voice."""

    STATUS_CHOICES = [
        ("draft", "Draft — awaiting documents"),
        ("processing", "Processing documents"),
        ("review", "Ready for expert review"),
        ("approved", "Approved — ready for sessions"),
        ("archived", "Archived"),
    ]

    expert = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="digital_twins"
    )
    name = models.CharField(max_length=200, help_text="Expert display name")
    title = models.CharField(max_length=300, help_text="Professional title")
    district_code = models.CharField(max_length=20)
    bio = models.TextField(help_text="Expert biography")
    expertise_summary = models.TextField(
        blank=True, help_text="AI-generated expertise summary"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Voice and avatar IDs from external services
    elevenlabs_voice_id = models.CharField(max_length=100, blank=True)
    heygen_avatar_id = models.CharField(max_length=100, blank=True)

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Digital Twin"
        verbose_name_plural = "Digital Twins"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.title} ({self.district_code})"


class TwinDocument(models.Model):
    """Source document uploaded by the expert. Processed by Textract + Claude."""

    DOC_TYPE_CHOICES = [
        ("research_paper", "Research Paper"),
        ("policy_brief", "Policy Brief"),
        ("book_chapter", "Book Chapter"),
        ("presentation", "Presentation"),
        ("report", "Report"),
        ("other", "Other"),
    ]

    twin = models.ForeignKey(
        DigitalTwin, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=300)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default="other")
    s3_key = models.CharField(max_length=500, help_text="S3 path to uploaded document")
    extracted_text = models.TextField(blank=True, help_text="Text extracted by Textract")
    analysis = models.JSONField(
        default=dict,
        help_text="Claude analysis: core_theses, expertise_boundaries, key_insights",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Twin Document"
        verbose_name_plural = "Twin Documents"
        ordering = ["twin", "-uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.twin.name})"


class GeneratedQuestion(models.Model):
    """AI-generated interview question based on the expert's documents."""

    CATEGORY_CHOICES = [
        ("foundation", "Foundation — establishing core expertise"),
        ("deep_dive", "Deep Dive — exploring specific insights"),
        ("confrontational", "Confrontational — challenging assumptions"),
        ("audience", "Audience — anticipated audience questions"),
    ]

    twin = models.ForeignKey(
        DigitalTwin, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    suggested_answer = models.TextField(
        blank=True, help_text="AI-suggested answer based on documents"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    order = models.IntegerField()
    is_approved = models.BooleanField(
        default=False, help_text="Expert approved this question"
    )

    class Meta:
        verbose_name = "Generated Question"
        verbose_name_plural = "Generated Questions"
        ordering = ["twin", "category", "order"]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:80]}..."


class TwinVideo(models.Model):
    """AI-generated avatar video using HeyGen."""

    STATUS_CHOICES = [
        ("pending", "Pending generation"),
        ("generating", "Generating via HeyGen"),
        ("ready", "Ready"),
        ("failed", "Generation failed"),
    ]

    twin = models.ForeignKey(
        DigitalTwin, on_delete=models.CASCADE, related_name="videos"
    )
    title = models.CharField(max_length=300)
    script_text = models.TextField(help_text="Text for the avatar to speak")
    heygen_video_id = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=500, blank=True)
    duration_seconds = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Twin Video"
        verbose_name_plural = "Twin Videos"
        ordering = ["twin", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class MasterclassSession(models.Model):
    """A live masterclass event using a Digital Twin."""

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("ended", "Ended"),
        ("published", "Published"),
    ]

    twin = models.ForeignKey(
        DigitalTwin, on_delete=models.CASCADE, related_name="sessions"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    # IVS reuse from Symposia
    ivs_channel_arn = models.CharField(max_length=500, blank=True)
    ivs_playback_url = models.CharField(max_length=500, blank=True)
    recording_s3_key = models.CharField(max_length=500, blank=True)

    # Link to Symposia Round Table for post-session pipeline
    symposia_roundtable_id = models.IntegerField(
        null=True, blank=True,
        help_text="Links to chronopoli_symposia.RoundTable for output generation",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Masterclass Session"
        verbose_name_plural = "Masterclass Sessions"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.title} — {self.twin.name} ({self.status})"
