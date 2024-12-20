from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'submission_date', 'is_published')
    list_filter = ('status', 'category', 'submission_date', 'publication_date')
    search_fields = ('title', 'keywords', 'authors__first_name', 'authors__last_name')
    readonly_fields = ('views_count', 'downloads_count', 'submission_date', 'last_updated')
    filter_horizontal = ('authors',)
    fieldsets = (
        (_('Article Information'), {
            'fields': ('title', 'category', 'keywords', 'annotation', 'authors')
        }),
        (_('Files'), {
            'fields': ('original_file', 'revised_file')
        }),
        (_('Page Information'), {
            'fields': ('start_page', 'end_page')
        }),
        (_('Statistics'), {
            'fields': ('views_count', 'downloads_count')
        }),
        (_('Status and Dates'), {
            'fields': ('status', 'submission_date', 'review_date', 'acceptance_date', 'publication_date', 'last_updated')
        }),
        (_('Journal'), {
            'fields': ('journal_issue',)
        }),
    )

    def is_published(self, obj):
        return obj.is_published
    is_published.boolean = True
    is_published.short_description = _('Published')

admin.site.register(Article, ArticleAdmin)
