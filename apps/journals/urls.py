from django.urls import path
from .views import LatestJournalIssueListView, AllJournalIssueListView, JournalIssueRetrieveAPIView

urlpatterns = [
    path('latest-journal-issue/', LatestJournalIssueListView.as_view(), name='latest-journal-issue-list'),
    path('all-journal-issues/', AllJournalIssueListView.as_view(), name='all-journal-issue-list'),
    path('journal-issue/<int:pk>/detail/', JournalIssueRetrieveAPIView.as_view(), name='journal-issue-detail'),
]
