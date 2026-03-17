"""
Chronopoli AI Onboarding – URL Configuration
"""
from django.urls import path

from . import views

app_name = "chronopoli_onboarding"

urlpatterns = [
    path("onboarding/", views.onboarding_start, name="start"),
    path("onboarding/submit/", views.onboarding_submit, name="submit"),
    path("onboarding/results/", views.onboarding_results, name="results"),
    path("api/onboarding/status/", views.api_onboarding_status, name="api-status"),
]
