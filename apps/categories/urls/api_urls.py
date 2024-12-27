from django.urls import path

from apps.categories.views.api_views import CategoryListView

urlpatterns = [
    path('all/', CategoryListView.as_view(), name='directions-list'),
]