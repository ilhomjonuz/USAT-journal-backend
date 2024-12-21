from rest_framework import serializers
from .models import JournalIssue, JournalVolume, Journal


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



class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'name']

class JournalVolumeSerializer(serializers.ModelSerializer):
    journal = JournalSerializer()

    class Meta:
        model = JournalVolume
        fields = ['id', 'journal', 'volume_number', 'year']

class JournalIssueSerializer(serializers.ModelSerializer):
    volume = JournalVolumeSerializer()
    page_range = serializers.CharField(read_only=True)
    total_pages = serializers.IntegerField(read_only=True)

    class Meta:
        model = JournalIssue
        fields = ['id', 'volume', 'issue_number', 'publication_date',
                  'is_published', 'views_count', 'page_range', 'total_pages']
