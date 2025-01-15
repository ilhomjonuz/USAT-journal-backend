from rest_framework import generics
from django.db.models import Exists, OuterRef
from apps.authors.models import Author
from apps.authors.serializers import AuthorListSerializer
from apps.articles.models import Article

class AuthorsListApiView(generics.ListAPIView):
    serializer_class = AuthorListSerializer

    def get_queryset(self):
        return Author.objects.filter(
            Exists(
                self.get_articles_queryset().filter(authors=OuterRef('pk'))
            )
        )

    def get_articles_queryset(self):
        return Article.objects.filter(status='PUBLISHED')
