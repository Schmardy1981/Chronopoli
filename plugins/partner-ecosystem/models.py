"""
Chronopoli Partner Ecosystem – Models

Partners are "Knowledge Partners" who host district-branded tracks.
"""
from django.db import models


class Partner(models.Model):
    """
    A Knowledge Partner on the Chronopoli platform.
    """
    TIER_CHOICES = [
        ("founding", "Founding Partner"),
        ("strategic", "Strategic Partner"),
        ("content", "Content Partner"),
        ("institutional", "Institutional Partner"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="content")
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    # OpenEdX org code for this partner (e.g., "RIPPLE", "CARDANO")
    openedx_org_code = models.CharField(max_length=50, unique=True)

    # Which districts this partner operates in
    districts = models.JSONField(
        default=list,
        help_text="List of district codes, e.g. ['CHRON-DA', 'CHRON-COMP']",
    )

    is_active = models.BooleanField(default=True)
    onboarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Knowledge Partner"
        verbose_name_plural = "Knowledge Partners"
        ordering = ["tier", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"


class PartnerTrack(models.Model):
    """
    A learning track hosted by a partner within a district.
    Maps to an OpenEdX course or set of courses.
    """
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name="tracks",
    )
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=100)
    district_code = models.CharField(
        max_length=20,
        help_text="District code, e.g. CHRON-DA",
    )
    description = models.TextField(blank=True)

    # OpenEdX course key (e.g., "course-v1:RIPPLE+DA-001+2025-Q2")
    course_key = models.CharField(max_length=255, blank=True)

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner Track"
        verbose_name_plural = "Partner Tracks"
        unique_together = ("partner", "slug")

    def __str__(self):
        return f"{self.partner.name} – {self.name}"
