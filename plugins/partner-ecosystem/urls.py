"""
Chronopoli Partner Ecosystem – URL Configuration
"""
from django.urls import path

from . import views
from . import dashboard_views

app_name = "chronopoli_partners"

urlpatterns = [
    path("", views.partner_list, name="list"),
    path("api/", views.api_partners, name="api-list"),
    path("<slug:slug>/", views.partner_detail, name="detail"),
    # Partner Dashboard (Phase 15)
    path("<slug:slug>/dashboard/", dashboard_views.partner_dashboard, name="dashboard"),
    path("api/<slug:slug>/analytics/", dashboard_views.api_analytics, name="api-analytics"),
    path("api/<slug:slug>/reports/", dashboard_views.api_intelligence_reports, name="api-reports"),
]
