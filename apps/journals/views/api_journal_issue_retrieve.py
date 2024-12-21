from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from apps.journals.models import JournalIssue
from apps.journals.serializers import JournalRetrieveSerializer


class JournalIssueRetrieveAPIView(generics.RetrieveAPIView):
    queryset = JournalIssue.objects.filter(is_published=True)
    serializer_class = JournalRetrieveSerializer

    @swagger_auto_schema(
        operation_description="Get the detail of a journal issue",
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
        issue = self.get_object()
        # Increment the views_count field
        issue.views_count += 1
        issue.save(update_fields=['views_count'])
        return super().get(request, *args, **kwargs)
