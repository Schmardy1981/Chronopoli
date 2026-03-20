from django.contrib import admin
from .models import (
    DigitalTwin, TwinDocument, GeneratedQuestion,
    TwinVideo, MasterclassSession,
)


class TwinDocumentInline(admin.TabularInline):
    model = TwinDocument
    extra = 0
    fields = ("title", "doc_type", "s3_key", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class GeneratedQuestionInline(admin.TabularInline):
    model = GeneratedQuestion
    extra = 0
    fields = ("order", "category", "question_text", "is_approved")


class TwinVideoInline(admin.TabularInline):
    model = TwinVideo
    extra = 0
    fields = ("title", "status", "duration_seconds", "created_at")
    readonly_fields = ("created_at",)


@admin.register(DigitalTwin)
class DigitalTwinAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "district_code", "status", "is_published", "created_at")
    list_filter = ("status", "is_published", "district_code")
    search_fields = ("name", "title", "expert__username")
    raw_id_fields = ("expert",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [TwinDocumentInline, GeneratedQuestionInline, TwinVideoInline]


@admin.register(MasterclassSession)
class MasterclassSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "twin", "scheduled_at", "status")
    list_filter = ("status",)
    search_fields = ("title", "twin__name")
    readonly_fields = ("created_at",)
