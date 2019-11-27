from django.contrib.auth import get_user_model
from rest_framework import serializers

from attachments.serializers import ImageFieldSerializer

User = get_user_model()


class UserSerializerChange(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'about', 'username']


class UserSerializerGet(serializers.ModelSerializer):
    images = ImageFieldSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'about', 'date_joined',
                  'last_login', 'images']
