from django.urls import path

from apps.articles import views

urlpatterns = [
    path('submit/', views.ArticleSubmissionView.as_view(), name='article-submit'),
    path('latest/', views.LatestArticleListView.as_view(), name='latest-article-list'),
    path('all/', views.AllArticleListView.as_view(), name='all-article-list'),
    path('<int:id>/download/', views.ArticleFileDownloadView.as_view(), name='article-download'),
    path('<slug:slug>/detail/', views.ArticleRetrieveAPIView.as_view(), name='article-detail'),
]
