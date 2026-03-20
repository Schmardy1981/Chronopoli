"""
Chronopoli Company Academy – Models

Provides Learning Pathways, Open Badges 2.0 credentials,
and a talent pipeline connecting learners to partner job postings.
"""
import uuid

from django.conf import settings
from django.db import models


class LearningPathway(models.Model):
    """
    A structured learning pathway curated by a Knowledge Partner.
    Consists of ordered course steps leading to a badge.
    """
    LEVEL_CHOICES = [
        ("entry", "Entry"),
        ("professional", "Professional"),
        ("advanced", "Advanced"),
    ]

    partner = models.ForeignKey(
        "chronopoli_partners.Partner",
        on_delete=models.CASCADE,
        related_name="pathways",
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField()
    description = models.TextField()
    district_code = models.CharField(max_length=20)
    estimated_hours = models.IntegerField(default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="entry")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Learning Pathway"
        verbose_name_plural = "Learning Pathways"
        ordering = ["partner", "title"]
        unique_together = ("partner", "slug")

    def __str__(self):
        return f"{self.partner.name} – {self.title}"


class PathwayStep(models.Model):
    """
    An ordered step within a Learning Pathway, mapping to an OpenEdX course.
    """
    pathway = models.ForeignKey(
        LearningPathway,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    order = models.IntegerField()
    course_key = models.CharField(max_length=255)
    title = models.CharField(max_length=300)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["pathway", "order"]
        unique_together = ("pathway", "order")

    def __str__(self):
        return f"{self.pathway.title} – Step {self.order}: {self.title}"


class Badge(models.Model):
    """
    An Open Badges 2.0 badge class. Linked to a pathway and/or partner.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)
    criteria_url = models.URLField(blank=True)
    criteria_text = models.TextField(blank=True)
    issuer_name = models.CharField(max_length=200, default="Chronopoli")
    issuer_url = models.URLField(default="https://chronopoli.io")
    pathway = models.ForeignKey(
        LearningPathway,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="badges",
    )
    partner = models.ForeignKey(
        "chronopoli_partners.Partner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """
    A badge awarded to a user, containing the Open Badges 2.0 assertion.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chronopoli_badges",
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="awards",
    )
    pathway = models.ForeignKey(
        LearningPathway,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    evidence_url = models.URLField(blank=True)
    assertion_uid = models.UUIDField(default=uuid.uuid4, unique=True)
    assertion_json = models.JSONField(default=dict)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user} – {self.badge.name}"


class PartnerJobPosting(models.Model):
    """
    A job posting from a Knowledge Partner, optionally requiring specific
    badges or district credentials.
    """
    partner = models.ForeignKey(
        "chronopoli_partners.Partner",
        on_delete=models.CASCADE,
        related_name="job_postings",
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    location = models.CharField(max_length=200)
    required_badges = models.ManyToManyField(Badge, blank=True)
    required_district = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self):
        return f"{self.partner.name} – {self.title}"


class JobApplication(models.Model):
    """
    A user's application to a partner job posting.
    May be auto-submitted by the talent pipeline.
    """
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    job = models.ForeignKey(
        PartnerJobPosting,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chronopoli_applications",
    )
    auto_submitted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    credential_snapshot = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "user")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user} → {self.job.title} ({self.status})"
