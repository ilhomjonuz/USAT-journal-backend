from django.urls import path

from apps.dashboard.views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
]
