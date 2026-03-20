from django.urls import path
from . import views

app_name = "chronopoli_ai_tutor"

urlpatterns = [
    path("chat/", views.tutor_chat, name="chat"),
    path("history/", views.tutor_history, name="history"),
]
