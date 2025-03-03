from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authors.models import Author
from apps.authors.serializers import AuthorListSerializer


class CompletedAuthorsListAPIView(generics.ListAPIView):
    serializer_class = AuthorListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        responses={
            200: AuthorListSerializer(many=True),
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
            )
        },
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Author.objects.filter(
            user__profile_completion_step="completed"
        ).exclude(user=self.request.user)
