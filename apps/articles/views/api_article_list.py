from rest_framework import generics

from apps.articles.models import Article
from apps.articles.serializers import LatestArticleListSerializer, AllArticleListSerializer


class LatestArticleListView(generics.ListAPIView):
    serializer_class = LatestArticleListSerializer
    queryset = Article.objects.filter(status='PUBLISHED', journal_issue__is_published=True).order_by('-publication_date')[:4]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AllArticleListView(generics.ListAPIView):
    serializer_class = AllArticleListSerializer
    queryset = Article.objects.filter(status='PUBLISHED', journal_issue__is_published=True).order_by('-publication_date')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
