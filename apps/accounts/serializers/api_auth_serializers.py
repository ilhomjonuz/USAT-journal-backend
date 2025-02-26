from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
import random
import string
import jwt
from django.conf import settings
from datetime import datetime

from apps.authors.models import Author

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_completion_step=User.Step.REGISTRATION
        )

        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.set_verification_code(verification_code)

        # Create empty author profile
        Author.objects.create(user=user, email=user.email)

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        verification_code = attrs.get('verification_code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("User with this email does not exist.")})

        if not user.is_verification_code_valid():
            raise serializers.ValidationError({"verification_code": _("Verification code has expired.")})

        if user.verification_code != verification_code:
            raise serializers.ValidationError({"verification_code": _("Invalid verification code.")})

        attrs['user'] = user
        return attrs


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("User with this email does not exist.")})

        attrs['user'] = user
        return attrs


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        # Determine whether the input is an email or username
        try:
            validate_email(email_or_username)
            email = email_or_username  # Valid email
        except DjangoValidationError:
            # If it's not an email, assume it's a username and fetch the corresponding email
            try:
                user = User.objects.get(username=email_or_username)
                email = user.email
            except User.DoesNotExist:
                raise serializers.ValidationError({"email_or_username": _("No user found with this username.")})

        # Authenticate using the determined email
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"password": _("Invalid credentials.")})

        if not user.is_active:
            raise serializers.ValidationError({"email_or_username": _("User account is disabled.")})

        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_data = {
            'id': obj['user'].id,
            'email': obj['user'].email,
            'username': obj['user'].username,
            'is_email_verified': obj['user'].is_email_verified,
            'profile_completion_step': obj['user'].profile_completion_step,
            'role': obj['user'].role
        }
        return user_data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": _("Password fields didn't match.")})

        return attrs

    def validate_new_password(self, value):
        # validate_password(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User with this email does not exist."))
        return value


class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        verification_code = attrs.get('verification_code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("User with this email does not exist.")})

        if not user.is_verification_code_valid():
            raise serializers.ValidationError({"verification_code": _("Verification code has expired.")})

        if user.verification_code != verification_code:
            raise serializers.ValidationError({"verification_code": _("Invalid verification code.")})

        attrs['user'] = user
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    # Updated to use reset token instead of verification code
    reset_token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": _("Password fields didn't match.")})

        reset_token = attrs.get('reset_token')

        try:
            # Decode the token to get the user ID
            payload = jwt.decode(
                reset_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = payload.get('user_id')
            exp = payload.get('exp')

            # Check if token is expired
            if datetime.fromtimestamp(exp) < datetime.now():
                raise serializers.ValidationError({"reset_token": _("Reset token has expired.")})

            user = User.objects.get(id=user_id)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            raise serializers.ValidationError({"reset_token": _("Invalid reset token.")})

        # validate_password(attrs['new_password'])
        attrs['user'] = user
        return attrs


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'country', 'city')


class WorkplaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('workplace', 'level')


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('phone', 'telegram_contact', 'whatsapp_contact')


class AcademicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('academic_degree', 'academic_title', 'orcid')


class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_email_verified', 'profile_completion_step', 'role', 'profile')

    def get_profile(self, obj):
        try:
            author = obj.profile
            return {
                'first_name': author.first_name,
                'last_name': author.last_name,
                'country': author.country,
                'city': author.city,
                'workplace': author.workplace,
                'level': author.level,
                'phone': author.phone,
                'telegram_contact': author.telegram_contact,
                'whatsapp_contact': author.whatsapp_contact,
                'academic_degree': author.academic_degree,
                'academic_title': author.academic_title,
                'orcid': author.orcid,
            }
        except Author.DoesNotExist:
            return None
