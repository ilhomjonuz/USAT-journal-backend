from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.authors.models import Author
from apps.authors.serializers import AuthorListSerializer


class CompletedAuthorsListAPIView(generics.ListAPIView):
    serializer_class = AuthorListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Foydalanuvchidan boshqa barcha toʻliq profilga ega mualliflarni olish"""
        return Author.objects.filter(
            user__profile_completion_step="completed"
        ).exclude(user=self.request.user)
