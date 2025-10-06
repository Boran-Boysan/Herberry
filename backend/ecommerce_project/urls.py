from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from accounts.views import custom_login_view

# Swagger - Sadece Admin kullanıcılar erişebilir
schema_view = get_schema_view(
    openapi.Info(
        title="Herberry API",
        default_version='v1',
        description="E-commerce API for organic products",
        contact=openapi.Contact(email="contact@herberry.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=False,  # Public değil
    permission_classes=[permissions.IsAdminUser],  # Sadece admin
)

urlpatterns = [
    # Ana sayfa - Özel login sayfası
    path('', custom_login_view, name='home-login'),

    # Django admin
    path('admin/', admin.site.urls),

    # Django authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # API Documentation - Sadece Admin Erişimi
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API Schema endpoints
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    # API endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/orders/', include('orders.urls')),
]

# Media files için URL pattern
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)