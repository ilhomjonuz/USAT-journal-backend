from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.journals.models import JournalIssue
from apps.journals.serializers import JournalIssueSerializer


class JournalIssueListView(generics.ListAPIView):
    queryset = JournalIssue.objects.filter(is_published=True)
    serializer_class = JournalIssueSerializer

    @swagger_auto_schema(
        operation_description="Get a list of published journal issues",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
