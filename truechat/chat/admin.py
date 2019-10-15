from django.contrib import admin
from .models import Message, Chat


class MembershipInline(admin.StackedInline):
    model = Chat.users.through
    fields = ('user', 'is_admin')
    extra = 1


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'is_dialog', 'notifications')
    list_display = ('name', 'is_dialog')
    inlines = [MembershipInline, ]


admin.site.register(Message)
