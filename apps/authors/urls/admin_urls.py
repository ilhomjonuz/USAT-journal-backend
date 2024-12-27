from django.urls import path

from apps.authors.views import admin_views

urlpatterns = [
    path('authors/', admin_views.AuthorListView.as_view(), name='author_list'),
    path('authors/create/', admin_views.AuthorCreateView.as_view(), name='author_create'),
    path('authors/<int:pk>/update/', admin_views.AuthorUpdateView.as_view(), name='author_update'),
    path('authors/<int:pk>/delete/', admin_views.AuthorDeleteView.as_view(), name='author_delete'),
]