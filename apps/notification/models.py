from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Notification(models.Model):
    """
    Bildirishnomalar modeli
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Foydalanuvchi')
    )
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name=_('Maqola')
    )
    title = models.CharField(_('Sarlavha'), max_length=255)
    message = models.TextField(_('Xabar'))
    is_read = models.BooleanField(_('O\'qilgan'), default=False)
    created_at = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Bildirishnoma')
        verbose_name_plural = _('Bildirishnomalar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @classmethod
    def notify_user(cls, user, article, title, message):
        """
        Foydalanuvchiga bildirishnoma yuborish
        """
        return cls.objects.create(
            user=user,
            article=article,
            title=title,
            message=message
        )

    @classmethod
    def notify_author(cls, article, title, message):
        """
        Maqola muallifiga bildirishnoma yuborish
        """
        return cls.notify_user(article.author, article, title, message)

    @classmethod
    def notify_secretary(cls, article, title, message):
        """
        Mas'ul kotibga bildirishnoma yuborish
        """
        # Barcha mas'ul kotiblarga bildirishnoma yuborish
        if article.secretary:
            return cls.notify_user(article.secretary, article, title, message)
        else:
            # Agar maqolaga mas'ul kotib tayinlanmagan bo'lsa, barcha mas'ul kotiblarga yuborish
            secretaries = User.objects.filter(role=User.Role.SECRETARY)
            notifications = []
            for secretary in secretaries:
                notifications.append(
                    cls.notify_user(secretary, article, title, message)
                )
            return notifications

    @classmethod
    def notify_reviewer(cls, article, title, message):
        """
        Taqrizchiga bildirishnoma yuborish
        """
        if article.reviewer:
            return cls.notify_user(article.reviewer, article, title, message)
        return None

    @classmethod
    def notify_editor(cls, article, title, message):
        """
        Muharrirga bildirishnoma yuborish
        """
        if article.editor:
            return cls.notify_user(article.editor, article, title, message)
        return None

    @classmethod
    def notify_deputy(cls, article, title, message):
        """
        Bosh muharrir o'rinbosariga bildirishnoma yuborish
        """
        if article.deputy_chief:
            return cls.notify_user(article.deputy_chief, article, title, message)
        return None
