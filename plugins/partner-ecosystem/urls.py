"""
Chronopoli Partner Ecosystem – URL Configuration
"""
from django.urls import path

from . import views

app_name = "chronopoli_partners"

urlpatterns = [
    path("", views.partner_list, name="list"),
    path("api/", views.api_partners, name="api-list"),
    path("<slug:slug>/", views.partner_detail, name="detail"),
]
