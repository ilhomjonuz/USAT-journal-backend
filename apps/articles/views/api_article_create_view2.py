import os

from django.conf import settings
from django.template.defaultfilters import title
from django.utils.translation import gettext_lazy as _
from rest_framework import status, permissions
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.articles.serializers.article_create2 import ArticleSubmission2Serializer


class ArticleSubmission2View(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @swagger_auto_schema(
        operation_summary="Article submission v2",
        operation_description="Submit a new article with authors v2",
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
                'references': openapi.Schema(type=openapi.TYPE_STRING, description='List of references'),
                'anti_plagiarism_certificate': openapi.Schema(type=openapi.TYPE_FILE, description='Anti-Plagiarism Certificate'),
                'original_file': openapi.Schema(type=openapi.TYPE_FILE, description='Original article file'),
                'authors_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'author_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    ),
                    description='List of authors data',
                ),
            },
            required=['direction_id', 'title', 'keywords', 'annotation', 'original_file']
        ),
        responses={
            201: openapi.Response(
                description="Article created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'article_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'errors': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING)  # ✅ FIXED HERE
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Forbidden - Invalid or Expired Token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="Error code"),
                        "messages": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "token_class": openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description="Type of token"),
                                    "token_type": openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description="Token category"),
                                    "message": openapi.Schema(type=openapi.TYPE_STRING,
                                                              description="Detailed error message")
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="Not Fount",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        "details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING)  # ✅ FIXED HERE
                            )
                        )
                    }
                )
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                examples={
                    "application/json": {
                        "success": False,
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
                        'success': False,
                        'message': _('Media directory is not writable: ') + f'{settings.MEDIA_ROOT}'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            serializer = ArticleSubmission2Serializer(
                data=request.data,
                context={'request': request}
            )

            if serializer.is_valid():
                article = serializer.save()
                return Response(
                    {
                        'success': True,
                        'message': _('Article submitted successfully'),
                        'article_id': article.id
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as e:
            return Response(
                {'success': False, 'details': e.detail},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
