from django.contrib import admin
from .models import Message, Chat


class MembershipInline(admin.TabularInline):
    model = Chat.users.through
    fields = ('user', 'is_banned')
    extra = 1


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'is_dialog', 'creator')
    list_display = ('name', 'is_dialog')
    inlines = [MembershipInline, ]


admin.site.register(Message)
