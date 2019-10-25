from chat.views import ChatViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ChatViewSet, basename='chats')

urlpatterns = router.urls


