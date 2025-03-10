from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count

from .models import Article, ArticleHistory, Comment


class ArticleHistoryInline(admin.TabularInline):
    model = ArticleHistory
    extra = 0
    readonly_fields = ['user', 'old_status', 'new_status', 'comment', 'file', 'created_at']
    can_delete = False
    max_num = 0
    verbose_name = _("Maqola tarixi")
    verbose_name_plural = _("Maqola tarixi")

    def has_add_permission(self, request, obj=None):
        return False


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['user', 'text', 'file', 'created_at']
    can_delete = False
    max_num = 0
    verbose_name = _("Izoh")
    verbose_name_plural = _("Izohlar")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author_name', 'category', 'status_display',
        'submission_date', 'review_stage', 'has_reviews'
    ]
    list_filter = [
        'status', 'category', 'submission_date', 'publication_date',
        'author', 'secretary', 'reviewer', 'editor', 'deputy_chief'
    ]
    search_fields = ['title', 'keywords', 'annotation', 'author__username', 'author__full_name']
    readonly_fields = [
        'slug', 'submission_date', 'revision_requested_date',
        'acceptance_date', 'publication_date', 'last_updated', 'views_count',
        'downloads_count'
    ]
    fieldsets = (
        (_('Asosiy ma\'lumotlar'), {
            'fields': (
                'title', 'slug', 'category', 'keywords',
                'annotation', 'references', 'authors'
            )
        }),
        (_('Fayllar'), {
            'fields': (
                'original_file', 'revised_file', 'anti_plagiarism_certificate'
            )
        }),
        (_('Holat va sanalar'), {
            'fields': (
                'status', 'submission_date', 'revision_requested_date',
                'acceptance_date', 'publication_date', 'last_updated'
            )
        }),
        (_('Tayinlangan foydalanuvchilar'), {
            'fields': (
                'author', 'secretary', 'reviewer', 'editor', 'deputy_chief'
            )
        }),
        (_('Jurnal ma\'lumotlari'), {
            'fields': (
                'journal_issue', 'start_page', 'end_page'
            )
        }),
        (_('Statistika'), {
            'fields': (
                'views_count', 'downloads_count'
            )
        }),
    )
    inlines = [ArticleHistoryInline, CommentInline]
    actions = ['increment_view_count', 'increment_download_count']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(reviews_count=Count('reviews'))
        return queryset

    def author_name(self, obj):
        if obj.author:
            return obj.author.full_name
        return "-"

    author_name.short_description = _("Muallif")

    def status_display(self, obj):
        status_colors = {
            'SUBMITTED': 'info',
            'SECRETARY_REVIEW': 'primary',
            'REVIEWER_REVIEW': 'primary',
            'EDITOR_REVIEW': 'primary',
            'DEPUTY_REVIEW': 'primary',
            'REVISION_REQUESTED': 'warning',
            'ACCEPTED': 'success',
            'REJECTED': 'danger',
            'PUBLISHED': 'success',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )

    status_display.short_description = _("Holat")

    def review_stage(self, obj):
        if obj.status == 'SECRETARY_REVIEW':
            return _("Mas'ul kotib")
        elif obj.status == 'REVIEWER_REVIEW':
            return _("Taqrizchi")
        elif obj.status == 'EDITOR_REVIEW':
            return _("Muharrir")
        elif obj.status == 'DEPUTY_REVIEW':
            return _("Bosh muharrir o'rinbosari")
        return "-"

    review_stage.short_description = _("Tekshiruv bosqichi")

    def has_reviews(self, obj):
        return obj.reviews_count > 0

    has_reviews.boolean = True
    has_reviews.short_description = _("Taqrizlar")

    def increment_view_count(self, request, queryset):
        for article in queryset:
            article.increment_view_count()
        self.message_user(request, _("Ko'rishlar soni oshirildi"))

    increment_view_count.short_description = _("Ko'rishlar sonini oshirish")

    def increment_download_count(self, request, queryset):
        for article in queryset:
            article.increment_download_count()
        self.message_user(request, _("Yuklab olishlar soni oshirildi"))

    increment_download_count.short_description = _("Yuklab olishlar sonini oshirish")


@admin.register(ArticleHistory)
class ArticleHistoryAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'old_status_display', 'new_status_display', 'created_at']
    list_filter = ['new_status', 'created_at', 'user']
    search_fields = ['article__title', 'user__username', 'user__full_name', 'comment']
    readonly_fields = ['article', 'user', 'old_status', 'new_status', 'comment', 'file', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def old_status_display(self, obj):
        if not obj.old_status:
            return "-"
        for status, display in Article.STATUS_CHOICES:
            if status == obj.old_status:
                return display
        return obj.old_status

    old_status_display.short_description = _("Oldingi holat")

    def new_status_display(self, obj):
        for status, display in Article.STATUS_CHOICES:
            if status == obj.new_status:
                return display
        return obj.new_status

    new_status_display.short_description = _("Yangi holat")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'text_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['article__title', 'user__username', 'user__full_name', 'text']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text

    text_preview.short_description = _("Matn")
