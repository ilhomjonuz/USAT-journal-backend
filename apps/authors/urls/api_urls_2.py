from django.urls import path

from apps.authors.views.api_authors_all_2_views import CompletedAuthorsListAPIView

urlpatterns = [
    path("completed/", CompletedAuthorsListAPIView.as_view(), name="completed-authors-list"),
]
