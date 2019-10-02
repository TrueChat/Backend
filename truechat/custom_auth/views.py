from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from custom_auth.serializers import UserSerializer

User = get_user_model()


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class UserAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
        UserIsOwnerOrReadOnly,
    )
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
