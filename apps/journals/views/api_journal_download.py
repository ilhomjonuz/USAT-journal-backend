from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.journals.models import JournalIssue


class JournalIssueFileDownloadView(APIView):
    def get(self, request, id):
        issue = get_object_or_404(JournalIssue, id=id)

        if issue.journal_file:
            # Increment the download count
            issue.downloads_count += 1
            issue.save()

            # Serve the file
            file_path = issue.journal_file.path
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{issue.journal_file.name}"'
            return response
        else:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
