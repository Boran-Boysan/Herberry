from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Kategoriler
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    # Urunler
    path('', views.ProductListView.as_view(), name='product-list'),
    path('discounted/', views.DiscountedProductsView.as_view(), name='discounted-products'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Admin
    path('admin/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('admin/<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('admin/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
]