from django.urls import path
from .views import AuthorsListApiView


urlpatterns = [
    path('all/', AuthorsListApiView.as_view(), name='authors-list'),
]