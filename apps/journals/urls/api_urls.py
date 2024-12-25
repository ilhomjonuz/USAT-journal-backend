from django.urls import path
from apps.journals import views

urlpatterns = [
    path('latest-issues/', views.LatestJournalIssueListView.as_view(), name='latest-journal-issue-list'),
    path('all-issues/', views.AllJournalIssueListView.as_view(), name='all-journal-issue-list'),
    path('issue/<int:id>/download/', views.JournalIssueFileDownloadView.as_view(), name='journal-issue-download'),
    path('issue/<slug:slug>/detail/', views.JournalIssueRetrieveAPIView.as_view(), name='journal-issue-detail'),
]
