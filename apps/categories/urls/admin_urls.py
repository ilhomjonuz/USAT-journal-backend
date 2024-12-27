from django.urls import path
from apps.categories.views import admin_views

urlpatterns = [
    path('categories/', admin_views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', admin_views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', admin_views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', admin_views.CategoryDeleteView.as_view(), name='category_delete'),
]
