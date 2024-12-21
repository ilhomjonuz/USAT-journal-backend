from django.urls import reverse
from rest_framework import serializers
from rest_framework.request import Request

from .models import JournalIssue
from ..categories.models import Category
from ..categories.serializers import JournalIssueRetrieveCategorySerializer


class JournalIssueListSerializer(serializers.ModelSerializer):
    journal = serializers.SerializerMethodField('read_journal')
    volume_number = serializers.SerializerMethodField('read_volume')

    class Meta:
        model = JournalIssue
        fields = ['id', 'journal', 'volume_number', 'issue_number', 'image']

    def read_journal(self, obj) -> str:
        return obj.volume.journal.name

    def read_volume(self, obj) -> str:
        return obj.volume.volume_number


class ArticleRetrieveJournalIssueSerializer(serializers.ModelSerializer):
    journal = serializers.SerializerMethodField('read_journal')
    volume_number = serializers.SerializerMethodField('read_volume')

    class Meta:
        model = JournalIssue
        fields = ['id', 'journal', 'volume_number', 'issue_number']

    def read_journal(self, obj) -> str:
        return obj.volume.journal.name

    def read_volume(self, obj) -> str:
        return obj.volume.volume_number


class JournalRetrieveSerializer(serializers.ModelSerializer):
    journal = serializers.SerializerMethodField()
    volume_number = serializers.SerializerMethodField()
    directions = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = JournalIssue
        fields = [
            'id', 'journal', 'volume_number', 'issue_number', 'image', 'start_page', 'end_page', 'directions',
            'views_count', 'downloads_count', 'publication_date', 'download_url'
        ]

    def get_journal(self, obj):
        return obj.volume.journal.name

    def get_volume_number(self, obj):
        return obj.volume.volume_number

    def get_directions(self, obj):
        request = self.context.get('request')
        categories = Category.objects.filter(
            article__journal_issue=obj,
            article__status='PUBLISHED'
        ).distinct()
        serializer = JournalIssueRetrieveCategorySerializer(categories, many=True, context={'journal_issue': obj, 'request': request})
        return serializer.data

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request is not None and isinstance(request, Request):
            url = reverse('journal-issue-download', kwargs={'id': obj.id})
            return request.build_absolute_uri(url)
        return None
