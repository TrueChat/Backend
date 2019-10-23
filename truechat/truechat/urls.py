from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, re_path
from rest_framework_swagger.views import get_swagger_view

from custom_auth.views import UserAPIViewChange, confirm_email

schema_view = get_swagger_view(title='TrueChat API')

urlpatterns = [
    url(r'^$', schema_view, name='api'),
    url(r'^rest-auth/', include('rest_auth.urls')),


    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', confirm_email, name='password_reset_confirm'),
    # after registration user is sent to this url for email confirming
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        confirm_email,
        name='account_confirm_email'),
    url(r'^rest-auth/registration/account-confirm-email/',
        confirm_email,
        name='account_email_verification_sent'),

    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'profile/(?P<username>\w+|)', UserAPIViewChange.as_view()),

    re_path(r'chats/', include('chat.urls')),
    path('admin/', admin.site.urls)
]
