from rest_framework import serializers
from .models import Article
from ..categories.serializers import CategorySerializer


class ArticleSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    category = CategorySerializer(read_only=True, many=False)

    class Meta:
        model = Article
        fields = '__all__'
