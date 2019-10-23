from chat.models import Chat, Message
from rest_framework import serializers
from custom_auth.serializers import UserSerializerGet


class ChatSerializer(serializers.ModelSerializer):
    """Chat room serialization"""
    creator = UserSerializerGet()
    users = UserSerializerGet(many=True)

    class Meta:
        model = Chat
        fields = ("id", "name", "description", "creator", "users", "is_dialog", "date_created")


class ChatSerializerChange(serializers.ModelSerializer):
    """Chat room serialization"""

    class Meta:
        model = Chat
        fields = ("name", "description")
