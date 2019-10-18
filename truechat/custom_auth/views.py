from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from allauth.account.models import EmailConfirmationHMAC
import requests

from custom_auth.serializers import UserSerializerChange, UserSerializerGet

User = get_user_model()


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class UserAPIViewChange(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_object(self):
        return self.request.user

    def put(self, request, username=None):
        user = self.get_object()
        if username and user.username != username:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializerChange(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, username=None):
        user = self.get_object()
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializerGet(user)
        return Response(serializer.data)


def confirm_email(request, key):
    email_confirmation = EmailConfirmationHMAC.from_key(key)
    if email_confirmation:
        email_confirmation.confirm(request)
    return HttpResponseRedirect(reverse_lazy('api'))

