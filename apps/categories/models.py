from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Direction Name"))
    code = models.CharField(max_length=200, verbose_name=_("Direction Code"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")

    def __str__(self):
        return self.name
