from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart-detail'),
    path('add/', views.AddToCartView.as_view(), name='cart-add'),
    path('items/<int:item_id>/update/', views.UpdateCartItemView.as_view(), name='cart-item-update'),
    path('items/<int:item_id>/remove/', views.RemoveFromCartView.as_view(), name='cart-item-remove'),
    path('clear/', views.ClearCartView.as_view(), name='cart-clear'),
]