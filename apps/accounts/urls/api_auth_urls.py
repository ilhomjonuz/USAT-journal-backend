from django.urls import path

from apps.accounts.views.api_auth_views import (
    RegisterView, VerifyEmailView, ResendVerificationCodeView,
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetResendVerificationCodeView,
    PasswordResetConfirmView, CustomTokenRefreshView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification-code/', ResendVerificationCodeView.as_view(), name='resend-verification-code'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),

    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password/reset/resend-verification-code/', PasswordResetResendVerificationCodeView.as_view(), name='password-reset-resend-verification-code'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
