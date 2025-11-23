from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = "Herberry Yönetim Paneli"
admin.site.site_title = "Herberry Admin"
admin.site.index_title = "Yönetim Paneli"

urlpatterns = [
    # 🏠 Landing page
    path('', views.landing_page, name='landing'),

    # 👨‍💼 Admin Panel
    path('admin/', admin.site.urls, name='admin-panel'),

    # 📚 API Documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),

    # 🔄 Swagger redirect (for backward compatibility)
    path('swagger/', RedirectView.as_view(url='/api/docs/', permanent=True), name='swagger-redirect'),

    # 🔐 Authentication & User Management
    # Endpoints: register, login, profile, addresses
    path('api/v1/auth/', include(('apps.accounts.urls', 'accounts'), namespace='auth')),

    # 🛒 Products & Categories
    # Endpoints: products list, product detail, categories, discounted products
    path('api/v1/products/', include(('apps.products.urls', 'products'), namespace='products')),

    # 🛍️ Shopping Cart
    # Endpoints: view cart, add to cart, update quantity, remove item, clear cart
    path('api/v1/cart/', include(('apps.cart.urls', 'cart'), namespace='cart')),

    # 📦 Orders
    # Endpoints: create order, order list, order detail
    path('api/v1/orders/', include(('apps.orders.urls', 'orders'), namespace='orders')),

    # 🔄 Subscriptions
    # Endpoints: subscription list, create, update, cancel
    path('api/v1/subscriptions/', include(('apps.subscriptions.urls', 'subscriptions'), namespace='subscriptions')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)