from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Custom User model with roles
class User(AbstractUser):
    class Role(models.TextChoices):
        AUTHOR = "author", _("Author")
        EDITOR = "editor", _("Editor")
        REVIEWER = "reviewer", _("Reviewer")
        SECRETARY = "secretary", _("Secretary")
        DEPUTY_EDITOR = "deputy_editor", _("Deputy Editor")
        ADMIN = "admin", _("Admin")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AUTHOR, verbose_name=_("Role"))
    prefers_dark_mode = models.BooleanField(default=False, verbose_name=_("Prefer Dark Mode"))

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_avatar(self):
        return f"{self.first_name[0]}{self.last_name[0]}"
