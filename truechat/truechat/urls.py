from django.conf.urls import url, include
from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from custom_auth.views import UserAPIView

schema_view = get_swagger_view(title='TrueChat API')

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    path('profile/<pk>/', UserAPIView.as_view()),
]
