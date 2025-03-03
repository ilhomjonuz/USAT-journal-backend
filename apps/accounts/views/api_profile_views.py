from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.serializers.api_profile_serializers import UserProfileSerializer, AuthorSerializer, \
    PersonalInfoSerializer, WorkplaceInfoSerializer, ContactInfoSerializer, AcademicInfoSerializer
from apps.authors.models import Author


User = get_user_model()


class PersonalInfoView(generics.GenericAPIView):
    serializer_class = PersonalInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Update personal information(register step1)",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Update user's personal information (first_name, last_name, country, city)",
        responses={
            200: openapi.Response(
                description="Personal information updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, format='id'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, format='username'),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                          "completed"]
                                ),
                                'role': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                                ),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                                        'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                        'level': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
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
            )
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            author = Author.objects.create(user=user, email=user.email)

        serializer = self.get_serializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Update user profile completion step
            user.profile_completion_step = User.Step.WORKPLACE_INFO
            user.save()

            # Return updated user profile
            user_serializer = UserProfileSerializer(user)

            return Response({
                'success': True,
                'message': _("Personal information updated successfully."),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class WorkplaceInfoView(generics.GenericAPIView):
    serializer_class = WorkplaceInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Update workplace information(register step2)",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Update user's workplace information (workplace, level)",
        responses={
            200: openapi.Response(
                description="Workplace information updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, format='id'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, format='username'),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                          "completed"]
                                ),
                                'role': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                                ),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                                        'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                        'level': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
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
            )
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            author = Author.objects.create(user=user, email=user.email)

        serializer = self.get_serializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Update user profile completion step
            user.profile_completion_step = User.Step.CONTACT_INFO
            user.save()

            # Return updated user profile
            user_serializer = UserProfileSerializer(user)

            return Response({
                'success': True,
                'message': _("Workplace information updated successfully."),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContactInfoView(generics.GenericAPIView):
    serializer_class = ContactInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Update contact information(register step3)",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Update user's contact information (phone, telegram_contact, whatsapp_contact)",
        responses={
            200: openapi.Response(
                description="Contact information updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, format='id'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, format='username'),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                          "completed"]
                                ),
                                'role': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                                ),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                                        'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                        'level': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
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
            )
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            author = Author.objects.create(user=user, email=user.email)

        serializer = self.get_serializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Update user profile completion step
            user.profile_completion_step = User.Step.ACADEMIC_INFO
            user.save()

            # Return updated user profile
            user_serializer = UserProfileSerializer(user)

            return Response({
                'success': True,
                'message': _("Contact information updated successfully."),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AcademicInfoView(generics.GenericAPIView):
    serializer_class = AcademicInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Update academic information(register step4)",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Update user's academic information (academic_degree, academic_title, orcid)",
        responses={
            200: openapi.Response(
                description="Academic information updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, format='id'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, format='username'),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                          "completed"]
                                ),
                                'role': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                                ),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                                        'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                        'level': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
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
            )
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            author = Author.objects.create(user=user, email=user.email)

        serializer = self.get_serializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Update user profile completion step
            user.profile_completion_step = User.Step.COMPLETED
            user.save()

            # Return updated user profile
            user_serializer = UserProfileSerializer(user)

            return Response({
                'success': True,
                'message': _("Academic information updated successfully."),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Get user profile",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Get current user's profile information",
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'profile_completion_step': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                  "completed"]
                        ),
                        'role': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                        ),
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'country': openapi.Schema(type=openapi.TYPE_STRING),
                                'city': openapi.Schema(type=openapi.TYPE_STRING),
                                'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                'level': openapi.Schema(type=openapi.TYPE_STRING),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                            }
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
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class UserUpdateProfileView(generics.GenericAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Update user profile(author information)",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Update user's all information (first_name, last_name, country, city, workplace, level, phone, telegram_contact, whatsapp_contact, academic_degree, academic_title, orcid)",
        responses={
            200: openapi.Response(
                description="Academic information updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, format='id'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, format='username'),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["registration", "personal_info", "workplace_info", "contact_info", "academic_info",
                                          "completed"]
                                ),
                                'role': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=["author", "editor", "reviewer", "secretary", "deputy_editor", "admin"]
                                ),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'country': openapi.Schema(type=openapi.TYPE_STRING),
                                        'city': openapi.Schema(type=openapi.TYPE_STRING),
                                        'workplace': openapi.Schema(type=openapi.TYPE_STRING),
                                        'level': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'telegram_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'whatsapp_contact': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_degree': openapi.Schema(type=openapi.TYPE_STRING),
                                        'academic_title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'orcid': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            }
                        )
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
            )
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            author = Author.objects.create(user=user, email=user.email)

        serializer = self.get_serializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Update user profile completion step
            user.profile_completion_step = User.Step.COMPLETED
            user.save()

            # Return updated user profile
            user_serializer = UserProfileSerializer(user)

            return Response({
                'success': True,
                'message': _("User profile information updated successfully."),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
