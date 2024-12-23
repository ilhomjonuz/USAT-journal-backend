from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from apps.articles.models import Article
from apps.articles.serializers import ArticleRetrieveSerializer


class ArticleRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(status='PUBLISHED', journal_issue__is_published=True)
    serializer_class = ArticleRetrieveSerializer

    lookup_field = 'slug'

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
        article = self.get_object()
        article.views_count += 1
        article.save(update_fields=['views_count'])
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
