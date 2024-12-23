from django.urls import reverse
from rest_framework import serializers
from rest_framework.request import Request

from apps.articles.models import Article
from apps.authors.serializers import ArticleAuthorSerializer, ArticleRetrieveAuthorSerializer


class LatestArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['title', 'slug', 'authors']


class AllArticleListSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)
    download_url = serializers.SerializerMethodField('get_download_url')

    class Meta:
        model = Article
        fields = ['title', 'slug', 'authors', 'publication_date', 'views_count', 'downloads_count', 'start_page', 'end_page', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request is not None and isinstance(request, Request):
            url = reverse('article-download', kwargs={'id': obj.id})
            return request.build_absolute_uri(url)
        return None


class ArticleRetrieveSerializer(serializers.ModelSerializer):
    authors = ArticleRetrieveAuthorSerializer(many=True)
    journal_issue = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField('get_download_url')

    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'journal_issue', 'authors', 'keywords',
            'annotation', 'start_page', 'end_page',
            'views_count', 'downloads_count', 'download_url', 'publication_date'
        ]

    def get_journal_issue(self, obj) -> dict:
        from ...journals.serializers import ArticleRetrieveJournalIssueSerializer
        serializer = ArticleRetrieveJournalIssueSerializer(obj.journal_issue)
        return serializer.data

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request is not None and isinstance(request, Request):
            url = reverse('article-download', kwargs={'id': obj.id})
            return request.build_absolute_uri(url)
        return None


class JournalIssueRetrieveArticleSerializer(serializers.ModelSerializer):
    authors = ArticleAuthorSerializer(many=True)
    download_url = serializers.SerializerMethodField('get_download_url')

    class Meta:
        model = Article
        fields = ['title', 'slug', 'authors', 'start_page', 'end_page', 'views_count', 'downloads_count', 'download_url', 'publication_date']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request is not None and isinstance(request, Request):
            url = reverse('article-download', kwargs={'id': obj.id})
            return request.build_absolute_uri(url)
        return None
