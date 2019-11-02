from chat.views import ChatViewSet, MessageAPIView
from rest_framework.routers import DefaultRouter
from django.urls import path

chats_router = DefaultRouter()
chats_router.register(r'', ChatViewSet, basename='chats')
# chats_router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = chats_router.urls + [
    path(r'message/<int:pk>/', MessageAPIView.as_view()),
]
