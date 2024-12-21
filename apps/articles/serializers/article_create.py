from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.articles.models import Article
from apps.authors.models import Author
from apps.categories.models import Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'first_name', 'last_name', 'country', 'city',
            'workplace', 'email', 'phone', 'messenger_contact',
            'academic_degree', 'academic_title', 'orcid'
        ]

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError(_("Email is required."))
        return value.lower()


class ArticleSubmissionSerializer(serializers.ModelSerializer):
    direction_id = serializers.IntegerField(write_only=True)
    authors_data = AuthorSerializer(many=True, write_only=True)

    class Meta:
        model = Article
        fields = [
            'direction_id', 'title', 'keywords', 'annotation',
            'original_file', 'authors_data'
        ]

    def create(self, validated_data):
        authors_data = validated_data.pop('authors_data')
        direction_id = validated_data.pop('direction_id')
        validated_data['category'] = direction_id
        article = Article.objects.create(**validated_data)

        for author_data in authors_data:
            # Try to get the existing author
            author, created = Author.objects.get_or_create(
                email=author_data['email']
            )

            if not created:  # If the author already exists, update their details
                for key, value in author_data.items():
                    setattr(author, key, value)
                author.save()

            # Associate the author with the article
            article.authors.add(author)

        return article

    def validate_direction_id(self, value):
        if not value:
            raise serializers.ValidationError(_("Direction ID is required."))
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError(_("Direction not found."))
        return value
