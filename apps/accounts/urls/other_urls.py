from django.urls import path
from apps.accounts.views import other_views

urlpatterns = [
    path('toggle-dark-mode/', other_views.toggle_dark_mode, name='toggle_dark_mode'),
]
