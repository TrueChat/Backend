from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from chat.models import Chat, Message
from chat.serializers import ChatSerializer, ChatSerializerChange
from django.db.models import Q


class IsChatMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all() or request.user == obj.creator


class IsChatAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creator


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ChatSerializer
        return ChatSerializerChange

    def get_permissions(self):
        permissions_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve']:
            permissions_classes += [IsChatMember]
        elif self.action not in ['list']:
            permissions_classes += [IsChatAdmin]
        return [permission() for permission in permissions_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        chat = serializer(data=request.data)
        if chat.is_valid():
            chat.save(creator=request.user)
            return Response(chat.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        queryset = request.user.chats.union(Chat.objects.filter(creator=request.user))
        chats = serializer(queryset, many=True)
        return Response(chats.data)


