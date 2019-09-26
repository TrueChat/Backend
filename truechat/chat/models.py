from custom_auth.models import User
from django.db import models
from django.utils import timezone


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название чата', max_length=255,
                            help_text='Название чата может быть максимум в 255 символов')
    description = models.CharField('Название чата', max_length=1023,
                                   help_text='Описание чата может быть максимум в 1023 символов', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Создатель',
                                related_name='created_chats', null=True)
    is_dialog = models.BooleanField('Личная ли переписка', default=False)
    notifications = models.BooleanField('Присылать ли нотификации', default=True,
                                        help_text='Будут ли появляться на телефоне нотификации о сообщении')
    users = models.ManyToManyField(User, related_name='chats')
    date_created = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        db_table = 'chats'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name='чат', related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Создатель',
                             related_name='messages', null=True)
    content = models.CharField('Содержание письма', max_length=4095,
                               help_text='Содержание письма может быть максимум в 4095 символов')
    date_created = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class MessageStatus(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='сообщение',
                                related_name='message_statuses')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Получатель',
                             related_name='message_statuses', null=True)
    is_read = models.BooleanField('Прочитано ли', default=False)

    class Meta:
        db_table = 'message_statuses'
        verbose_name = 'Статус сообщения'
        verbose_name_plural = 'Статусы сообщений'
