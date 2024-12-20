from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.translation import gettext_lazy as _

from apps.articles.models import Article
from apps.articles.serializers import ArticleSerializer


class LatestArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(status='PUBLISHED', journal_issue__is_published=True).order_by('-publication_date')[:4]

    @swagger_auto_schema(
        operation_description=_("Get a list of the latest articles"),
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description=_("Language code (uz, ru, or en)"),
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AllArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(status='PUBLISHED', journal_issue__is_published=True).order_by('-publication_date')

    @swagger_auto_schema(
        operation_description=_("Get a list of the latest articles"),
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description=_("Language code (uz, ru, or en)"),
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)