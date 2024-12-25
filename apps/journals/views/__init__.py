from .api_journal_issues_list import LatestJournalIssueListView, AllJournalIssueListView
from .api_journal_issue_retrieve import JournalIssueRetrieveAPIView
from .api_journal_download import JournalIssueFileDownloadView
from .template_view import (JournalListView, JournalDetailView, JournalCreateView, JournalUpdateView, JournalDeleteView,
                            JournalVolumeListView, JournalVolumeDetailView, JournalVolumeCreateView, JournalVolumeUpdateView,
                            JournalVolumeDeleteView, JournalIssueListView, JournalIssueDetailView, JournalIssueCreateView,
                            JournalIssueUpdateView, JournalIssueDeleteView)
__all__ = [
    "LatestJournalIssueListView",
    "AllJournalIssueListView",
    "JournalIssueRetrieveAPIView",
    "JournalIssueFileDownloadView",
    "JournalListView",
    "JournalDetailView",
    "JournalCreateView",
    "JournalUpdateView",
    "JournalDeleteView",
    "JournalVolumeListView",
    "JournalVolumeDetailView",
    "JournalVolumeCreateView",
    "JournalVolumeUpdateView",
    "JournalVolumeDeleteView",
    "JournalIssueListView",
    "JournalIssueDetailView",
    "JournalIssueCreateView",
    "JournalIssueUpdateView",
    "JournalIssueDeleteView",
]