from django.urls import path

from apps.dashboard.views import redirect_admin

urlpatterns = [
    path('', redirect_admin, name='redirect-admin'),
]
