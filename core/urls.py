from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path('api/docs/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api-auth/', include('rest_framework.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    prefix_default_language=False
)