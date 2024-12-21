from django.urls import path
from .views import LatestJournalIssueListView, AllJournalIssueListView, JournalIssueRetrieveAPIView, JournalIssueFileDownloadView

urlpatterns = [
    path('latest-issues/', LatestJournalIssueListView.as_view(), name='latest-journal-issue-list'),
    path('all-issues/', AllJournalIssueListView.as_view(), name='all-journal-issue-list'),
    path('issue/<int:id>/download/', JournalIssueFileDownloadView.as_view(), name='journal-issue-download'),
    path('issue/<int:pk>/detail/', JournalIssueRetrieveAPIView.as_view(), name='journal-issue-detail'),
]
