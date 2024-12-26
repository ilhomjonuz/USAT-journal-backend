from django.urls import path

from apps.journals import views

urlpatterns = [
    # Journal URLs
    path('journals/', views.JournalListView.as_view(), name='journal_list'),
    path('journals/create/', views.JournalCreateView.as_view(), name='journal_create'),
    path('journals/<int:pk>/update/', views.JournalUpdateView.as_view(), name='journal_update'),
    path('journals/<int:pk>/delete/', views.JournalDeleteView.as_view(), name='journal_delete'),

    # JournalVolume URLs
    path('volumes/', views.JournalVolumeListView.as_view(), name='volume_list'),
    path('volumes/create/', views.JournalVolumeCreateView.as_view(), name='volume_create'),
    path('volumes/<int:pk>/update/', views.JournalVolumeUpdateView.as_view(), name='volume_update'),
    path('volumes/<int:pk>/delete/', views.JournalVolumeDeleteView.as_view(), name='volume_delete'),

    # JournalIssue URLs
    path('issues/', views.JournalIssueListView.as_view(), name='issue_list'),
    path('issues/create/', views.JournalIssueCreateView.as_view(), name='issue_create'),
    path('issues/<int:pk>/update/', views.JournalIssueUpdateView.as_view(), name='issue_update'),
    path('issues/<int:pk>/delete/', views.JournalIssueDeleteView.as_view(), name='issue_delete'),
]
