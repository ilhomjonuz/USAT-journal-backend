from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.authors.models import Author

User = get_user_model()


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
            return AuthorSerializer(author).data
        except Author.DoesNotExist:
            return None


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'country', 'city', 'workplace', 'level', 'phone', 'telegram_contact', 'whatsapp_contact', 'academic_degree', 'academic_title', 'orcid']
