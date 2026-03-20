"""
Chronopoli E-Commerce Models

Manages course pricing, team subscriptions, partner payouts, and Stripe events.
Integrates with OpenEdX enrollment API for payment → auto-enrollment flow.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CoursePricingTier(models.Model):
    """
    Maps OpenEdX courses to Stripe prices and learning layers.
    Free courses have is_free=True and price_usd=0.
    """
    LAYER_CHOICES = [
        ("L1", "Entry — $49–$149"),
        ("L2", "Professional — $299–$799"),
        ("L3", "Advanced Practitioner — $999–$2,499"),
        ("L4", "Live Cohort — $3,000–$8,000"),
    ]

    course_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="OpenEdX course key (e.g. course-v1:CHRON-AI+AI-101+2026)",
    )
    layer = models.CharField(max_length=5, choices=LAYER_CHOICES, default="L1")
    price_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stripe Price ID (e.g. price_1abc...). Created via Stripe Dashboard or API.",
    )
    is_free = models.BooleanField(default=True)
    district_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Pricing Tier"
        verbose_name_plural = "Course Pricing Tiers"
        ordering = ["layer", "course_key"]

    def __str__(self):
        price = "FREE" if self.is_free else f"${self.price_usd}"
        return f"{self.course_key} — {self.get_layer_display()} ({price})"


class TeamSubscription(models.Model):
    """
    Corporate/enterprise team subscription via Stripe Billing.
    One subscription per partner, covers N seats.
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("trialing", "Trialing"),
        ("unpaid", "Unpaid"),
    ]

    organization_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    partner_slug = models.CharField(
        max_length=100,
        blank=True,
        help_text="Links to Partner model slug if this is a Company Academy subscription",
    )
    stripe_customer_id = models.CharField(max_length=100, unique=True)
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    seats = models.IntegerField(default=10, help_text="Number of licensed seats")
    seats_used = models.IntegerField(default=0)
    price_per_seat_usd = models.DecimalField(max_digits=8, decimal_places=2, default=125)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Team Subscription"
        verbose_name_plural = "Team Subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization_name} — {self.seats} seats ({self.status})"

    @property
    def seats_remaining(self):
        return max(0, self.seats - self.seats_used)


class PartnerPayout(models.Model):
    """
    Tracks revenue share payouts to partners via Stripe Connect.
    70% to creator/partner, 30% to Chronopoli.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    partner_slug = models.CharField(max_length=100)
    stripe_transfer_id = models.CharField(max_length=100, unique=True, blank=True)
    stripe_connect_account_id = models.CharField(max_length=100)
    course_key = models.CharField(max_length=255)
    buyer_email = models.EmailField()
    total_amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    partner_share_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="70% of total — partner receives this",
    )
    platform_share_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="30% of total — Chronopoli retains this",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Partner Payout"
        verbose_name_plural = "Partner Payouts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.partner_slug} — ${self.partner_share_usd} ({self.status})"


class StripeWebhookEvent(models.Model):
    """
    Logs all Stripe webhook events for auditing and idempotency.
    """
    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    payload = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Stripe Webhook Event"
        verbose_name_plural = "Stripe Webhook Events"
        ordering = ["-received_at"]

    def __str__(self):
        status = "processed" if self.processed else "pending"
        return f"{self.event_type} ({self.stripe_event_id[:20]}...) — {status}"


class Purchase(models.Model):
    """
    Records individual course purchases by users.
    Links Stripe payment to OpenEdX enrollment.
    """
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("completed", "Completed"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chronopoli_purchases")
    course_key = models.CharField(max_length=255)
    pricing_tier = models.ForeignKey(
        CoursePricingTier, on_delete=models.SET_NULL, null=True, blank=True,
    )
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    amount_usd = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    enrolled = models.BooleanField(default=False, help_text="True after OpenEdX enrollment succeeds")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Course Purchase"
        verbose_name_plural = "Course Purchases"
        ordering = ["-created_at"]
        unique_together = [("user", "course_key")]

    def __str__(self):
        return f"{self.user.username} — {self.course_key} (${self.amount_usd})"
