"""
Chronopoli Symposia – URL Configuration
"""
from django.urls import path

from . import views

app_name = "chronopoli_symposia"

urlpatterns = [
    # Pages
    path("symposia/", views.roundtable_list, name="list"),
    path("symposia/schedule/", views.roundtable_schedule, name="schedule"),
    path("symposia/approve/", views.approval_view, name="approve"),
    path("symposia/<slug:slug>/", views.roundtable_detail, name="detail"),

    # API
    path(
        "api/symposia/output/<int:output_id>/approve/",
        views.api_approve_output,
        name="api-approve-output",
    ),
    path(
        "api/symposia/<slug:slug>/status/",
        views.api_roundtable_status,
        name="api-roundtable-status",
    ),
]
