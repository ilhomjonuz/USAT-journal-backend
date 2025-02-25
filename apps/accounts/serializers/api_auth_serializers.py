import re

from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.authors.models import Author
import random
import string

User = get_user_model()

# Regex pattern for validating email addresses
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def generate_verification_code():
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'  # Custom field name for login

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        login = attrs.get(self.username_field)
        password = attrs.get('password')

        if not login or not password:
            raise serializers.ValidationError(_("Both login and password are required."))

        # Attempt to find user by email or username
        try:
            user = User.objects.get(Q(email__iexact=login) | Q(username__exact=login))
        except User.DoesNotExist:
            raise serializers.ValidationError({"login": _("Invalid email or username.")})

        # Authenticate user

        if not check_password(password, user.password):
            raise serializers.ValidationError({"password": _("Incorrect password.")})

        # Ensure email is verified
        if not user.is_email_verified:
            raise serializers.ValidationError({
                "email": _("Email not verified. Please verify your email."),
                "requires_verification": True
            })

        # **Muammoni to‘g‘rilash:** `attrs` ichiga `self.username_field`ni qo‘shish
        attrs[self.username_field] = user.email  # `login` sifatida email qaytariladi

        # Call parent method to generate tokens
        data = super().validate(attrs)

        # Add custom fields to response
        data.update({
            "profile_completion_step": user.profile_completion_step,
            "role": user.role
        })

        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})

        # Check if username exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": _("A user with that username already exists.")})

        # Check if email exists
        email = attrs['email'].lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": _("A user with that email already exists.")})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'].lower(),
            role=User.Role.AUTHOR
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create author profile with the same email
        Author.objects.create(
            user=user,
            email=validated_data['email'].lower()
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        verification_code = attrs.get('verification_code')

        try:
            user = User.objects.get(email=email)

            if not user.is_verification_code_valid():
                raise serializers.ValidationError({
                    "verification_code": _("Verification code has expired. Please request a new one.")
                })

            if user.verification_code != verification_code:
                raise serializers.ValidationError({
                    "verification_code": _("Invalid verification code.")
                })

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": _("User with this email does not exist.")
            })

        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AuthorPersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'country', 'city')


class AuthorWorkplaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('workplace', 'level')


class AuthorContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('phone', 'telegram_contact', 'whatsapp_contact')


class AuthorAcademicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('academic_degree', 'academic_title', 'orcid')


class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ('user', 'id')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": _("Password fields didn't match.")})
        return attrs


# 3-step password reset serializers
class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ForgotPasswordVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        verification_code = attrs.get('verification_code')

        try:
            user = User.objects.get(email=email)

            if not user.is_verification_code_valid():
                raise serializers.ValidationError({
                    "verification_code": _("Verification code has expired. Please request a new one.")
                })

            if user.verification_code != verification_code:
                raise serializers.ValidationError({
                    "verification_code": _("Invalid verification code.")
                })

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": _("User with this email does not exist.")
            })

        return attrs


class ForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": _("Password fields didn't match.")})

        return attrs

