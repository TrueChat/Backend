from rest_framework import serializers

from attachments.models import Image


class ImageFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['pk', 'name', 'imageURL']
        read_only_fields = ['date_created']
