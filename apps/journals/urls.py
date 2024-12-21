from django.urls import path
from .views.journal_issues import LatestJournalIssueListView, AllJournalIssueListView

urlpatterns = [
    path('latest-journal-issue/', LatestJournalIssueListView.as_view(), name='latest-journal-issue-list'),
    path('all-journal-issues/', AllJournalIssueListView.as_view(), name='all-journal-issue-list'),
]
