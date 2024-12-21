from django.utils.translation import gettext_lazy as _
from rest_framework import status, views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.articles.serializers import ArticleSubmissionSerializer

class ArticleSubmissionAPIView(views.APIView):
    parser_classes = [MultiPartParser]

    # @swagger_auto_schema(
    #     operation_description="Create a new article",
    #     request_body=ArticleSubmissionSerializer,
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'Accept-Language',
    #             openapi.IN_HEADER,
    #             description="Language code (uz, ru, or en)",
    #             type=openapi.TYPE_STRING,
    #             enum=['uz', 'ru', 'en']
    #         ),
    #     ],
    #     responses={201: openapi.Response('Article created successfully')}
    # )
    def post(self, request, *args, **kwargs):
        serializer = ArticleSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save()
            return Response({
                'status': 'success',
                'message': _('Article created successfully'),
                'article_id': article.id
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
