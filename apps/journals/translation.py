from modeltranslation.translator import register, TranslationOptions

from .models import Journal


@register(Journal)
class JournalTranslationOptions(TranslationOptions):
    fields = ('name', 'description')