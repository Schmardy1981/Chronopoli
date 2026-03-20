"""
Chronopoli AI Tutor Models

Conversational AI tutor powered by Amazon Bedrock Knowledge Bases.
Tracks sessions and messages per user with source citations.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TutorSession(models.Model):
    """A conversation session between a user and the AI Tutor."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tutor_sessions"
    )
    district_code = models.CharField(max_length=20, blank=True)
    course_key = models.CharField(
        max_length=255, blank=True,
        help_text="If started from within a course context",
    )
    title = models.CharField(max_length=300, default="New conversation")
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tutor Session"
        verbose_name_plural = "Tutor Sessions"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"{self.user.username} — {self.title} ({self.district_code})"


class TutorMessage(models.Model):
    """Individual message in a tutor conversation."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(
        TutorSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    sources = models.JSONField(
        default=list,
        help_text="Knowledge base source citations [{uri, title, score}]",
    )
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tutor Message"
        verbose_name_plural = "Tutor Messages"
        ordering = ["session", "created_at"]

    def __str__(self):
        preview = self.content[:80] + "..." if len(self.content) > 80 else self.content
        return f"[{self.role}] {preview}"
