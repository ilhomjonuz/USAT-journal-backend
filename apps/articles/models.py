from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.utils import timezone


class Article(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', _('Submitted')),
        ('UNDER_REVIEW', _('Under Review')),
        ('ACCEPTED', _('Accepted')),
        ('REJECTED', _('Rejected')),
        ('PUBLISHED', _('Published')),
    ]

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        verbose_name=_("Direction")
    )
    title = models.CharField(max_length=500, verbose_name=_("Title"))
    keywords = models.TextField(
        verbose_name=_("Keywords"),
        help_text=_("Enter keywords separated by commas")
    )
    annotation = models.TextField(verbose_name=_("Annotation"))
    authors = models.ManyToManyField(
        'authors.Author',
        related_name='articles',
        verbose_name=_("Authors")
    )
    original_file = models.FileField(
        upload_to='article_submissions/',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'doc', 'docx', 'odt'])],
        verbose_name=_("Original Article File"),
        help_text=_("Accepted file types: .txt, .doc, .docx, .odt")
    )
    revised_file = models.FileField(
        upload_to='article_revisions/',
        validators=[FileExtensionValidator(allowed_extensions=[
            'doc', 'docx', 'odt', 'pdf', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'rtf'
        ])],
        null=True,
        blank=True,
        verbose_name=_("Revised Article File"),
        help_text=_("Accepted file types: .doc, .docx, .odt, .pdf, .ppt, .pptx, .xls, .xlsx, .txt, .rtf")
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
    review_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Review Date"),
        help_text=_("Date when the article was sent for review")
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

    def increment_view_count(self):
        """Increment the view count by 1"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_download_count(self):
        """Increment the download count by 1"""
        self.downloads_count += 1
        self.save(update_fields=['downloads_count'])

    def set_under_review(self):
        """Mark article as under review"""
        self.status = 'UNDER_REVIEW'
        self.review_date = timezone.now()
        self.save(update_fields=['status', 'review_date'])

    def accept(self):
        """Accept the article"""
        self.status = 'ACCEPTED'
        self.acceptance_date = timezone.now()
        self.save(update_fields=['status', 'acceptance_date'])

    def publish(self):
        """Publish the article"""
        self.status = 'PUBLISHED'
        self.publication_date = timezone.now()
        self.save(update_fields=['status', 'publication_date'])

    def reject(self):
        """Reject the article"""
        self.status = 'REJECTED'
        self.save(update_fields=['status'])
