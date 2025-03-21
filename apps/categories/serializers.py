from .models import Category

from rest_framework import serializers

from ..articles.models import Article
from ..articles.serializers import JournalIssueRetrieveArticleSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code']


class JournalIssueRetrieveCategorySerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'articles']

    def get_articles(self, obj):
        request = self.context.get('request')
        journal_issue = self.context.get('journal_issue')
        articles = Article.objects.filter(
            category=obj,
            journal_issue=journal_issue,
            status='PUBLISHED'
        )
        return JournalIssueRetrieveArticleSerializer(articles, many=True, context={'request': request}).data
