from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Admin site özelleştirmesi
admin.site.site_header = "🍓 Herberry Yönetim Paneli"
admin.site.site_title = "Herberry Admin"
admin.site.index_title = "Yönetim Paneli"
admin.site.site_url = "/"

schema_view = get_schema_view(
    openapi.Info(
        title="Herberry API",
        default_version='v1',
        description="E-commerce API for organic products",
        contact=openapi.Contact(email="contact@herberry.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Landing Page (Ana Sayfa)
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    # Django admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API Schema endpoints
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    # API endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/subscriptions/', include('subscriptions.4urls')),
]

# Media files için URL pattern
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

