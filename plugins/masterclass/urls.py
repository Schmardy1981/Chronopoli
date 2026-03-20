from django.urls import path
from . import views

app_name = "chronopoli_masterclass"

urlpatterns = [
    path("", views.twin_list, name="list"),
    path("create/", views.twin_create, name="create"),
    path("<int:pk>/", views.twin_detail, name="detail"),
    path("<int:pk>/upload/", views.twin_upload_document, name="upload"),
    path("<int:pk>/generate-questions/", views.twin_generate_questions, name="generate-questions"),
    path("session/<int:pk>/", views.session_detail, name="session"),
    path("api/<int:pk>/", views.api_twin_detail, name="api-detail"),
]
