from django.urls import path
from .views import toggle_dark_mode

urlpatterns = [
    path('toggle-dark-mode/', toggle_dark_mode, name='toggle_dark_mode'),
]
