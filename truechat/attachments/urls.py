from django.urls import path

from attachments.views import message_destroy_image

urlpatterns = [
    path(r'<int:pk>/delete_image/', message_destroy_image)
]
