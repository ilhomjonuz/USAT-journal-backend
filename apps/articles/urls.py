from django.urls import path
from .views import LatestArticleListView, AllArticleListView

urlpatterns = [
    path('latest-articles/', LatestArticleListView.as_view(), name='latest-article-list'),
    path('all-articles/', AllArticleListView.as_view(), name='all-article-list'),
]
