from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.articles.models import Article


class ArticleFileDownloadView(APIView):
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)

        if article.revised_file:
            # Increment the download count
            article.downloads_count += 1
            article.save()

            # Serve the file
            file_path = article.revised_file.path
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{article.revised_file.name}"'
            return response
        else:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
