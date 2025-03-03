from django.urls import path

from apps.accounts.views import api_profile_views

urlpatterns = [
    # Profile completion
    path('personal-info/', api_profile_views.PersonalInfoView.as_view(), name='personal-info'),
    path('workplace-info/', api_profile_views.WorkplaceInfoView.as_view(), name='workplace-info'),
    path('contact-info/', api_profile_views.ContactInfoView.as_view(), name='contact-info'),
    path('academic-info/', api_profile_views.AcademicInfoView.as_view(), name='academic-info'),
    path('get/', api_profile_views.UserProfileView.as_view(), name='user-profile'),
    path('update/', api_profile_views.UserUpdateProfileView.as_view(), name='user-profile-update'),
]
