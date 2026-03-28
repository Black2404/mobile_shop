from django.urls import path
from .views import chat, admin_chat

urlpatterns = [
    path("chat/", chat),
    path("admin-chat/", admin_chat),
]
