from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionListView.as_view(), name='subscription-list'),
    path('create/', views.SubscriptionCreateView.as_view(), name='subscription-create'),
    path('<int:id>/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('<int:id>/update/', views.SubscriptionUpdateView.as_view(), name='subscription-update'),
    path('<int:id>/delete/', views.SubscriptionDeleteView.as_view(), name='subscription-delete'),
]