from rest_framework.serializers import Serializer

from chat.models import Chat, Message
from rest_framework import serializers
from custom_auth.serializers import UserSerializerGet
from custom_auth.models import User


class ChatSerializer(serializers.ModelSerializer):
    """Chat room serialization"""
    creator = UserSerializerGet()
    users = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, instance):
        return MessageSerializer(instance.last_message).data if instance.last_message else Serializer(None).data

    def get_users(self, instance):
        users = []
        for member in instance.members.filter(is_banned=False):
            users.append(member.user)
        return UserSerializerGet(users, many=True).data

    class Meta:
        model = Chat
        fields = ("id", "name", "description", "creator", "users", "is_dialog", "date_created", "last_message")


class ChatSerializerChange(serializers.ModelSerializer):
    """Chat room serialization"""

    class Meta:
        model = Chat
        fields = ("id", "name", "description")


class MessageSerializer(serializers.ModelSerializer):
    chat = ChatSerializerChange()
    user = UserSerializerGet()

    class Meta:
        model = Message
        fields = ("id", "user", "content", "chat", 'date_created')


class MessageSerializerChange(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("id", "content")
