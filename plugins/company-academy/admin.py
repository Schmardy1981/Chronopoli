"""
Chronopoli Company Academy – Admin configuration.
"""
from django.contrib import admin

from chronopoli_academy.models import (
    Badge,
    JobApplication,
    LearningPathway,
    PartnerJobPosting,
    PathwayStep,
    UserBadge,
)


class PathwayStepInline(admin.TabularInline):
    model = PathwayStep
    extra = 1
    ordering = ("order",)


@admin.register(LearningPathway)
class LearningPathwayAdmin(admin.ModelAdmin):
    list_display = ("title", "partner", "district_code", "level", "estimated_hours", "is_published")
    list_filter = ("district_code", "level", "is_published", "partner")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PathwayStepInline]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "issuer_name", "pathway", "partner", "district_code")
    list_filter = ("district_code", "issuer_name", "partner")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "pathway", "assertion_uid", "issued_at")
    list_filter = ("badge", "issued_at")
    search_fields = ("user__username", "user__email", "badge__name")
    readonly_fields = ("assertion_uid", "assertion_json", "issued_at")


@admin.register(PartnerJobPosting)
class PartnerJobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "partner", "location", "is_active", "posted_at", "expires_at")
    list_filter = ("is_active", "partner", "required_district")
    search_fields = ("title", "description", "location")
    filter_horizontal = ("required_badges",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "auto_submitted", "submitted_at")
    list_filter = ("status", "auto_submitted")
    search_fields = ("user__username", "user__email", "job__title")
    readonly_fields = ("credential_snapshot", "submitted_at")
