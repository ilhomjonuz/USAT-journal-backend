from rest_framework import serializers
from .models import Article
from ..authors.serializers import ArticleAuthorSerializer, ArticleRetrieveAuthorSerializer
from ..journals.serializers import ArticleRetrieveJournalIssueSerializer


class LatestArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'authors']


class AllArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'authors', 'publication_date', 'views_count', 'downloads_count', 'start_page', 'end_page', 'revised_file']


class ArticleRetrieveSerializer(serializers.ModelSerializer):
    authors = ArticleRetrieveAuthorSerializer(many=True)
    journal_issue = ArticleRetrieveJournalIssueSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'journal_issue', 'authors', 'keywords', 'annotation', 'revised_file', 'start_page', 'end_page', 'views_count', 'downloads_count', 'publication_date']
