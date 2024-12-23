import os
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.articles.serializers import ArticleSubmissionSerializer


class ArticleSubmissionView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @swagger_auto_schema(
        operation_description="Submit a new article with authors",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'direction_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Direction ID'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Article title'),
                'keywords': openapi.Schema(type=openapi.TYPE_STRING, description='Keywords separated by commas'),
                'annotation': openapi.Schema(type=openapi.TYPE_STRING, description='Article annotation'),
                'original_file': openapi.Schema(type=openapi.TYPE_FILE, description='Original article file'),
                'authors_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'country': openapi.Schema(type=openapi.TYPE_STRING),
                            'city': openapi.Schema(type=openapi.TYPE_STRING),
                            'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                            'phone': openapi.Schema(type=openapi.TYPE_STRING),
                            'messenger_contact': openapi.Schema(type=openapi.TYPE_STRING),
                            'academic_degree': openapi.Schema(type=openapi.TYPE_STRING, enum=['PHD_ECON', 'PHD_PED', 'PHD_TECH', 'DSC_ECON', 'DSC_PED', 'DSC_TECH']),
                            'academic_title': openapi.Schema(type=openapi.TYPE_STRING, enum=['DOCENT', 'PROFESSOR']),
                            'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    description='List of authors data'
                ),
            },
            required=['direction_id', 'title', 'keywords', 'annotation', 'original_file', 'authors_data']
        ),
        responses={
            201: openapi.Response(
                description="Article created successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Article submitted successfully",
                        "article_id": 1
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "status": "error",
                        "errors": {
                            "field": ["error message"]
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error message"
                    }
                }
            )
        }
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            if not os.access(settings.MEDIA_ROOT, os.W_OK):
                return Response(
                    {
                        'status': 'error',
                        'message': _('Media directory is not writable: ') + f'{settings.MEDIA_ROOT}'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            serializer = ArticleSubmissionSerializer(
                data=request.data,
                context={'request': request}
            )

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

        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
