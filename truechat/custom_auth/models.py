from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from attachments.models import Image


class User(AbstractUser):
    about = models.CharField('О себе', max_length=1023, null=True, blank=True)
    images = GenericRelation(Image)

    class Meta:
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
