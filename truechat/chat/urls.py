from chat.views import ChatViewSet, MessageViewSet
from rest_framework.routers import DefaultRouter

chats_router = DefaultRouter()
chats_router.register(r'', ChatViewSet, basename='chats')
# chats_router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = chats_router.urls


