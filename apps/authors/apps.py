from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authors'
    verbose_name = _("Author")
    verbose_name_plural = _("Authors")
