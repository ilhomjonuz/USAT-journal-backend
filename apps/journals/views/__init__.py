from .api_journal_issues_list import LatestJournalIssueListView, AllJournalIssueListView
from .api_journal_issue_retrieve import JournalIssueRetrieveAPIView
from .api_journal_download import JournalIssueFileDownloadView
from .template_view import (JournalListView, JournalCreateView, JournalUpdateView, JournalDeleteView,
                            JournalVolumeListView, JournalVolumeCreateView, JournalVolumeUpdateView,
                            JournalVolumeDeleteView, JournalIssueListView, JournalIssueCreateView,
                            JournalIssueUpdateView, JournalIssueDeleteView)
__all__ = [
    "LatestJournalIssueListView",
    "AllJournalIssueListView",
    "JournalIssueRetrieveAPIView",
    "JournalIssueFileDownloadView",
    "JournalListView",
    "JournalCreateView",
    "JournalUpdateView",
    "JournalDeleteView",
    "JournalVolumeListView",
    "JournalVolumeCreateView",
    "JournalVolumeUpdateView",
    "JournalVolumeDeleteView",
    "JournalIssueListView",
    "JournalIssueCreateView",
    "JournalIssueUpdateView",
    "JournalIssueDeleteView",
]