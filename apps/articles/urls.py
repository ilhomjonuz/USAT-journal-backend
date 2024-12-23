from django.urls import path

from .views import (LatestArticleListView, AllArticleListView, ArticleFileDownloadView, ArticleRetrieveAPIView,
                    ArticleSubmissionView)


urlpatterns = [
    path('submit/', ArticleSubmissionView.as_view(), name='article-submit'),
    path('latest/', LatestArticleListView.as_view(), name='latest-article-list'),
    path('all/', AllArticleListView.as_view(), name='all-article-list'),
    path('<int:id>/download/', ArticleFileDownloadView.as_view(), name='article-download'),
    path('<slug:slug>/detail/', ArticleRetrieveAPIView.as_view(), name='article-detail'),
]
