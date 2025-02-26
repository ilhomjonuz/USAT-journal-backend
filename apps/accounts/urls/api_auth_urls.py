from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.api_auth_views import (
    RegisterView, VerifyEmailView, ResendVerificationCodeView,
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetConfirmView,
    PersonalInfoView, WorkplaceInfoView, ContactInfoView, AcademicInfoView,
    UserProfileView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification-code/', ResendVerificationCodeView.as_view(), name='resend-verification-code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Profile completion
    path('profile/personal-info/', PersonalInfoView.as_view(), name='personal-info'),
    path('profile/workplace-info/', WorkplaceInfoView.as_view(), name='workplace-info'),
    path('profile/contact-info/', ContactInfoView.as_view(), name='contact-info'),
    path('profile/academic-info/', AcademicInfoView.as_view(), name='academic-info'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
