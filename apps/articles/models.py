from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()


def article_file_path(instance, filename):
    """Generate file path for article files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('articles', str(instance.id), filename)


class Article(models.Model):
    """
    Maqola modeli
    """
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_SECRETARY_REVIEW = 'SECRETARY_REVIEW'
    STATUS_REVIEWER_REVIEW = 'REVIEWER_REVIEW'
    STATUS_EDITOR_REVIEW = 'EDITOR_REVIEW'
    STATUS_DEPUTY_REVIEW = 'DEPUTY_REVIEW'
    STATUS_REVISION_REQUESTED = 'REVISION_REQUESTED'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_PUBLISHED = 'PUBLISHED'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, _('Yuborilgan')),
        (STATUS_SECRETARY_REVIEW, _('Mas\'ul kotib tekshiruvida')),
        (STATUS_REVIEWER_REVIEW, _('Taqrizchi tekshiruvida')),
        (STATUS_EDITOR_REVIEW, _('Muharrir tekshiruvida')),
        (STATUS_DEPUTY_REVIEW, _('Bosh muharrir o\'rinbosari tekshiruvida')),
        (STATUS_REVISION_REQUESTED, _('Tahrir uchun qaytarilgan')),
        (STATUS_ACCEPTED, _('Qabul qilingan')),
        (STATUS_REJECTED, _('Rad etilgan')),
        (STATUS_PUBLISHED, _('Chop etilgan')),
    ]

    title = models.CharField(_('Sarlavha'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True, blank=True)
    keywords = models.CharField(_('Kalit so\'zlar'), max_length=255)
    annotation = models.TextField(_('Annotatsiya'))
    references = models.TextField(_('Adabiyotlar ro\'yxati'), blank=True, null=True)

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name=_('Kategoriya')
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_articles',
        verbose_name=_('Muallif')
    )
    authors = models.ManyToManyField(
        'authors.Author',
        related_name='articles',
        verbose_name=_('Mualliflar')
    )

    secretary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secretary_articles',
        verbose_name=_('Mas\'ul kotib')
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewer_articles',
        verbose_name=_('Taqrizchi')
    )

    editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='editor_articles',
        verbose_name=_('Muharrir')
    )

    deputy_chief = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deputy_articles',
        verbose_name=_('Bosh muharrir o\'rinbosari')
    )

    status = models.CharField(
        _('Holat'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )

    original_file = models.FileField(
        _('Asl fayl'),
        upload_to=article_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'odt'])]
    )

    revised_file = models.FileField(
        _('Tahrirlangan fayl'),
        upload_to=article_file_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    anti_plagiarism_certificate = models.FileField(
        _('Antiplagiat sertifikati'),
        upload_to=article_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    submission_date = models.DateTimeField(_('Yuborilgan sana'), auto_now_add=True)
    last_updated = models.DateTimeField(_('So\'nggi yangilanish'), auto_now=True)
    revision_requested_date = models.DateTimeField(_('Tahrir so\'ralgan sana'), null=True, blank=True)
    acceptance_date = models.DateTimeField(_('Qabul qilingan sana'), null=True, blank=True)
    publication_date = models.DateTimeField(_('Chop etilgan sana'), null=True, blank=True)

    journal_issue = models.ForeignKey(
        'journals.JournalIssue',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_('Jurnal soni')
    )

    start_page = models.PositiveIntegerField(_('Boshlanish sahifasi'), null=True, blank=True)
    end_page = models.PositiveIntegerField(_('Tugash sahifasi'), null=True, blank=True)

    views_count = models.PositiveIntegerField(_('Ko\'rishlar soni'), default=0)
    downloads_count = models.PositiveIntegerField(_('Yuklab olishlar soni'), default=0)

    class Meta:
        verbose_name = _('Maqola')
        verbose_name_plural = _('Maqolalar')
        ordering = ['-submission_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

            # Ensure slug is unique
            counter = 1
            original_slug = self.slug
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def assign_secretary(self, secretary):
        """
        Mas'ul kotib tayinlash
        """
        old_status = self.status
        self.secretary = secretary
        self.status = self.STATUS_SECRETARY_REVIEW
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status=self.STATUS_SECRETARY_REVIEW,
            comment=f'Mas\'ul kotib tayinlandi'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_secretary(
            self,
            _("Sizga yangi maqola tayinlandi"),
            _(f"Sizga yangi maqola tayinlandi: {self.title}")
        )

        return self

    def assign_reviewer(self, secretary, reviewer):
        """
        Taqrizchi tayinlash
        """
        old_status = self.status
        self.reviewer = reviewer
        self.status = self.STATUS_REVIEWER_REVIEW
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status=self.STATUS_REVIEWER_REVIEW,
            comment=f'Taqrizchi tayinlandi'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_reviewer(
            self,
            _("Sizga yangi maqola tayinlandi"),
            _(f"Sizga yangi maqola tayinlandi: {self.title}")
        )

        return self

    def assign_editor(self, secretary, editor):
        """
        Muharrir tayinlash
        """
        old_status = self.status
        self.editor = editor
        self.status = self.STATUS_EDITOR_REVIEW
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status=self.STATUS_EDITOR_REVIEW,
            comment=f'Muharrir tayinlandi'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_editor(
            self,
            _("Sizga yangi maqola tayinlandi"),
            _(f"Sizga yangi maqola tayinlandi: {self.title}")
        )

        return self

    def secretary_request_revision(self, secretary, comment, file=None):
        """
        Mas'ul kotib tahrir talab qilishi
        """
        old_status = self.status
        self.status = self.STATUS_REVISION_REQUESTED
        self.revision_requested_date = timezone.now()
        self.save()

        # Tarix yozuvini yaratish
        history = ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status=self.STATUS_REVISION_REQUESTED,
            comment=comment,
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_author(
            self,
            _("Maqolangiz tahrir uchun qaytarildi"),
            _(f"Maqolangiz tahrir uchun qaytarildi: {self.title}")
        )

        return self

    def secretary_reject(self, secretary, comment):
        """
        Mas'ul kotib rad etishi
        """
        old_status = self.status
        self.status = self.STATUS_REJECTED
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status=self.STATUS_REJECTED,
            comment=comment
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_author(
            self,
            _("Maqolangiz rad etildi"),
            _(f"Maqolangiz rad etildi: {self.title}")
        )

        return self

    def submit_revision(self, author, revised_file, comment=''):
        """
        Tahrirlangan maqolani yuborish
        """
        old_status = self.status
        self.revised_file = revised_file

        # Agar taqrizchi tayinlangan bo'lsa, taqrizchiga yuborish
        if self.reviewer:
            self.status = self.STATUS_REVIEWER_REVIEW
        # Agar muharrir tayinlangan bo'lsa, muharrirga yuborish
        elif self.editor:
            self.status = self.STATUS_EDITOR_REVIEW
        # Aks holda mas'ul kotibga yuborish
        else:
            self.status = self.STATUS_SECRETARY_REVIEW

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=author,
            old_status=old_status,
            new_status=self.status,
            comment=comment or _('Tahrirlangan maqola yuborildi'),
            file=revised_file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification

        # Mas'ul kotibga bildirishnoma yuborish
        Notification.notify_secretary(
            self,
            _("Tahrirlangan maqola yuborildi"),
            _(f"Tahrirlangan maqola yuborildi: {self.title}")
        )

        # Agar taqrizchi tayinlangan bo'lsa, taqrizchiga bildirishnoma yuborish
        if self.reviewer and self.status == self.STATUS_REVIEWER_REVIEW:
            Notification.notify_reviewer(
                self,
                _("Tahrirlangan maqola yuborildi"),
                _(f"Tahrirlangan maqola yuborildi: {self.title}")
            )

        # Agar muharrir tayinlangan bo'lsa, muharrirga bildirishnoma yuborish
        if self.editor and self.status == self.STATUS_EDITOR_REVIEW:
            Notification.notify_editor(
                self,
                _("Tahrirlangan maqola yuborildi"),
                _(f"Tahrirlangan maqola yuborildi: {self.title}")
            )

        return self

    def reviewer_decision(self, reviewer, is_approved, comment, file=None):
        """
        Taqrizchi qarori
        """
        old_status = self.status

        if is_approved:
            # Agar muharrir tayinlangan bo'lsa, muharrirga yuborish
            if self.editor:
                self.status = self.STATUS_EDITOR_REVIEW
            # Aks holda mas'ul kotibga yuborish
            else:
                self.status = self.STATUS_SECRETARY_REVIEW
        else:
            # Tahrir uchun qaytarish
            self.status = self.STATUS_REVISION_REQUESTED
            self.revision_requested_date = timezone.now()

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=reviewer,
            old_status=old_status,
            new_status=self.status,
            comment=comment,
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification

        if is_approved:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Taqrizchi maqolani qabul qildi"),
                _(f"Taqrizchi maqolani qabul qildi: {self.title}")
            )

            # Agar muharrir tayinlangan bo'lsa, muharrirga bildirishnoma yuborish
            if self.editor and self.status == self.STATUS_EDITOR_REVIEW:
                Notification.notify_editor(
                    self,
                    _("Sizga yangi maqola tayinlandi"),
                    _(f"Sizga yangi maqola tayinlandi: {self.title}")
                )
        else:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Taqrizchi maqolani tahrir uchun qaytardi"),
                _(f"Taqrizchi maqolani tahrir uchun qaytardi: {self.title}")
            )

            # Muallifga bildirishnoma yuborish
            Notification.notify_author(
                self,
                _("Maqolangiz tahrir uchun qaytarildi"),
                _(f"Maqolangiz tahrir uchun qaytarildi: {self.title}")
            )

        return self

    def editor_decision(self, editor, is_approved, comment, file=None):
        """
        Muharrir qarori
        """
        old_status = self.status

        if is_approved:
            # Agar bosh muharrir o'rinbosari tayinlangan bo'lsa, unga yuborish
            if self.deputy_chief:
                self.status = self.STATUS_DEPUTY_REVIEW
            # Aks holda mas'ul kotibga yuborish
            else:
                self.status = self.STATUS_SECRETARY_REVIEW
        else:
            # Tahrir uchun qaytarish
            self.status = self.STATUS_REVISION_REQUESTED
            self.revision_requested_date = timezone.now()

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=editor,
            old_status=old_status,
            new_status=self.status,
            comment=comment,
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification

        if is_approved:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Muharrir maqolani qabul qildi"),
                _(f"Muharrir maqolani qabul qildi: {self.title}")
            )

            # Agar bosh muharrir o'rinbosari tayinlangan bo'lsa, unga bildirishnoma yuborish
            if self.deputy_chief and self.status == self.STATUS_DEPUTY_REVIEW:
                Notification.notify_deputy(
                    self,
                    _("Sizga yangi maqola tayinlandi"),
                    _(f"Sizga yangi maqola tayinlandi: {self.title}")
                )
        else:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Muharrir maqolani tahrir uchun qaytardi"),
                _(f"Muharrir maqolani tahrir uchun qaytardi: {self.title}")
            )

            # Muallifga bildirishnoma yuborish
            Notification.notify_author(
                self,
                _("Maqolangiz tahrir uchun qaytarildi"),
                _(f"Maqolangiz tahrir uchun qaytarildi: {self.title}")
            )

        return self

    def deputy_decision(self, deputy, is_approved, comment):
        """
        Bosh muharrir o'rinbosari qarori
        """
        old_status = self.status

        if is_approved:
            # Maqolani qabul qilish
            self.status = self.STATUS_ACCEPTED
            self.acceptance_date = timezone.now()
        else:
            # Tahrir uchun qaytarish
            self.status = self.STATUS_REVISION_REQUESTED
            self.revision_requested_date = timezone.now()

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=deputy,
            old_status=old_status,
            new_status=self.status,
            comment=comment
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification

        if is_approved:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Bosh muharrir o'rinbosari maqolani qabul qildi"),
                _(f"Bosh muharrir o'rinbosari maqolani qabul qildi: {self.title}")
            )

            # Muallifga bildirishnoma yuborish
            Notification.notify_author(
                self,
                _("Maqolangiz qabul qilindi"),
                _(f"Maqolangiz qabul qilindi: {self.title}")
            )
        else:
            # Mas'ul kotibga bildirishnoma yuborish
            Notification.notify_secretary(
                self,
                _("Bosh muharrir o'rinbosari maqolani tahrir uchun qaytardi"),
                _(f"Bosh muharrir o'rinbosari maqolani tahrir uchun qaytardi: {self.title}")
            )

            # Muallifga bildirishnoma yuborish
            Notification.notify_author(
                self,
                _("Maqolangiz tahrir uchun qaytarildi"),
                _(f"Maqolangiz tahrir uchun qaytarildi: {self.title}")
            )

        return self

    def publish(self, user, journal_issue, start_page, end_page, revised_file=None):
        """
        Maqolani chop etish
        """
        old_status = self.status
        self.status = self.STATUS_PUBLISHED
        self.journal_issue = journal_issue
        self.start_page = start_page
        self.end_page = end_page
        self.publication_date = timezone.now()

        if revised_file:
            self.revised_file = revised_file

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=user,
            old_status=old_status,
            new_status=self.STATUS_PUBLISHED,
            comment=f'Maqola chop etildi: {journal_issue}'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification

        # Muallifga bildirishnoma yuborish
        Notification.notify_author(
            self,
            _("Maqolangiz chop etildi"),
            _(f"Maqolangiz chop etildi: {self.title}")
        )

        return self


class ArticleHistory(models.Model):
    """
    Maqola tarixi modeli
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Maqola')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_history',
        verbose_name=_('Foydalanuvchi')
    )
    old_status = models.CharField(
        _('Eski holat'),
        max_length=20,
        choices=Article.STATUS_CHOICES,
        null=True,
        blank=True
    )
    new_status = models.CharField(
        _('Yangi holat'),
        max_length=20,
        choices=Article.STATUS_CHOICES
    )
    comment = models.TextField(_('Izoh'))
    file = models.FileField(
        _('Fayl'),
        upload_to=article_file_path,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Maqola tarixi')
        verbose_name_plural = _('Maqola tarixi')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article.title} - {self.new_status}"


class Comment(models.Model):
    """
    Maqola izohi modeli
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Maqola')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_comments',
        verbose_name=_('Foydalanuvchi')
    )
    text = models.TextField(_('Matn'))
    file = models.FileField(
        _('Fayl'),
        upload_to=article_file_path,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Yaratilgan sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Izoh')
        verbose_name_plural = _('Izohlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article.title} - {self.user.username}"
