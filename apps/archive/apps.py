from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArchiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.archive'
    verbose_name = _("Archive")
    verbose_name_plural = _("Archives")
