from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from functools import cached_property


class User(AbstractUser):
    class Role(models.TextChoices):
        AUTHOR = "author", _("Author")
        EDITOR = "editor", _("Editor")
        REVIEWER = "reviewer", _("Reviewer")
        SECRETARY = "secretary", _("Secretary")
        DEPUTY_EDITOR = "deputy_editor", _("Deputy Editor")
        ADMIN = "admin", _("Admin")

    class Step(models.TextChoices):
        REGISTRATION = "registration", _("Initial Registration")
        PERSONAL_INFO = "personal_info", _("Personal Information")
        WORKPLACE_INFO = "workplace_info", _("Workplace Information")
        CONTACT_INFO = "contact_info", _("Contact Information")
        ACADEMIC_INFO = "academic_info", _("Academic Information")
        COMPLETED = "completed", _("Profile Completed")

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.AUTHOR, verbose_name=_("Role")
    )
    email = models.EmailField(
        verbose_name=_("Email address"), unique=True, db_index=True
    )
    is_email_verified = models.BooleanField(default=False, verbose_name=_("Is email verified"))
    profile_completion_step = models.CharField(
        max_length=20,
        choices=Step.choices,
        default=Step.REGISTRATION,
        verbose_name=_("Profile Completion Step"),
        db_index=True
    )
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    prefers_dark_mode = models.BooleanField(default=False, verbose_name=_("Prefer Dark Mode"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email  # Use email instead of username for better identification

    def save(self, *args, **kwargs):
        """Ensure email is always stored in lowercase to avoid duplicate issues."""
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    @cached_property
    def get_avatar(self):
        first_initial = self.first_name[0] if self.first_name else "?"
        last_initial = self.last_name[0] if self.last_name else "?"
        return f"{first_initial}{last_initial}".upper()

    def set_verification_code(self, code):
        """Set verification code with timestamp."""
        self.verification_code = code
        self.verification_code_created = timezone.now()
        self.save(update_fields=["verification_code", "verification_code_created"])

    def is_verification_code_valid(self):
        """Check if the verification code is still valid (10 minutes)."""
        if not self.verification_code or not self.verification_code_created:
            return False
        expiration_time = self.verification_code_created + timedelta(minutes=10)
        return timezone.now() <= expiration_time

    def clear_verification_code(self):
        """Clear verification code and timestamp."""
        self.verification_code = None
        self.verification_code_created = None
        self.save(update_fields=["verification_code", "verification_code_created"])
