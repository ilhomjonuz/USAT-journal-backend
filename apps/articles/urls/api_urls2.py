from django.urls import path

from apps.articles.views import api_article_create_view2
from apps.articles.views.api_article_download import ArticleCertificateDownloadView

urlpatterns = [
    path('submit/', api_article_create_view2.ArticleSubmission2View.as_view(), name='article-submit-v2'),
    path('certificate/<int:id>/download/', ArticleCertificateDownloadView.as_view(), name='article-certificate-download'),
]
