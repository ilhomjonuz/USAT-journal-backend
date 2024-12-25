from django.conf import settings
from django.utils import translation


class LanguageMiddleware:
    """
    Middleware to set the language for API requests based on the 'Accept-Language' header.
    For non-API requests, it bypasses language handling.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for an API endpoint
        if request.path.startswith('/api/v1/'):
            language = self._get_language(request)
            translation.activate(language)
            request.LANGUAGE_CODE = language  # Attach it to the request object

        # Process the response
        response = self.get_response(request)

        # Deactivate the language after processing the request
        translation.deactivate()

        return response

    def _get_language(self, request):
        """
        Determines the language to activate based on the 'Accept-Language' header.
        """
        requested_language = request.headers.get('Accept-Language')
        supported_languages = dict(settings.LANGUAGES).keys()

        # Return the requested language if supported, otherwise fall back to the default
        return (
            requested_language
            if requested_language in supported_languages
            else settings.LANGUAGE_CODE
        )
