from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title_preview', 'user', 'article', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'user']
    search_fields = ['title', 'message', 'user__username', 'user__full_name', 'article__title']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def title_preview(self, obj):
        if len(obj.title) > 50:
            return obj.title[:50] + "..."
        return obj.title

    title_preview.short_description = _("Sarlavha")

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, _("Tanlangan bildirishnomalar o'qilgan deb belgilandi"))

    mark_as_read.short_description = _("O'qilgan deb belgilash")

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, _("Tanlangan bildirishnomalar o'qilmagan deb belgilandi"))

    mark_as_unread.short_description = _("O'qilmagan deb belgilash")