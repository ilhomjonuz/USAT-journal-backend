from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.articles.models import Article
from apps.authors.models import Author
from apps.categories.models import Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'first_name', 'last_name', 'country', 'city', 'workplace',
            'email', 'phone', 'messenger_contact', 'academic_degree',
            'academic_title', 'orcid'
        ]


class ArticleSubmissionSerializer(serializers.ModelSerializer):
    direction_id = serializers.IntegerField(write_only=True)
    authors_data = serializers.JSONField(write_only=True)
    original_file = serializers.FileField()

    class Meta:
        model = Article
        fields = [
            'direction_id', 'title', 'keywords', 'annotation',
            'authors_data', 'original_file'
        ]

    def validate_direction_id(self, value):
        if not value:
            raise serializers.ValidationError(_('Direction id is required'))

        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError(_('Invalid direction id'))

        return value

    def create(self, validated_data):
        authors_data = validated_data.pop('authors_data')
        direction_id = validated_data.pop('direction_id')
        category = Category.objects.get(id=direction_id)
        validated_data['category'] = category
        article = Article.objects.create(**validated_data)

        for author_data in authors_data:
            email = author_data.get('email')
            author, created = Author.objects.get_or_create(email=email, defaults=author_data)

            if not created:
                # Update existing author's information
                for key, value in author_data.items():
                    setattr(author, key, value)
                author.save()

            article.authors.add(author)

        return article
