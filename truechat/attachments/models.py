import cloudinary
from cloudinary.models import CloudinaryField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class Image(models.Model):
    name = models.CharField('Название картинки', max_length=255,
                            help_text='Название картинки может быть максимум в 255 символов',
                            blank=True)
    imageURL = models.CharField(max_length=100, verbose_name='Image URL')
    imageFile = CloudinaryField('ImageFile')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date_created = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        cloudinary.uploader.destroy(self.name)
        super(Image, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'Picture'
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинка'
        ordering = ['-date_created']
