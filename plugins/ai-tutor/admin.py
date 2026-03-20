from django.contrib import admin
from .models import TutorSession, TutorMessage


class TutorMessageInline(admin.TabularInline):
    model = TutorMessage
    extra = 0
    readonly_fields = ("role", "content", "sources", "tokens_used", "created_at")
    fields = ("role", "content", "sources", "created_at")


@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "district_code", "course_key", "last_activity")
    list_filter = ("district_code",)
    search_fields = ("user__username", "title", "course_key")
    raw_id_fields = ("user",)
    readonly_fields = ("started_at", "last_activity")
    inlines = [TutorMessageInline]


@admin.register(TutorMessage)
class TutorMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "short_content", "created_at")
    list_filter = ("role",)
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    short_content.short_description = "Content"
