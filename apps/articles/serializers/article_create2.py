from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.articles.models import Article
from apps.authors.models import Author
from apps.categories.models import Category


class ArticleSubmission2Serializer(serializers.ModelSerializer):
    direction_id = serializers.IntegerField(write_only=True, required=True)
    authors_data = serializers.JSONField(write_only=True, required=False)
    anti_plagiarism_certificate = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Accepted file types: .pdf'
    )
    original_file = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'odt'])],
        help_text='Article original file, types: doc, docx, odt'
    )

    class Meta:
        model = Article
        fields = [
            'direction_id', 'title', 'keywords', 'annotation', 'references',
            'authors_data', 'anti_plagiarism_certificate', 'original_file'
        ]

    def validate_direction_id(self, value):
        if not value:
            raise serializers.ValidationError(_('Direction id is required'))

        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError(_('Invalid direction id'))

        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            raise NotFound({"user": _("User profile does not exist. Please create a profile first.")})

        authors_data = validated_data.pop('authors_data', [])
        direction_id = validated_data.pop('direction_id')

        try:
            # Transaksiya boshlanishi
            with transaction.atomic():
                category = Category.objects.get(id=direction_id)
                validated_data['category'] = category
                article = Article.objects.create(**validated_data)

                article.authors.add(author)

                for author_data in authors_data:
                    author_id = author_data.get('author_id')
                    try:
                        author = Author.objects.get(id=author_id)
                        article.authors.add(author)
                    except Author.DoesNotExist:
                        # Agar Author topilmasa, transaksiya bekor qilinadi
                        raise NotFound({"detail": _(f"Author with id {author_id} not found.")})

                return article

        except Exception as e:
            # Boshqa xatoliklar uchun
            raise e
