"""
Chronopoli Symposia – Models

Round Tables: scheduled expert panels streamed via AWS IVS, recorded to S3,
then processed through a Step Functions pipeline that generates transcripts,
analysis papers, social-media posts, and partner reports.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================
# ROUND TABLE
# ============================================================

class RoundTable(models.Model):
    """
    A scheduled expert discussion panel within one or more Knowledge Districts.
    Streamed live via AWS IVS, recorded, then fed into the content pipeline.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open for Invitations"),
        ("confirmed", "Confirmed"),
        ("live", "Live"),
        ("recording", "Recording"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="initiated_roundtables",
    )
    district_codes = models.JSONField(
        default=list,
        help_text="List of district codes, e.g. ['CHRON-AI', 'CHRON-COMP']",
    )
    description = models.TextField()
    agenda = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    duration_mins = models.IntegerField(default=90)

    # AWS IVS fields
    ivs_channel_arn = models.CharField(max_length=500, blank=True)
    ivs_stream_key = models.CharField(max_length=500, blank=True)
    ivs_playback_url = models.CharField(max_length=500, blank=True)
    ivs_recording_s3 = models.CharField(max_length=500, blank=True)

    # Step Functions pipeline
    sfn_execution_arn = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Round Table"
        verbose_name_plural = "Round Tables"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


# ============================================================
# INVITATION
# ============================================================

class Invitation(models.Model):
    """
    An invitation sent to an expert to join a Round Table as panelist,
    moderator, or observer.
    """

    ROLE_CHOICES = [
        ("panelist", "Panelist"),
        ("moderator", "Moderator"),
        ("observer", "Observer"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    round_table = models.ForeignKey(
        RoundTable,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invitee_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    invitee_email = models.EmailField()
    invitee_name = models.CharField(max_length=200)
    invitee_org = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization name, e.g. Ripple, Cardano",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="panelist",
    )
    invite_token = models.CharField(max_length=64, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Round Table Invitation"
        verbose_name_plural = "Round Table Invitations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invitee_name} → {self.round_table.title} ({self.get_status_display()})"


# ============================================================
# ROUND TABLE OUTPUT
# ============================================================

class RoundTableOutput(models.Model):
    """
    A content artefact produced by the post-session pipeline:
    transcript, analysis paper, social posts, partner report, etc.
    """

    OUTPUT_TYPE_CHOICES = [
        ("transcript", "Transcript"),
        ("analysis", "Analysis"),
        ("opinion_paper", "Opinion Paper"),
        ("linkedin_post", "LinkedIn Post"),
        ("instagram_carousel", "Instagram Carousel"),
        ("video_script", "Video Script"),
        ("partner_report", "Partner Report"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generated", "Generated"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("rejected", "Rejected"),
    ]

    round_table = models.ForeignKey(
        RoundTable,
        on_delete=models.CASCADE,
        related_name="outputs",
    )
    output_type = models.CharField(
        max_length=30,
        choices=OUTPUT_TYPE_CHOICES,
    )
    s3_key = models.CharField(max_length=500)
    content_preview = models.TextField(
        blank=True,
        help_text="First 500 characters of generated content",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    generated_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_outputs",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Round Table Output"
        verbose_name_plural = "Round Table Outputs"
        ordering = ["round_table", "output_type"]
        unique_together = [("round_table", "output_type")]

    def __str__(self):
        return f"{self.round_table.title} – {self.get_output_type_display()}"


# ============================================================
# PIPELINE RUN
# ============================================================

class PipelineRun(models.Model):
    """
    Tracks a single execution of the AWS Step Functions content pipeline
    for a Round Table session.
    """

    STATUS_CHOICES = [
        ("running", "Running"),
        ("waiting_approval", "Waiting for Approval"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    round_table = models.ForeignKey(
        RoundTable,
        on_delete=models.CASCADE,
        related_name="pipeline_runs",
    )
    sfn_execution_arn = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="running",
    )
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pipeline Run"
        verbose_name_plural = "Pipeline Runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Pipeline {self.pk} – {self.round_table.title} ({self.get_status_display()})"
