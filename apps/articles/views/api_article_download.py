import os
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.articles.models import Article


class ArticleFileDownloadView(APIView):
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)

        if article.revised_file:
            file_path = os.path.join(settings.MEDIA_ROOT, article.revised_file.name)

            if os.path.exists(file_path):
                try:
                    # Increment the download count
                    article.increment_download_count()

                    # Serve the file
                    response = FileResponse(open(file_path, 'rb'))
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
                except IOError:
                    return Response({"error": _("Error reading file")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": _("File not found on server")}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": _("No revised file available for this article")}, status=status.HTTP_404_NOT_FOUND)


class ArticleCertificateDownloadView(APIView):
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)

        if article.publication_certificate:
            file_path = os.path.join(settings.MEDIA_ROOT, article.publication_certificate.name)

            if os.path.exists(file_path):
                try:
                    # Serve the file
                    response = FileResponse(open(file_path, 'rb'))
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
                except IOError:
                    return Response({"error": _("Error reading file")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": _("File not found on server")}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": _("No revised file available for this article")}, status=status.HTTP_404_NOT_FOUND)
