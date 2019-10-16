from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializerChange(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'about']


class UserSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'about', 'date_joined', 'last_login']
