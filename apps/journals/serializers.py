from rest_framework import serializers
from .models import JournalIssue, JournalVolume, Journal

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
