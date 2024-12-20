from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import JournalVolume, JournalIssue, Journal
from ..articles.models import Article


class JournalVolumeInline(admin.TabularInline):
    model = JournalVolume
    extra = 1

class JournalAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [JournalVolumeInline]

admin.site.register(Journal, JournalAdmin)

class JournalIssueInline(admin.TabularInline):
    model = JournalIssue
    extra = 1

class JournalVolumeAdmin(admin.ModelAdmin):
    list_display = ('journal', 'volume_number', 'year', 'created_at')
    list_filter = ('journal', 'year')
    search_fields = ('journal__name', 'volume_number')
    inlines = [JournalIssueInline]

admin.site.register(JournalVolume, JournalVolumeAdmin)

class ArticleInline(admin.TabularInline):
    model = Article
    extra = 1
    fields = ('title', 'status', 'start_page', 'end_page')
    readonly_fields = ('status',)

class JournalIssueAdmin(admin.ModelAdmin):
    list_display = ('volume', 'issue_number', 'publication_date', 'is_published', 'views_count')
    list_filter = ('is_published', 'publication_date', 'volume__journal')
    search_fields = ('volume__journal__name', 'issue_number')
    readonly_fields = ('views_count',)
    inlines = [ArticleInline]
    fieldsets = (
        (_('Issue Information'), {
            'fields': ('volume', 'issue_number', 'publication_date', 'is_published')
        }),
        (_('Files'), {
            'fields': ('image', 'journal_file')
        }),
        (_('Page Information'), {
            'fields': ('start_page', 'end_page')
        }),
        (_('Statistics'), {
            'fields': ('views_count',)
        }),
    )

admin.site.register(JournalIssue, JournalIssueAdmin)
