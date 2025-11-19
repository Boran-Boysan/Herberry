from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Herberry Yönetim Paneli"
admin.site.site_title = "Herberry Admin"
admin.site.index_title = "Yönetim Paneli"

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.accounts.urls')),
        path('products/', include('apps.products.urls')),
        path('cart/', include('apps.cart.urls')),
        path('orders/', include('apps.orders.urls')),
        path('subscriptions/', include('apps.subscriptions.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)