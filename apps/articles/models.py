from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import redirect
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.utils import timezone


User = get_user_model()


class Article(models.Model):
    """Maqola modeli"""
    STATUS_CHOICES = [
        ('SUBMITTED', _('Submitted')),  # Yuborilgan
        ('SECRETARY_REVIEW', _('Secretary review')),  # Mas\'ul kotib tekshiruvida
        ('REVIEWER_REVIEW', _('Reviewer review')),  # Taqrizchi tekshiruvida
        ('EDITOR_REVIEW', _('Editor review')),  # Muharrir tekshiruvida
        ('DEPUTY_REVIEW', _('Deputy editor review')),  # Bosh muharrir o\'rinbosari tekshiruvida
        ('REVISION_REQUESTED', _('Returned for revision')),  # Tahrir uchun qaytarilgan
        ('ACCEPTED', _('Accepted')),  # Qabul qilingan
        ('REJECTED', _('Rejected')),  # Rad etilgan
        ('PUBLISHED', _('Published')),  # Chop etilgan
    ]

    # Existing fields from the provided model
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        verbose_name=_("Direction"),
        related_name='articles'
    )
    title = models.CharField(max_length=500, verbose_name=_("Title"))
    slug = models.SlugField(verbose_name=_("Slug"), unique=True)
    keywords = models.TextField(
        verbose_name=_("Keywords"),
        help_text=_("Enter keywords separated by commas")
    )
    annotation = models.TextField(verbose_name=_("Annotation"))
    references = models.TextField(verbose_name=_("List of references"), null=True, blank=True)
    authors = models.ManyToManyField(
        'authors.Author',
        related_name='articles',
        verbose_name=_("Authors")
    )
    anti_plagiarism_certificate = models.FileField(
        upload_to='anti_plagiarism_certificates/',
        verbose_name=_("Anti-Plagiarism Certificate"),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text=_("Accepted file types: .pdf"),
        null=True,
        blank=True
    )
    original_file = models.FileField(
        upload_to='article_submissions/',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'doc', 'docx', 'odt'])],
        verbose_name=_("Original Article File"),
        help_text=_("Accepted file types: .txt, .doc, .docx, .odt"),
        blank=True
    )
    revised_file = models.FileField(
        upload_to='article_revisions/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True,
        verbose_name=_("Final Article File"),
        help_text=_("Accepted file types: .pdf")
    )

    # Page information
    start_page = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Start Page"),
        null=True,
        blank=True,
        help_text=_("Starting page in the journal")
    )
    end_page = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("End Page"),
        null=True,
        blank=True,
        help_text=_("Ending page in the journal")
    )

    # Statistics
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Views Count"),
        help_text=_("Number of times the article has been viewed")
    )
    downloads_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Downloads Count"),
        help_text=_("Number of times the article has been downloaded")
    )

    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED',
        verbose_name=_("Status")
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submission Date")
    )
    revision_requested_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Tahrir so'ralgan sana"),
        help_text=_("Article returned for editing date")
    )
    acceptance_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Acceptance Date"),
        help_text=_("Date when the article was accepted")
    )
    publication_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Publication Date"),
        help_text=_("Date when the article was published")
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated")
    )

    journal_issue = models.ForeignKey(
        'journals.JournalIssue',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_("Journal Issue")
    )

    # Tayinlangan foydalanuvchilar
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='authored_articles',
        verbose_name=_('Author')
    )
    secretary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='secretary_articles',
        verbose_name=_('Mas\'ul kotib')
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewer_articles',
        verbose_name=_('Taqrizchi')
    )
    editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='editor_articles',
        verbose_name=_('Muharrir')
    )
    deputy_chief = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deputy_chief_articles',
        verbose_name=_('Bosh muharrir o\'rinbosari')
    )

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['-submission_date']),
            models.Index(fields=['status']),
            models.Index(fields=['publication_date']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return redirect('article_detail', kwargs={'pk': self.pk})

    def generate_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    @property
    def is_published(self):
        return self.status == 'PUBLISHED' and self.journal_issue and self.journal_issue.is_published

    @property
    def page_range(self):
        """Return the page range as a string (e.g., '1-120')"""
        if self.start_page and self.end_page:
            return f"{self.start_page}-{self.end_page}"
        return None

    @property
    def total_pages(self):
        """Calculate total number of pages"""
        if self.start_page and self.end_page:
            return self.end_page - self.start_page + 1
        return None

    @property
    def is_under_review(self):
        return self.status in ['SECRETARY_REVIEW', 'REVIEWER_REVIEW', 'EDITOR_REVIEW', 'DEPUTY_REVIEW']

    @property
    def needs_revision(self):
        return self.status == 'REVISION_REQUESTED'

    @property
    def can_be_withdrawn(self):
        return self.status not in ['PUBLISHED', 'REJECTED']

    @property
    def current_reviewer(self):
        """Return the current reviewer based on status"""
        if self.status == 'REVIEWER_REVIEW':
            return self.reviewer
        return None

    @property
    def current_editor(self):
        """Return the current editor based on status"""
        if self.status == 'EDITOR_REVIEW':
            return self.editor
        return None

    @property
    def current_deputy(self):
        """Return the current deputy chief based on status"""
        if self.status == 'DEPUTY_REVIEW':
            return self.deputy_chief
        return None

    def increment_view_count(self):
        """Increment the view count by 1"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_download_count(self):
        """Increment the download count by 1"""
        self.downloads_count += 1
        self.save(update_fields=['downloads_count'])

    def submit(self, user):
        """Maqolani yuborish"""
        self.status = 'SUBMITTED'
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=user,
            new_status='SUBMITTED',
            comment=_('Maqola yuborildi')
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_secretary(
            self,
            _("Yangi maqola yuborildi"),
            _(f"Yangi maqola yuborildi: {self.title}")
        )

        return True

    def assign_secretary(self, secretary):
        """Mas'ul kotibni tayinlash"""
        if self.status == 'SUBMITTED':
            self.secretary = secretary
            self.status = 'SECRETARY_REVIEW'
            self.save()

            # Tarix yozuvini yaratish
            ArticleHistory.objects.create(
                article=self,
                user=secretary,
                old_status='SUBMITTED',
                new_status='SECRETARY_REVIEW',
                comment='Mas\'ul kotib tayinlandi'
            )

            # Bildirishnoma yuborish
            from apps.notifications.models import Notification
            Notification.notify_author(
                self,
                _("Maqolangiz ko'rib chiqilmoqda"),
                _(f"Maqolangiz mas'ul kotib tomonidan ko'rib chiqilmoqda")
            )

            return True
        return False

    def assign_reviewer(self, secretary, reviewer):
        """Taqrizchini tayinlash"""
        if self.status == 'SECRETARY_REVIEW':
            self.reviewer = reviewer
            self.status = 'REVIEWER_REVIEW'
            self.save()

            # Tarix yozuvini yaratish
            ArticleHistory.objects.create(
                article=self,
                user=secretary,
                old_status='SECRETARY_REVIEW',
                new_status='REVIEWER_REVIEW',
                comment=f'Taqrizchi ({reviewer.full_name}) tayinlandi'
            )

            # Bildirishnoma yuborish
            from apps.notifications.models import Notification
            Notification.notify_reviewer(
                self,
                _("Sizga yangi maqola tayinlandi"),
                _(f"Sizga yangi maqola tayinlandi: {self.title}")
            )

            return True
        return False

    def reviewer_decision(self, reviewer, is_approved, comment='', file=None):
        """Taqrizchi qarori"""
        if self.status != 'REVIEWER_REVIEW' or self.reviewer != reviewer:
            return False

        if is_approved:
            self.status = 'SECRETARY_REVIEW'  # Qayta mas'ul kotibga yuboriladi
            new_status = 'SECRETARY_REVIEW'
            status_comment = 'Taqrizchi tasdiqladi, mas\'ul kotibga yuborildi'
        else:
            self.status = 'REVISION_REQUESTED'
            self.revision_requested_date = timezone.now()
            new_status = 'REVISION_REQUESTED'
            status_comment = 'Tahrir talab qilinadi'

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=reviewer,
            old_status='REVIEWER_REVIEW',
            new_status=new_status,
            comment=comment or status_comment,
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        if is_approved:
            Notification.notify_secretary(
                self,
                _("Taqrizchi maqolani tasdiqladi"),
                _(f"Taqrizchi maqolani tasdiqladi: {self.title}")
            )
        else:
            Notification.notify_secretary(
                self,
                _("Taqrizchi tahrir talab qildi"),
                _(f"Taqrizchi tahrir talab qildi: {self.title}")
            )

        return True

    def assign_editor(self, secretary, editor):
        """Muharrirni tayinlash"""
        if self.status == 'SECRETARY_REVIEW' and self.reviewer is not None:
            self.editor = editor
            self.status = 'EDITOR_REVIEW'
            self.save()

            # Tarix yozuvini yaratish
            ArticleHistory.objects.create(
                article=self,
                user=secretary,
                old_status='SECRETARY_REVIEW',
                new_status='EDITOR_REVIEW',
                comment=f'Muharrir ({editor.full_name}) tayinlandi'
            )

            # Bildirishnoma yuborish
            from apps.notifications.models import Notification
            Notification.notify_editor(
                self,
                _("Sizga yangi maqola tayinlandi"),
                _(f"Sizga yangi maqola tayinlandi: {self.title}")
            )

            return True
        return False

    def editor_decision(self, editor, is_approved, comment='', file=None):
        """Muharrir qarori"""
        if self.status != 'EDITOR_REVIEW' or self.editor != editor:
            return False

        if is_approved:
            self.status = 'DEPUTY_REVIEW'
            new_status = 'DEPUTY_REVIEW'
            status_comment = _('Muharrir tasdiqladi, bosh muharrir o\'rinbosariga yuborildi')
        else:
            self.status = 'REVISION_REQUESTED'
            self.revision_requested_date = timezone.now()
            new_status = 'REVISION_REQUESTED'
            status_comment = _('Tahrir talab qilinadi')

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=editor,
            old_status='EDITOR_REVIEW',
            new_status=new_status,
            comment=comment or status_comment,
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        if is_approved:
            Notification.notify_secretary(
                self,
                _("Muharrir maqolani tasdiqladi"),
                _(f"Muharrir maqolani tasdiqladi: {self.title}")
            )
            Notification.notify_deputy(
                self,
                _("Sizga yangi maqola tayinlandi"),
                _(f"Sizga yangi maqola tayinlandi: {self.title}")
            )
        else:
            Notification.notify_secretary(
                self,
                _("Muharrir tahrir talab qildi"),
                _(f"Muharrir tahrir talab qildi: {self.title}")
            )

        return True

    def deputy_decision(self, deputy, is_approved, comment=''):
        """Bosh muharrir o'rinbosari qarori"""
        if self.status != 'DEPUTY_REVIEW' or self.deputy_chief != deputy:
            return False

        if is_approved:
            self.status = 'ACCEPTED'
            self.acceptance_date = timezone.now()
            status_comment = 'Maqola qabul qilindi'
        else:
            self.status = 'REVISION_REQUESTED'
            self.revision_requested_date = timezone.now()
            status_comment = 'Tahrir talab qilinadi'

        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=deputy,
            old_status='DEPUTY_REVIEW',
            new_status=self.status,
            comment=comment or status_comment
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        if is_approved:
            Notification.notify_secretary(
                self,
                _("Bosh muharrir o'rinbosari maqolani tasdiqladi"),
                _(f"Bosh muharrir o'rinbosari maqolani tasdiqladi: {self.title}")
            )
            Notification.notify_author(
                self,
                _("Maqolangiz qabul qilindi"),
                _(f"Maqolangiz qabul qilindi va chop etishga tayyorlanmoqda")
            )
        else:
            Notification.notify_secretary(
                self,
                _("Bosh muharrir o'rinbosari tahrir talab qildi"),
                _(f"Bosh muharrir o'rinbosari tahrir talab qildi: {self.title}")
            )

        return True

    def publish(self, user, journal_issue, start_page, end_page, revised_file=None):
        """Maqolani chop etish"""
        if self.status != 'ACCEPTED':
            return False

        self.status = 'PUBLISHED'
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
            old_status='ACCEPTED',
            new_status='PUBLISHED',
            comment=f'Maqola chop etildi. Jurnal: {journal_issue}, Sahifalar: {start_page}-{end_page}'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_author(
            self,
            _("Maqolangiz chop etildi"),
            _(f"Maqolangiz chop etildi. Jurnal: {journal_issue}, Sahifalar: {start_page}-{end_page}")
        )

        return True

    def submit_revision(self, author, revised_file, comment=''):
        """Tahrirlangan maqolani yuborish"""
        if self.status != 'REVISION_REQUESTED':
            return False

        old_status = self.status
        self.revised_file = revised_file
        self.status = 'SUBMITTED'
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=author,
            old_status=old_status,
            new_status='SUBMITTED',
            comment=comment or 'Tahrirlangan maqola yuborildi',
            file=revised_file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_secretary(
            self,
            _("Tahrirlangan maqola yuborildi"),
            _(f"Tahrirlangan maqola yuborildi: {self.title}")
        )

        return True

    def reject(self, user, comment=''):
        """Maqolani rad etish"""
        old_status = self.status
        self.status = 'REJECTED'
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=user,
            old_status=old_status,
            new_status='REJECTED',
            comment=comment or 'Maqola rad etildi'
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_author(
            self,
            _("Maqolangiz rad etildi"),
            _(f"Maqolangiz rad etildi: {comment or 'Maqola rad etildi'}")
        )

        return True

    def secretary_request_revision(self, secretary, comment='', file=None):
        """Mas'ul kotib tahrir talab qilishi"""
        if self.status != 'SECRETARY_REVIEW':
            return False

        old_status = self.status
        self.status = 'REVISION_REQUESTED'
        self.revision_requested_date = timezone.now()
        self.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=self,
            user=secretary,
            old_status=old_status,
            new_status='REVISION_REQUESTED',
            comment=comment or 'Mas\'ul kotib tahrir talab qildi',
            file=file
        )

        # Bildirishnoma yuborish
        from apps.notifications.models import Notification
        Notification.notify_author(
            self,
            _("Maqolangiz tahrir uchun qaytarildi"),
            _(f"Maqolangiz tahrir uchun qaytarildi: {comment or 'Tahrir talab qilinadi'}")
        )

        return True

    def secretary_reject(self, secretary, comment=''):
        """Mas'ul kotib rad etishi"""
        if self.status != 'SECRETARY_REVIEW':
            return False

        return self.reject(secretary, comment)


class ArticleHistory(models.Model):
    """Maqola tarixi"""
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='history', verbose_name=_('Maqola'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_actions',
                             verbose_name=_('Foydalanuvchi'))

    old_status = models.CharField(_('Oldingi holat'), max_length=30, null=True, blank=True)
    new_status = models.CharField(_('Yangi holat'), max_length=30)

    comment = models.TextField(_('Izoh'), blank=True)
    file = models.FileField(_('Fayl'), upload_to='articles/history/', null=True, blank=True)

    created_at = models.DateTimeField(_('Sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Maqola tarixi')
        verbose_name_plural = _('Maqola tarixi')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article.title} - {self.new_status} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"


class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments', verbose_name=_('Maqola'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Foydalanuvchi'))

    text = models.TextField(_('Matn'))
    file = models.FileField(_('Fayl'), upload_to='comments/', null=True, blank=True)

    created_at = models.DateTimeField(_('Sana'), auto_now_add=True)

    class Meta:
        verbose_name = _('Izoh')
        verbose_name_plural = _('Izohlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article.title} - {self.user.full_name}"
