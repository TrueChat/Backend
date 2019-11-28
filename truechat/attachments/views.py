from random import randint

from cloudinary import uploader
from cloudinary.templatetags import cloudinary

from attachments.models import Image


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
