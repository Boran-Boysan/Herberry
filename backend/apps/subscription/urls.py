from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_list, name='subscription-list'),
    path('<int:subscription_id>/', views.subscription_detail, name='subscription-detail'),
    path('create/', views.create_subscription, name='create-subscription'),
    path('<int:subscription_id>/update/', views.update_subscription, name='update-subscription'),
]