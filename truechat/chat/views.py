from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from chat.models import Chat, Message
from chat.serializers import ChatSerializer, ChatSerializerChange
from custom_auth.models import User


class IsChatMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user)


class IsChatAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creator


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action in ['add_member']:
            return Serializer
        if self.action in ['list', 'retrieve']:
            return ChatSerializer
        return ChatSerializerChange

    def get_permissions(self):
        permissions_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'add_member']:
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

    @action(detail=True, methods=['post'], url_path='add_member/(?P<username>[^/.]+)', url_name='add_member')
    def add_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            chat = Chat.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.is_member(user):
            return Response(data={"errors": ["User is already in the chat"]}, status=status.HTTP_409_CONFLICT)

        # TODO PERMISSION FIX
        if not chat.is_member(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        chat.users.add(user)
        chat.save()
        return Response(ChatSerializer(chat).data)

