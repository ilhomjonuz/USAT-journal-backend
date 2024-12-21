from rest_framework import serializers

from .models import Author


class ArticleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name']


class ArticleRetrieveAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'country', 'city', 'workplace', 'academic_degree', 'academic_title']
