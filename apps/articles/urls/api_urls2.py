from django.urls import path

from apps.articles.views import api_article_create_view2

urlpatterns = [
    path('submit/', api_article_create_view2.ArticleSubmission2View.as_view(), name='article-submit-v2')
]
