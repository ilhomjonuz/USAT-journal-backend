from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.dashboard.views import redirect_dashboard

schema_view = get_schema_view(
   openapi.Info(
      title="USAT journal API",
      default_version='v1',
      description="USAT journal API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="ilhomjonpersonal@gmail.com"),
      license=openapi.License(name="USAT License"),
   ),
   public=False,
   permission_classes=[permissions.IsAuthenticated,],
)

urlpatterns = [
    path('', redirect_dashboard, name='redirect-dashboard'),
    path('accounts/', include('apps.accounts.urls.other_urls')),
    path('api/docs/swagger<format>/', login_required(schema_view.without_ui(cache_timeout=0)), name='schema-json'),
    path('api/docs/swagger/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    path('api/docs/redoc/', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    path('api-auth/', include('rest_framework.urls')),

    path('api/auth/v2/', include('apps.accounts.urls.api_auth_urls')),
    path('api/profile/v2/', include('apps.accounts.urls.api_profile_urls')),
    path('api/journals/v1/', include('apps.journals.urls.api_urls')),
    path('api/articles/v1/', include('apps.articles.urls.api_urls')),
    path('api/articles/v2/', include('apps.articles.urls.api_urls2')),
    path('api/authors/v1/', include('apps.authors.urls.api_urls')),
    path('api/authors/v2/', include('apps.authors.urls.api_urls_2')),
    path('api/directions/v1/', include('apps.categories.urls.api_urls')),
]

urlpatterns += i18n_patterns(
    path('dashboard/', include('apps.dashboard.urls')),  # Dashboard uchun
    path('accounts/', include('apps.accounts.urls.auth_urls')),
    path('admin/', admin.site.urls),  # Admin uchun
    path('journal-admin/', include('apps.journals.urls.admin_urls')),
    path('article-admin/', include('apps.articles.urls.admin_urls')),
    path('category-admin/', include('apps.categories.urls.admin_urls')),
    path('author-admin/', include('apps.authors.urls.admin_urls'))
    # prefix_default_language=False
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.USE_I18N:
    urlpatterns += [
        path('i18n/', include('django.conf.urls.i18n')),
    ]
