from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.core.exceptions import ValidationError
from apps.articles.models import Article
from apps.authors.models import Author, DEGREE_CHOICES, ACADEMIC_TITLE_CHOICES
from apps.categories.models import Category

class AuthorSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    workplace = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    messenger_contact = serializers.CharField(max_length=100)
    academic_degree = serializers.ChoiceField(choices=DEGREE_CHOICES)
    academic_title = serializers.ChoiceField(choices=ACADEMIC_TITLE_CHOICES)
    orcid = serializers.CharField(max_length=20, required=False)

class ArticleSubmissionSerializer(serializers.ModelSerializer):
    authors_data = AuthorSerializer(many=True)
    direction_id = serializers.IntegerField()
    original_file = serializers.FileField(required=True)

    class Meta:
        model = Article
        fields = ['direction_id', 'title', 'keywords', 'annotation', 'authors_data', 'original_file']

    def validate_direction_id(self, value):
        """Validate that the direction_id exists in Category."""
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise ValidationError(_("Invalid direction_id"))
        return value

    def create(self, validated_data):
        authors_data = validated_data.pop('authors_data')
        direction_id = validated_data.pop('direction_id')
        original_file = validated_data.pop('original_file')

        article = Article.objects.create(
            category_id=direction_id,
            original_file=original_file,
            **validated_data
        )

        for author_data in authors_data:
            author, created = Author.objects.update_or_create(
                email=author_data['email'],
                defaults=author_data
            )
            article.authors.add(author)

        article.save()
        return article
