from django.contrib import admin
from .models import (
    CoursePricingTier,
    TeamSubscription,
    PartnerPayout,
    StripeWebhookEvent,
    Purchase,
)


@admin.register(CoursePricingTier)
class CoursePricingTierAdmin(admin.ModelAdmin):
    list_display = ("course_key", "layer", "price_usd", "is_free", "district_code")
    list_filter = ("layer", "is_free", "district_code")
    search_fields = ("course_key",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(TeamSubscription)
class TeamSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "organization_name", "seats", "seats_used", "status",
        "price_per_seat_usd", "current_period_end",
    )
    list_filter = ("status",)
    search_fields = ("organization_name", "contact_email", "partner_slug")
    readonly_fields = ("created_at", "updated_at", "seats_remaining")

    def seats_remaining(self, obj):
        return obj.seats_remaining
    seats_remaining.short_description = "Seats Remaining"


@admin.register(PartnerPayout)
class PartnerPayoutAdmin(admin.ModelAdmin):
    list_display = (
        "partner_slug", "course_key", "total_amount_usd",
        "partner_share_usd", "platform_share_usd", "status", "created_at",
    )
    list_filter = ("status", "partner_slug")
    search_fields = ("partner_slug", "course_key", "buyer_email")
    readonly_fields = ("created_at",)


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("stripe_event_id", "event_type", "processed", "received_at")
    list_filter = ("event_type", "processed")
    search_fields = ("stripe_event_id",)
    readonly_fields = ("received_at", "payload")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user", "course_key", "amount_usd", "status", "enrolled", "created_at",
    )
    list_filter = ("status", "enrolled")
    search_fields = ("user__username", "user__email", "course_key")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "completed_at")
