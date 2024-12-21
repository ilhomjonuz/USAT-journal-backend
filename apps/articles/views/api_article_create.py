from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.response import Response

from apps.articles.models import Article
from apps.articles.serializers import ArticleSubmissionSerializer


class ArticleSubmissionView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSubmissionSerializer

    @swagger_auto_schema(
        request_body=ArticleSubmissionSerializer,
        responses={
            201: openapi.Response(
                description="Article submitted successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Article submitted successfully",
                        "article_id": 1
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "status": "error",
                        "errors": {
                            "title": ["This field is required."]
                        }
                    }
                },
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': _('Article submitted successfully'),
                    'article_id': article.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'status': 'error',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
