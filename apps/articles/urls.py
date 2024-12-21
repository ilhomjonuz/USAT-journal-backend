from django.urls import path
from .views import LatestArticleListView, AllArticleListView, ArticleFileDownloadView, ArticleRetrieveAPIView

urlpatterns = [
    path('latest-articles/', LatestArticleListView.as_view(), name='latest-article-list'),
    path('all-articles/', AllArticleListView.as_view(), name='all-article-list'),
    path('article/<int:id>/download/', ArticleFileDownloadView.as_view(), name='article-download'),
    path('article/<int:pk>/detail/', ArticleRetrieveAPIView.as_view(), name='article-detail'),
]
