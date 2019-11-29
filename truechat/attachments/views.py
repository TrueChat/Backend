from random import randint

from cloudinary import uploader
from cloudinary.templatetags import cloudinary
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from attachments.models import Image
from chat.models import Message, Chat
from custom_auth.models import User


class ImageMixin:

    @staticmethod
    def upload_image_cloudinary(file, image_name):
        uploader.upload(
            file,
            public_id=image_name,
        )

    @staticmethod
    def post_cloudinary(request, obj):
        print(request.FILES)
        for file in request.FILES.values():
            image_name = '{0}_v{1}'.format(file.name.split('.')[0],
                                           randint(1000, 9999))
            ImageMixin.upload_image_cloudinary(file=file, image_name=image_name)
            image_url = cloudinary.utils.cloudinary_url(image_name)[0]
            image = Image(name=image_name, imageURL=image_url, content_object=obj)
            image.save()

    def load_image_cloudinary(self, image: Image):
        print(image.imageURL)

    @staticmethod
    def can_change_photo(user, image):
        obj = image.content_object
        if obj.__class__ is Message:
            return obj.user == user
        elif obj.__class__ is Chat:
            return obj.creator == user
        elif obj.__class__ is User:
            return obj == user
        return False


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def message_destroy_image(request, pk=None):
    try:
        image = Image.objects.get(pk=pk)
    except Image.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = request.user
    if not ImageMixin.can_change_photo(user, image):
        return Response(status=status.HTTP_403_FORBIDDEN)
    image.delete()
    return Response(status=status.HTTP_200_OK)
