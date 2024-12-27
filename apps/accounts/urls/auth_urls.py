from django.urls import path

from apps.accounts.views import auth_views

urlpatterns = [
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),
]