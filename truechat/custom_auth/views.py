from allauth.account.models import EmailConfirmationHMAC
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from custom_auth.models import User
from custom_auth.serializers import UserSerializerChange, UserSerializerGet


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


class UserListView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, search_string=None):
        query = SearchQuery(search_string)

        username_vector = SearchVector('username', weight='A')
        first_name_vector = SearchVector('first_name', weight='B')
        last_name_vector = SearchVector('last_name', weight='B')
        email_vector = SearchVector('email', weight='B')
        about_vector = SearchVector('about', weight='C')
        vectors = username_vector + first_name_vector + last_name_vector + email_vector + about_vector
        qs = User.objects
        qs = qs.annotate(search=vectors).filter(search=query)
        qs = qs.annotate(rank=SearchRank(vectors, query)).order_by('-rank')
        print(qs)
        return Response(UserSerializerGet(qs, many=True).data)


def confirm_email(request, key):
    email_confirmation = EmailConfirmationHMAC.from_key(key)
    if email_confirmation:
        email_confirmation.confirm(request)
    return HttpResponseRedirect('http://truechat-client.herokuapp.com/auth')
