from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JournalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.journals'
    verbose_name = _("Journal")
    verbose_name_plural = _("Journals")
