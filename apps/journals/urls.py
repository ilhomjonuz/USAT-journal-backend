from django.urls import path
from .views.journal_issues import JournalIssueListView

urlpatterns = [
    path('journal-issues/', JournalIssueListView.as_view(), name='journal-issue-list'),
]
