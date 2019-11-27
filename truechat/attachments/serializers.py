from rest_framework import serializers

from attachments.models import ImageField


class ImageFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageField
        fields = ['name']
