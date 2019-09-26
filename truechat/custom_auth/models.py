from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    about = models.CharField('О себе', max_length=1023, null=True, blank=True)

    class Meta:
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
