from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Abonelik CRUD
    path('', views.SubscriptionListView.as_view(), name='subscription-list'),
    path('create/', views.SubscriptionCreateView.as_view(), name='subscription-create'),
    path('<int:id>/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('<int:id>/update/', views.SubscriptionUpdateView.as_view(), name='subscription-update'),
    path('<int:id>/delete/', views.SubscriptionDeleteView.as_view(), name='subscription-delete'),
    path('<int:id>/activate/', views.SubscriptionActivateView.as_view(), name='subscription-activate'),

    # Abonelik Ürün İşlemleri
    path('<int:subscription_id>/items/', views.SubscriptionItemListView.as_view(), name='subscription-items'),
    path('<int:subscription_id>/items/add/', views.SubscriptionItemAddView.as_view(), name='subscription-item-add'),
    path('<int:subscription_id>/items/<int:id>/update/', views.SubscriptionItemUpdateView.as_view(),
         name='subscription-item-update'),
    path('<int:subscription_id>/items/<int:id>/delete/', views.SubscriptionItemDeleteView.as_view(),
         name='subscription-item-delete'),
]