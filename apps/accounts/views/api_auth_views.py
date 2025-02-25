from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import random
import string
import jwt

from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    AuthorPersonalInfoSerializer,
    AuthorWorkplaceInfoSerializer,
    AuthorContactInfoSerializer,
    AuthorAcademicInfoSerializer,
    AuthorProfileSerializer,
    PasswordChangeSerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifyCodeSerializer,
    ForgotPasswordResetSerializer
)
from apps.accounts.utility import send_email_in_background
from apps.authors.models import Author

User = get_user_model()


def generate_verification_code():
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user, verification_code):
    """Send verification code to user's email"""
    subject = 'Verify your email'
    message = f'Your verification code is: {verification_code}. This code will expire in 10 minutes.'
    send_email_in_background(
        subject=subject,
        message=message,
        recipient_list=[user.email]
    )


def send_password_reset_email(user, verification_code):
    """Send password reset code to user's email"""
    subject = 'Reset your password'
    message = f'Your password reset code is: {verification_code}. This code will expire in 10 minutes.'
    send_email_in_background(
        subject=subject,
        message=message,
        recipient_list=[user.email]
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and send verification code
        verification_code = generate_verification_code()
        user.set_verification_code(verification_code)
        send_verification_email(user, verification_code)

        return Response({
            "message": _("User registered successfully. Please check your email for verification code.")
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": _("Successfully logged out.")}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        user = User.objects.get(email=email)

        # Mark email as verified and clear verification code
        user.is_email_verified = True
        user.clear_verification_code()
        user.profile_completion_step = User.Step.PERSONAL_INFO
        user.save()

        # Generate tokens for automatic login
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': _('Email successfully verified'),
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'profile_completion_step': user.profile_completion_step,
            'role': user.role
        }, status=status.HTTP_200_OK)


class ResendVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'].lower())

            # Generate and send new verification code
            verification_code = generate_verification_code()
            user.set_verification_code(verification_code)
            send_verification_email(user, verification_code)

            return Response({
                "message": _("New verification code has been sent to your email.")
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "error": _("User with this email does not exist.")
            }, status=status.HTTP_404_NOT_FOUND)


class AuthorPersonalInfoView(generics.UpdateAPIView):
    serializer_class = AuthorPersonalInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Author.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = request.user
        user.profile_completion_step = User.Step.WORKPLACE_INFO
        user.save(update_fields=["profile_completion_step"])
        response.data['profile_completion_step'] = user.profile_completion_step
        return response


class AuthorWorkplaceInfoView(generics.UpdateAPIView):
    serializer_class = AuthorWorkplaceInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Author.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = request.user
        user.profile_completion_step = User.Step.CONTACT_INFO
        user.save(update_fields=["profile_completion_step"])
        response.data['profile_completion_step'] = user.profile_completion_step
        return response


class AuthorContactInfoView(generics.UpdateAPIView):
    serializer_class = AuthorContactInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Author.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = request.user
        user.profile_completion_step = User.Step.ACADEMIC_INFO
        user.save(update_fields=["profile_completion_step"])
        response.data['profile_completion_step'] = user.profile_completion_step
        return response


class AuthorAcademicInfoView(generics.UpdateAPIView):
    serializer_class = AuthorAcademicInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Author.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = request.user
        user.profile_completion_step = User.Step.COMPLETED
        user.save(update_fields=["profile_completion_step"])
        response.data['profile_completion_step'] = user.profile_completion_step
        return response


class AuthorProfileView(generics.RetrieveAPIView):
    serializer_class = AuthorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Author.objects.get(user=self.request.user)


class PasswordChangeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Check if old password is correct
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": _("Wrong password.")}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"message": _("Password changed successfully.")}, status=status.HTTP_200_OK)


# 3-step password reset views
class ForgotPasswordRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'].lower())

            # Generate and send password reset code
            verification_code = generate_verification_code()
            user.set_verification_code(verification_code)
            send_password_reset_email(user, verification_code)

            return Response({
                "message": _("Password reset code has been sent to your email.")
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # For security reasons, don't reveal that the user doesn't exist
            return Response({
                "message": _("If a user with this email exists, a password reset code has been sent.")
            }, status=status.HTTP_200_OK)


class ForgotPasswordVerifyCodeView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordVerifyCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        user = User.objects.get(email=email)

        # Mark email as verified and clear verification code
        user.is_email_verified = True
        user.clear_verification_code()
        user.save()

        # Generate tokens for automatic login
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': _('Code verified successfully.'),
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'profile_completion_step': user.profile_completion_step
        }, status=status.HTTP_200_OK)


class ForgotPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ForgotPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = request.user

            # Set new password and clear verification code
            user.set_password(serializer.validated_data['new_password'])
            user.clear_verification_code()
            user.save()

            return Response({
                "message": _("Password has been reset successfully.")
            }, status=status.HTTP_200_OK)

        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return Response({
                "error": _("Invalid or expired token. Please try again.")
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "error": _("User not found.")
            }, status=status.HTTP_404_NOT_FOUND)

