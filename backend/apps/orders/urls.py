from django.urls import path
from . import views
from .payment_views import (
    CreatePaymentIntentView,
    ConfirmPaymentView,
    RefundPaymentView,
    TestCardsView
)

app_name = 'orders'

urlpatterns = [
    # Sipariş endpoints
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('create/', views.OrderCreateView.as_view(), name='order-create'),

    # 💳 Ödeme endpoints
    path('payment/create-intent/', CreatePaymentIntentView.as_view(), name='payment-create-intent'),
    path('payment/confirm/', ConfirmPaymentView.as_view(), name='payment-confirm'),
    path('payment/refund/', RefundPaymentView.as_view(), name='payment-refund'),
    path('payment/test-cards/', TestCardsView.as_view(), name='payment-test-cards'),
]