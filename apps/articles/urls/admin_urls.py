from django.urls import path

from apps.articles import views

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('<int:pk>/download/<str:file_type>/', views.download_file, name='article_download_file'),
    path('action/', views.article_action, name='article_action'),
]