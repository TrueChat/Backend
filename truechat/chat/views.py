from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from chat.models import Chat, Message, Membership
from chat.serializers import ChatSerializer, ChatSerializerChange, MessageSerializer, MessageSerializerChange
from custom_auth.models import User


class IsNotBanned(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(user=request.user, chat=obj)
            if membership.is_banned:
                return False
        except Membership.DoesNotExist:
            pass
        return True


class IsChatGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_dialog


class IsChatMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(user=request.user, chat=obj)
            if membership.is_banned:
                return False
        except Membership.DoesNotExist:
            if obj.creator == request.user:
                return True
            return False

        return obj.is_member(request.user)


class IsChatAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creator


class IsMessageCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsMessageAvailable(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return IsChatMember.has_object_permission(obj.user, request, view, obj.chat)
        return request.user == obj.user


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action in ['add_member', 'ban_member', 'unban_member', 'messages', 'create_private_chat',
                           'get_private_chat']:
            return Serializer
        if self.action in ['list', 'retrieve']:
            return ChatSerializer
        if self.action in ['add_message']:
            return MessageSerializerChange
        return ChatSerializerChange

    def get_permissions(self):
        permissions_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'add_member', 'delete_member', 'add_message', 'messages']:
            permissions_classes += [IsChatMember]
        elif self.action not in ['list']:
            permissions_classes += [IsChatAdmin]
        if self.action not in ['retrieve', 'create_private_chat', 'list', 'messages', 'add_message', 'create',
                               'get_private_chat']:
            permissions_classes += [IsChatGroup]
        return [permission() for permission in permissions_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        chat = serializer(data=request.data)
        if chat.is_valid():
            chat.save(creator=request.user)
            return Response(chat.data)
        return Response(chat.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        membership = Membership.objects.filter(user=request.user, is_banned=False)
        chats = Chat.objects.filter(members__in=membership)
        queryset = chats.union(Chat.objects.filter(creator=request.user)).order_by('-date_created')
        page = self.paginate_queryset(queryset)
        if page is not None and request.GET.get('page') is not None:
            chats = serializer(page, many=True)
            return self.get_paginated_response(chats.data)
        chats = serializer(queryset, many=True)
        return Response(chats.data)

    @action(detail=True, methods=['post'], url_path='add_member/(?P<username>[^/.]+)', url_name='add_member')
    def add_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            chat = self.get_object()
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.is_member(user):
            return Response(data={"errors": ["User is already in the chat"]}, status=status.HTTP_409_CONFLICT)
        try:
            membership = Membership.objects.get(user=user, chat=chat)
            if membership.is_banned:
                return Response(data={"errors": ["User is not in the chat. User is banned."]},
                                status=status.HTTP_409_CONFLICT)
        except Membership.DoesNotExist:
            pass
        if chat.is_dialog:
            return Response(data={"errors": ["Chat is a dialog"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        chat.users.add(user)
        chat.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=['delete'], url_path='delete_member/(?P<username>[^/.]+)', url_name='del_member')
    def del_member(self, request, username, pk=None):
        """Creator can delete everyone"""
        try:
            user = User.objects.get(username=username)
            chat = self.get_object()
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.creator != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if chat.is_dialog:
            return Response(data={"errors": ["Chat is a dialog"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            membership = Membership.objects.get(user=user, chat=chat)
            if membership.is_banned:
                return Response(data={"errors": ["User is not in the chat. User is banned."]},
                                status=status.HTTP_409_CONFLICT)
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not chat.is_member(user):
            return Response(data={"errors": ["User is not in the chat"]}, status=status.HTTP_409_CONFLICT)
        if chat.creator == user:
            return Response(data={"errors": ["User is the owner of the chat. Chat may be deleted."]},
                            status=status.HTTP_409_CONFLICT)

        chat.users.remove(user)
        chat.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=['put'], url_path='ban_member/(?P<username>[^/.]+)', url_name='ban_member')
    def ban_member(self, request, username, pk=None):
        """Creator can ban everyone"""
        try:
            user = User.objects.get(username=username)
            chat = self.get_object()
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.creator != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if chat.is_dialog:
            return Response(data={"errors": ["Chat is a dialog"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if not chat.is_member(user):
            return Response(data={"errors": ["User is not in the chat"]}, status=status.HTTP_409_CONFLICT)
        if chat.creator == user:
            return Response(data={"errors": ["User is the owner of the chat"]},
                            status=status.HTTP_409_CONFLICT)
        membership = Membership.objects.get(user=user, chat=chat)
        membership.is_banned = True
        membership.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=['put'], url_path='unban_member/(?P<username>[^/.]+)', url_name='unban_member')
    def unban_member(self, request, username, pk=None):
        """Creator can unban everyone"""
        try:
            user = User.objects.get(username=username)
            chat = self.get_object()
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.creator != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if chat.is_dialog:
            return Response(data={"errors": ["Chat is a dialog"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if not chat.is_member(user):
            return Response(data={"errors": ["User is not in the chat"]}, status=status.HTTP_409_CONFLICT)
        if chat.creator == user:
            return Response(data={"errors": ["User is the owner of the chat"]},
                            status=status.HTTP_409_CONFLICT)
        membership = Membership.objects.get(user=user, chat=chat)
        membership.is_banned = False
        membership.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=['delete'])
    def delete_member(self, request, pk=None):
        """Delete current user from the given chat"""
        try:
            chat = self.get_object()
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if chat.is_dialog:
            return Response(data={"errors": ["Chat is a dialog"]}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if chat.creator == request.user:
            return Response(data={"errors": ["User is the owner of the chat. Chat may be deleted."]},
                            status=status.HTTP_409_CONFLICT)
        membership = Membership.objects.get(user=request.user, chat=chat)
        if membership.is_banned:
            return Response(data={"errors": ["User is not in the chat. User is banned."]},
                            status=status.HTTP_409_CONFLICT)

        chat.users.remove(request.user)
        chat.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=['post'], url_path='add_message')
    def add_message(self, request, pk=None):
        user = request.user
        try:
            chat = self.get_object()
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        message = MessageSerializerChange(data=request.data)
        if message.is_valid():
            valid_data = message.validated_data
            content = valid_data.get('content')
            new_message = Message(content=content, user=request.user, chat=chat)
            new_message.save()
            return Response(MessageSerializer(new_message).data)
        return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        try:
            chat = self.get_object()
        except Chat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset = chat.messages.all()
        page = self.paginate_queryset(queryset)
        if page is not None and request.GET.get('page') is not None:
            return self.get_paginated_response(MessageSerializer(page, many=True).data)

        return Response(MessageSerializer(queryset, many=True).data)

    @action(detail=False, methods=['post', 'get'], url_path='private_chats/(?P<username>[^/.]+)',
            url_name='create_private_chat')
    def create_private_chat(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        us1 = username
        us2 = request.user.username
        chats = Chat.objects.filter(Q(name=f'{us1}-{us2}') | Q(name=f'{us1}-{us2}') & Q(is_dialog=True))
        if chats.exists():
            if request.method == 'POST':
                return Response(
                    data={"errors": ["Chat is already existed"], "data": ChatSerializer(chats, many=True).data},
                    status=status.HTTP_409_CONFLICT)
            elif request.method == 'GET':
                return Response(ChatSerializer(chats, many=True).data)
        if request.method == 'POST':
            chat = Chat.objects.create(name=f'{us1}-{us2}', creator=request.user, is_dialog=True)
            chat.users.add(user)
            chat.save()
            return Response(ChatSerializer(chat).data)
        elif request.method == 'GET':
            return Response(status=status.HTTP_404_NOT_FOUND)


class MessageAPIView(RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MessageSerializer
        return MessageSerializerChange

    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsMessageAvailable]
