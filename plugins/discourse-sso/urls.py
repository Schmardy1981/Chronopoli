from django.urls import path
from . import views

app_name = "chronopoli_discourse_sso"

urlpatterns = [
    path("sso/", views.discourse_sso, name="discourse-sso"),
]
