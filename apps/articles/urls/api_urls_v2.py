from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.articles.views.views_v2 import ArticleViewSet, ArticleHistoryViewSet, CommentViewSet, ArticleSubmissionView, \
    ArticleWorkflowViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'article-history', ArticleHistoryViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'workflow', ArticleWorkflowViewSet, basename='workflow')
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('submit/', ArticleSubmissionView.as_view(), name='article-submit-v2')
]
