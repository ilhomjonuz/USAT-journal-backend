from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Journal(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Journal Name"))
    description = models.TextField(verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")

    def __str__(self):
        return self.name


class JournalVolume(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='volumes', verbose_name=_("Journal"))
    volume_number = models.PositiveIntegerField(verbose_name=_("Volume Number"))
    year = models.PositiveIntegerField(verbose_name=_("Year"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        unique_together = ['journal', 'volume_number']
        ordering = ['-year', '-volume_number']
        verbose_name = _("Journal Volume")
        verbose_name_plural = _("Journal Volumes")

    def __str__(self):
        return f"{self.journal.name} - Volume {self.volume_number}"


class JournalIssue(models.Model):
    number = models.PositiveIntegerField(verbose_name=_("Number"))
    volume = models.ForeignKey(JournalVolume, on_delete=models.CASCADE, related_name='issues', verbose_name=_("Volume"))
    issue_number = models.PositiveIntegerField(verbose_name=_("Issue Number"))
    image = models.ImageField(upload_to='journal_issues/', null=True, blank=True, verbose_name=_("Cover Image"))
    journal_file = models.FileField(upload_to='journal_issues/', null=True, blank=True, verbose_name=_("Journal File"))
    publication_date = models.DateField(verbose_name=_("Publication Date"))
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    start_page = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Start Page"),
        default=1
    )
    end_page = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("End Page")
    )

    class Meta:
        unique_together = ['volume', 'issue_number']
        ordering = ['-publication_date', '-issue_number']
        verbose_name = _("Journal Issue")
        verbose_name_plural = _("Journal Issues")

    def __str__(self):
        return f"{self.volume} - Issue {self.issue_number}"

    @property
    def page_range(self):
        """Return the page range as a string (e.g., '1-120')"""
        return f"{self.start_page}-{self.end_page}"

    @property
    def total_pages(self):
        """Calculate total number of pages"""
        return self.end_page - self.start_page + 1

    def increment_view_count(self):
        """Increment the view count by 1"""
        self.views_count += 1
        self.save()
