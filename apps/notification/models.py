from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.articles.models import Article

User = get_user_model()


class Notification(models.Model):
    """Bildirishnoma modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                             verbose_name=_('Foydalanuvchi'))
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='notifications',
                                verbose_name=_('Maqola'), null=True, blank=True)

    title = models.CharField(_('Sarlavha'), max_length=255)
    message = models.TextField(_('Xabar'))

    is_read = models.BooleanField(_('O\'qilgan'), default=False)
    created_at = models.DateTimeField(_('Sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Bildirishnoma')
        verbose_name_plural = _('Bildirishnomalar')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @classmethod
    def notify_author(cls, article, title, message):
        """Muallifga bildirishnoma yuborish"""
        return cls.objects.create(
            user=article.author,
            article=article,
            title=title,
            message=message
        )

    @classmethod
    def notify_secretary(cls, article, title, message):
        """Mas'ul kotibga bildirishnoma yuborish"""
        if article.secretary:
            return cls.objects.create(
                user=article.secretary,
                article=article,
                title=title,
                message=message
            )
        return None

    @classmethod
    def notify_reviewer(cls, article, title, message):
        """Taqrizchiga bildirishnoma yuborish"""
        if article.reviewer:
            return cls.objects.create(
                user=article.reviewer,
                article=article,
                title=title,
                message=message
            )
        return None

    @classmethod
    def notify_editor(cls, article, title, message):
        """Muharrirga bildirishnoma yuborish"""
        if article.editor:
            return cls.objects.create(
                user=article.editor,
                article=article,
                title=title,
                message=message
            )
        return None

    @classmethod
    def notify_deputy(cls, article, title, message):
        """Bosh muharrir o'rinbosariga bildirishnoma yuborish"""
        if article.deputy_chief:
            return cls.objects.create(
                user=article.deputy_chief,
                article=article,
                title=title,
                message=message
            )
        return None
