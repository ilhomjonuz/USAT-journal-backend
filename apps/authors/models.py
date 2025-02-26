from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


DEGREE_CHOICES = [
    ('PHD_ECON', _('(PhD), Economics')),
    ('PHD_PED', _('(PhD), Pedagogy')),
    ('PHD_TECH', _('(PhD), Technical Sciences')),
    ('DSC_ECON', _('(DSc), Economics')),
    ('DSC_PED', _('(DSc), Pedagogy')),
    ('DSC_TECH', _('(DSc), Technical Sciences')),
]

ACADEMIC_TITLE_CHOICES = [
    ('DOCENT', _('Docent')),
    ('PROFESSOR', _('Professor')),
    ('ACADEMIC', _('Academic'))
]

class Author(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='profile',
        null=True,
        blank=True,
        verbose_name=_('User')
    )
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"), blank=True)
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), blank=True)
    country = models.CharField(max_length=100, verbose_name=_("Country"), blank=True)
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True)
    workplace = models.CharField(max_length=200, verbose_name=_("Workplace"), blank=True)
    level = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Position or level of education"))
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True)
    telegram_contact = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Telegram Contact"),
        help_text=_("Telegram username")
    )
    whatsapp_contact = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("WhatsApp Contact"),
        help_text=_("WhatsApp number")
    )
    academic_degree = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Academic Degree")
    )
    academic_title = models.CharField(
        max_length = 20,
        choices = ACADEMIC_TITLE_CHOICES,
        null=True,
        blank=True,
        verbose_name = _("Academic Title")
    )
    orcid = models.CharField(
        max_length=20,
        verbose_name=_("ORCID Number"),
        blank=True,
        help_text=_("ORCID identifier")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    objects = models.Manager()

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
