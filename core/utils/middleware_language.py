from django.conf import settings
from django.utils import translation


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.headers.get('Accept-Language')
        if language in dict(settings.LANGUAGES):
            translation.activate(language)
        else:
            translation.activate(settings.LANGUAGE_CODE)

        response = self.get_response(request)

        translation.deactivate()

        return response
