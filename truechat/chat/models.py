from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from custom_auth.models import User
from attachments.models import ImageField


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название чата', max_length=255,
                            help_text='Название чата может быть максимум в 255 символов')
    description = models.CharField('Описание чата', max_length=1023,
                                   help_text='Описание чата может быть максимум в 1023 символов',
                                   null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Создатель',
                                related_name='created_chats', null=True)
    is_dialog = models.BooleanField('Личная ли переписка', default=False)
    users = models.ManyToManyField(User, related_name='chats', through='Membership')
    date_created = models.DateTimeField('Дата создания', default=timezone.now)
    images = GenericRelation(ImageField)

    def is_member(self, user):
        return self.members.filter(user=user).exists() or self.creator == user

    @property
    def last_message(self):
        messages = self.messages.order_by('-date_created')
        return messages.first() if len(messages) else None

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'chats'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Участник',
                             related_name='memberships')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name='Чат',
                             related_name='members')
    is_banned = models.BooleanField('Забанен ли?', default=False)
    date_started = models.DateTimeField('Дата начала общения в чате', default=timezone.now)
    notifications = models.BooleanField('Присылать ли нотификации', default=True,
                                        help_text='Будут ли появляться на телефоне нотификации о сообщении')

    def __str__(self):
        return f'{self.user}({self.chat})'

    class Meta:
        db_table = 'Membership'
        unique_together = ['chat', 'user']
        ordering = ['-date_started']


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name='чат',
                             related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Создатель',
                             related_name='messages', null=True)
    content = models.CharField('Содержание письма', max_length=4095,
                               help_text='Содержание письма может быть максимум в 4095 символов')
    date_created = models.DateTimeField('Дата создания', default=timezone.now)
    images = GenericRelation(ImageField)

    def __str__(self):
        return f'{self.chat.name}.{self.user.username} - {self.date_created}'

    class Meta:
        db_table = 'messages'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-date_created']


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
