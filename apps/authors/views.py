from rest_framework import generics

from apps.authors.models import Author
from apps.authors.serializers import AuthorListSerializer


class AuthorsListApiView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorListSerializer
