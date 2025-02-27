from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import string
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.serializers import (
    RegisterSerializer, VerifyEmailSerializer, ResendVerificationCodeSerializer,
    LoginSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer,
    PersonalInfoSerializer, WorkplaceInfoSerializer, ContactInfoSerializer, AcademicInfoSerializer,
    UserProfileSerializer
)
from apps.authors.models import Author
from apps.accounts.utils import send_verification_email, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Register with email, username, and password. A verification code will be sent to the email.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send verification email in background thread
            send_verification_email(user.email, user.verification_code)

            return Response({
                'success': True,
                'message': _("Registration successful. Please verify your email."),
            }, status=status.HTTP_201_CREATED)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify email with code",
        operation_description="Verify user's email with the code sent to their email",
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(type=openapi.TYPE_STRING),
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_email_verified = True
            user.profile_completion_step = User.Step.PERSONAL_INFO
            user.clear_verification_code()
            user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'message': _("Email verified successfully."),
                'tokens': {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'is_email_verified': user.is_email_verified,
                    'profile_completion_step': user.profile_completion_step,
                }
            }, status=status.HTTP_200_OK)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(generics.GenericAPIView):
    serializer_class = ResendVerificationCodeSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Resend verification code",
        operation_description="Resend verification code to user's email",
        responses={
            200: openapi.Response(
                description="Verification code resent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate new verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.set_verification_code(verification_code)

            # Send verification email in background thread
            send_verification_email(user.email, verification_code)

            return Response({
                'success': True,
                'message': _("Verification code resent successfully.")
            }, status=status.HTTP_200_OK)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Login user",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Login with email/username and password",
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'profile_completion_step': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
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
                description="Email not verified",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'requires_verification': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Check if email is verified
            if not user.is_email_verified:
                # Generate new verification code
                verification_code = ''.join(random.choices(string.digits, k=6))
                user.set_verification_code(verification_code)

                # Send verification email in background thread
                send_verification_email(user.email, verification_code)

                return Response({
                    'success': False,
                    'message': _("Email not verified. A new verification code has been sent."),
                    'requires_verification': True,
                    'email': user.email
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'tokens': {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'is_email_verified': user.is_email_verified,
                    'profile_completion_step': user.profile_completion_step,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout user",
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
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token')
            }
        ),
        operation_description="Blacklist the refresh token to logout",
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
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
            403: openapi.Response(
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
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({
                'success': False,
                'errors': {
                    'refresh_token':_("Refresh token is required")
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create RefreshToken instance
            token = RefreshToken(refresh_token)

            # Blacklist the token
            token.blacklist()

            return Response({
                'success': True,
                'message': _("Logout successful")
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            # Handle specific token errors
            return Response({
                'success': False,
                'errors': {
                    'refresh_token': _("Invalid or expired token")
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle other exceptions
            return Response({
                'success': False,
                'errors': {
                    'refresh_token': _("Logout failed")
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Change user password with old and new password",
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
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
            403: openapi.Response(
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'success': False,
                    'errors': {'old_password': [_("Old password is incorrect.")]}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                'success': True,
                'message': _("Password changed successfully.")
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Request password reset",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Request password reset by providing email",
        responses={
            200: openapi.Response(
                description="Password reset code sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.set_verification_code(verification_code)

            # Send password reset email in background thread
            send_password_reset_email(user.email, verification_code)

            return Response({
                'success': True,
                'message': _("Password reset code sent to your email."),
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetVerifyView(generics.GenericAPIView):
    serializer_class = PasswordResetVerifySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify password reset code",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Verify the password reset code sent to email",
        responses={
            200: openapi.Response(
                description="Password reset code verified",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'reset_token': openapi.Schema(type=openapi.TYPE_STRING),
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate a special reset token valid for 15 minutes
            payload = {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(minutes=15),
                'type': 'password_reset'
            }
            reset_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({
                'success': True,
                'message': _("Verification code is valid."),
                'reset_token': reset_token
            }, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetResendVerificationCodeView(generics.GenericAPIView):
    serializer_class = ResendVerificationCodeSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Password reset resend verification code",
        operation_description="Password reset resend verification code to user's email",
        responses={
            200: openapi.Response(
                description="Password reset verification code resent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate new verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            user.set_verification_code(verification_code)

            # Send verification email in background thread
            send_password_reset_email(user.email, verification_code)

            return Response({
                'success': True,
                'message': _("Password reset verification code resent successfully")
            }, status=status.HTTP_200_OK)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Reset password",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        operation_description="Reset password with reset token and new password",
        responses={
            200: openapi.Response(
                description="Password reset successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.clear_verification_code()
            user.save()

            return Response({
                'success': True,
                'message': _("Password reset successful.")
            }, status=status.HTTP_200_OK)

        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PersonalInfoView(generics.GenericAPIView):
    serializer_class = PersonalInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update personal information",
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
            403: openapi.Response(
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

    @swagger_auto_schema(
        operation_summary="Update workplace information",
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
            403: openapi.Response(
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

    @swagger_auto_schema(
        operation_summary="Update contact information",
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
            403: openapi.Response(
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

    @swagger_auto_schema(
        operation_summary="Update academic information",
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
            403: openapi.Response(
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
            403: openapi.Response(
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


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom Token Refresh View to properly format 400 Bad Request responses.
    """
    @swagger_auto_schema(
        operation_summary="Refresh JWT access token",
        operation_description="Send the refresh token to get a new access token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Valid refresh token")
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description="New access token")
                }
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
                                items=openapi.Schema(type=openapi.TYPE_STRING)
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Invalid or expired refresh token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                        'code': openapi.Schema(type=openapi.TYPE_STRING, description="Error code")
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Handle token refresh requests with a custom error response format.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == 400:
            # Customizing the 400 Bad Request error format
            return Response(
                {
                    "success": False,
                    "errors": response.data  # This contains the error details
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response
