from django.urls import path

from apps.authors.views import api_views

urlpatterns = [
    path('all/', api_views.AuthorsListApiView.as_view(), name='authors-list'),
]