"""
Chronopoli Company Academy – URL configuration.
"""
from django.urls import path

from chronopoli_academy import views

app_name = "chronopoli_academy"

urlpatterns = [
    # Pages
    path("", views.academy_home, name="academy_home"),
    path("pathway/<slug:slug>/", views.pathway_detail, name="pathway_detail"),
    path("badge/<slug:slug>/", views.badge_detail, name="badge_detail"),
    path("jobs/", views.job_list, name="job_list"),

    # JSON APIs
    path("api/badges/", views.api_user_badges, name="api_user_badges"),
    path(
        "api/pathway/<int:pathway_id>/progress/",
        views.api_pathway_progress,
        name="api_pathway_progress",
    ),
]
