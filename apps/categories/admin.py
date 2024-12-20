from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from apps.categories.models import Category

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # editing an existing object
            fieldsets[0][1]['fields'] = tuple(
                f'{field}__{lang}' for lang, _ in self.get_language_tabs(request) for field in ('name', 'description')
            )
        return fieldsets
