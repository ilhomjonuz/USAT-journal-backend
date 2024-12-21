from django.urls import reverse
from rest_framework import serializers
from .models import Article
from ..authors.serializers import ArticleAuthorSerializer, ArticleRetrieveAuthorSerializer


class LatestArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'authors']


class AllArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)
    download_url = serializers.SerializerMethodField('get_download_url')

    class Meta:
        model = Article
        fields = ['id', 'title', 'authors', 'publication_date', 'views_count', 'downloads_count', 'start_page', 'end_page', 'download_url']

    def get_download_url(self, obj):
        return reverse('article-download', kwargs={'id': obj.id})


class ArticleRetrieveSerializer(serializers.ModelSerializer):
    authors = ArticleRetrieveAuthorSerializer(many=True)
    journal_issue = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'journal_issue', 'authors', 'keywords',
            'annotation', 'revised_file', 'start_page', 'end_page',
            'views_count', 'downloads_count', 'publication_date'
        ]

    def get_journal_issue(self, obj):
        from ..journals.serializers import ArticleRetrieveJournalIssueSerializer
        serializer = ArticleRetrieveJournalIssueSerializer(obj.journal_issue)
        return serializer.data


class JournalIssueRetrieveArticleSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'authors', 'start_page', 'end_page', 'views_count', 'downloads_count', 'publication_date', 'revised_file']
