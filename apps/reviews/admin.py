from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'article', 'reviewer_name', 'recommendation_display',
        'average_score_display', 'is_anonymous', 'created_at'
    ]
    list_filter = ['recommendation', 'is_anonymous', 'created_at', 'reviewer']
    search_fields = ['article__title', 'reviewer__username', 'reviewer__full_name', 'comments_to_author',
                     'comments_to_editor']
    readonly_fields = ['created_at', 'updated_at', 'average_score']
    fieldsets = (
        (_('Asosiy ma\'lumotlar'), {
            'fields': ('article', 'reviewer', 'is_anonymous')
        }),
        (_('Baholash'), {
            'fields': (
                'scientific_value', 'methodology', 'practical_value',
                'novelty', 'average_score'
            )
        }),
        (_('Tavsiya va izohlar'), {
            'fields': (
                'recommendation', 'comments_to_author', 'comments_to_editor', 'review_file'
            )
        }),
        (_('Sanalar'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.full_name
        return "-"

    reviewer_name.short_description = _("Taqrizchi")

    def recommendation_display(self, obj):
        recommendation_colors = {
            'ACCEPT': 'success',
            'MINOR_REVISION': 'info',
            'MAJOR_REVISION': 'warning',
            'REJECT': 'danger',
        }
        color = recommendation_colors.get(obj.recommendation, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_recommendation_display()
        )

    recommendation_display.short_description = _("Tavsiya")

    def average_score_display(self, obj):
        avg_score = obj.average_score
        if avg_score is None:
            return format_html('<span class="badge badge-secondary">{}</span>', _("Noma'lum"))

        if avg_score >= 4.5:
            color = 'success'
        elif avg_score >= 3.5:
            color = 'info'
        elif avg_score >= 2.5:
            color = 'warning'
        else:
            color = 'danger'

        return format_html(
            '<span class="badge badge-{}">{:.1f}</span>',
            color, avg_score
        )

    average_score_display.short_description = _("O'rtacha ball")
