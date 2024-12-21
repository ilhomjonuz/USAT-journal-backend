from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.journals.models import JournalIssue
from apps.journals.serializers import JournalIssueListSerializer


class LatestJournalIssueListView(generics.ListAPIView):
    queryset = JournalIssue.objects.filter(is_published=True).order_by('-publication_date')[:4]
    serializer_class = JournalIssueListSerializer

    @swagger_auto_schema(
        operation_description="Get the latest published journal issues",
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


class AllJournalIssueListView(generics.ListAPIView):
    queryset = JournalIssue.objects.filter(is_published=True).order_by('-publication_date')
    serializer_class = JournalIssueListSerializer

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
