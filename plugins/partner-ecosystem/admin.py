"""
Chronopoli Partner Ecosystem – Django Admin
"""
from django.contrib import admin

from .models import Partner, PartnerTrack


class PartnerTrackInline(admin.TabularInline):
    model = PartnerTrack
    extra = 0
    fields = ("name", "slug", "district_code", "course_key", "is_published")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "openedx_org_code", "is_active", "onboarded_at")
    list_filter = ("tier", "is_active")
    search_fields = ("name", "openedx_org_code")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PartnerTrackInline]


@admin.register(PartnerTrack)
class PartnerTrackAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "district_code", "course_key", "is_published")
    list_filter = ("district_code", "is_published", "partner")
    search_fields = ("name", "course_key")
