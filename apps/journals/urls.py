from django.urls import path
from .views.journal_issues import LatestJournalIssueListView, JournalIssueListView

urlpatterns = [
    path('latest-journal-issue/', LatestJournalIssueListView.as_view(), name='latest-journal-issue-list'),
    path('all-journal-issues/', JournalIssueListView.as_view(), name='all-journal-issue-list'),
]
