"""
Chronopoli AI Onboarding – Django Admin
"""
from django.contrib import admin

from .models import OnboardingProfile


@admin.register(OnboardingProfile)
class OnboardingProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_type",
        "primary_district",
        "recommended_layer",
        "onboarding_completed",
        "onboarding_completed_at",
    )
    list_filter = (
        "onboarding_completed",
        "user_type",
        "primary_district",
        "recommended_layer",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "questionnaire_answers")
    raw_id_fields = ("user",)
