"""
Chronopoli Symposia – Django Admin
"""
from django.contrib import admin

from .models import RoundTable, Invitation, RoundTableOutput, PipelineRun


# ============================================================
# INLINES
# ============================================================

class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0
    fields = (
        "invitee_name",
        "invitee_email",
        "invitee_org",
        "role",
        "status",
        "invite_token",
        "expires_at",
        "responded_at",
    )
    readonly_fields = ("invite_token", "responded_at")
    raw_id_fields = ("invitee_user",)


class RoundTableOutputInline(admin.TabularInline):
    model = RoundTableOutput
    extra = 0
    fields = (
        "output_type",
        "status",
        "s3_key",
        "content_preview",
        "generated_at",
        "approved_by",
        "approved_at",
    )
    readonly_fields = ("generated_at", "approved_at")
    raw_id_fields = ("approved_by",)


# ============================================================
# MODEL ADMINS
# ============================================================

@admin.register(RoundTable)
class RoundTableAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "initiator",
        "status",
        "scheduled_at",
        "duration_mins",
        "created_at",
    )
    list_filter = ("status", "district_codes")
    search_fields = ("title", "slug", "description", "initiator__username")
    readonly_fields = (
        "created_at",
        "updated_at",
        "ivs_channel_arn",
        "ivs_stream_key",
        "ivs_playback_url",
        "ivs_recording_s3",
        "sfn_execution_arn",
    )
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("initiator",)
    inlines = [InvitationInline, RoundTableOutputInline]


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "round_table",
        "status",
        "started_at",
        "completed_at",
    )
    list_filter = ("status",)
    search_fields = (
        "round_table__title",
        "sfn_execution_arn",
        "error_message",
    )
    readonly_fields = ("started_at", "completed_at")
    raw_id_fields = ("round_table",)
