from django.urls import path

from chat.views import MessageAPIView, message_upload_image

urlpatterns = [
    path(r'<int:pk>/', MessageAPIView.as_view()),
    path(r'<int:pk>/upload_photo/', message_upload_image)
]
