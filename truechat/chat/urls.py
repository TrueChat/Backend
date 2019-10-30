from chat.views import ChatViewSet
from rest_framework.routers import DefaultRouter

chats_router = DefaultRouter()
chats_router.register(r'', ChatViewSet, basename='chats')

urlpatterns = chats_router.urls


