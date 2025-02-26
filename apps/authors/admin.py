from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.authors.models import Author


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'academic_degree', 'academic_title')
    list_filter = ('academic_degree', 'academic_title', 'country')
    search_fields = ('last_name', 'first_name', 'email', 'orcid')
    fieldsets = (
        (_('User profile'), {
            'fields': ('user',)
        }),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'country', 'city')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'telegram_contact', 'whatsapp_contact')
        }),
        (_('Academic Information'), {
            'fields': ('workplace', 'level', 'academic_degree', 'academic_title', 'orcid')
        }),
    )

admin.site.register(Author, AuthorAdmin)
