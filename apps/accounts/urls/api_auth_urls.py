from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.api_auth_views import (
    CustomTokenObtainPairView,
    RegisterView,
    LogoutView,
    VerifyEmailView,
    ResendVerificationView,
    AuthorPersonalInfoView,
    AuthorWorkplaceInfoView,
    AuthorContactInfoView,
    AuthorAcademicInfoView,
    AuthorProfileView,
    PasswordChangeView,
    ForgotPasswordRequestView,
    ForgotPasswordVerifyCodeView,
    ForgotPasswordResetView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email verification
    path('email-verify/', VerifyEmailView.as_view(), name='email-verify'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),

    # Profile completion steps
    path('profile/personal-info/', AuthorPersonalInfoView.as_view(), name='personal-info'),
    path('profile/workplace-info/', AuthorWorkplaceInfoView.as_view(), name='workplace-info'),
    path('profile/contact-info/', AuthorContactInfoView.as_view(), name='contact-info'),
    path('profile/academic-info/', AuthorAcademicInfoView.as_view(), name='academic-info'),
    path('profile/', AuthorProfileView.as_view(), name='user-profile'),

    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/forgot/request/', ForgotPasswordRequestView.as_view(), name='forgot-password-request'),
    path('password/forgot/verify/', ForgotPasswordVerifyCodeView.as_view(), name='forgot-password-verify'),
    path('password/forgot/reset/', ForgotPasswordResetView.as_view(), name='forgot-password-reset'),
]

