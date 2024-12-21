from django.urls import path

from .views import CategoryListView

urlpatterns = [
    path('all/', CategoryListView.as_view(), name='directions-list'),
]