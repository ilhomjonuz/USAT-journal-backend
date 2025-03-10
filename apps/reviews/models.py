from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.articles.models import Article

User = get_user_model()


class Review(models.Model):
    """Taqriz modeli"""
    RECOMMENDATION_CHOICES = [
        ('ACCEPT', _('Qabul qilish')),
        ('MINOR_REVISION', _('Kichik tahrir talab qilinadi')),
        ('MAJOR_REVISION', _('Katta tahrir talab qilinadi')),
        ('REJECT', _('Rad etish')),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Maqola'))
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews',
                                 verbose_name=_('Taqrizchi'))

    # Baholash
    scientific_value = models.PositiveSmallIntegerField(_('Ilmiy qiymati'), choices=[(i, str(i)) for i in range(1, 6)])
    methodology = models.PositiveSmallIntegerField(_('Metodologiyasi'), choices=[(i, str(i)) for i in range(1, 6)])
    practical_value = models.PositiveSmallIntegerField(_('Amaliy ahamiyati'),
                                                       choices=[(i, str(i)) for i in range(1, 6)])
    novelty = models.PositiveSmallIntegerField(_('Yangiligi'), choices=[(i, str(i)) for i in range(1, 6)])

    # Tavsiya va izohlar
    recommendation = models.CharField(_('Tavsiya'), max_length=20, choices=RECOMMENDATION_CHOICES)
    comments_to_author = models.TextField(_('Muallif uchun izohlar'), null=True, blank=True)
    comments_to_editor = models.TextField(_('Muharrir uchun izohlar'), null=True, blank=True)

    # Qo'shimcha ma'lumotlar
    review_file = models.FileField(_('Taqriz fayli'), upload_to='reviews/', null=True, blank=True)
    is_anonymous = models.BooleanField(_('Anonim taqriz'), default=True)

    # Sanalar
    created_at = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yangilangan sana'), auto_now=True)

    class Meta:
        verbose_name = _('Taqriz')
        verbose_name_plural = _('Taqrizlar')
        ordering = ['-created_at']
        unique_together = ['article', 'reviewer']

    def __str__(self):
        return f"{self.article.title} - {self.reviewer.full_name}"

    @property
    def average_score(self):
        """O'rtacha ball"""
        scores = [
            self.scientific_value,
            self.methodology,
            self.practical_value,
            self.novelty
        ]

        # `None` bo'lgan qiymatlarni filtrlaymiz
        valid_scores = [score for score in scores if score is not None]

        # Agar hammasi `None` bo'lsa, `None` qaytaradi
        if not valid_scores:
            return None

        # O'rtacha ballni hisoblaymiz
        return sum(valid_scores) / len(valid_scores)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Yangi taqriz yaratilganda maqola holatini yangilash
        if is_new and self.article.status == 'REVIEWER_REVIEW':
            # Taqrizchi tavsiyasiga qarab maqola holatini o'zgartirish
            is_approved = self.recommendation in ['ACCEPT', 'MINOR_REVISION']
            self.article.reviewer_decision(
                reviewer=self.reviewer,
                is_approved=is_approved,
                comment=f'Taqrizchi xulosasi: {self.get_recommendation_display()}',
                file=self.review_file if self.review_file else None  # Agar fayl mavjud bo'lsa
            )
