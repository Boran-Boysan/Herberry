from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Subscription, SubscriptionItem
from .serializers import SubscriptionSerializer


@api_view(['GET'])
def subscription_list(request):
    """Kullanıcının abonelikleri"""
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def subscription_detail(request, subscription_id):
    """Abonelik detayı"""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)


@api_view(['POST'])
def create_subscription(request):
    """Yeni abonelik oluştur"""
    subscription_type = request.data.get('type')
    address_id = request.data.get('address_id')
    preferred_day = request.data.get('preferred_day')

    if not all([subscription_type, address_id]):
        return Response({
            'error': 'Abonelik türü ve adres gerekli'
        }, status=status.HTTP_400_BAD_REQUEST)

    subscription = Subscription.objects.create(
        user=request.user,
        type=subscription_type,
        address_id=address_id,
        preferred_day=preferred_day
    )

    return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_subscription(request, subscription_id):
    """Abonelik güncelle"""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    is_active = request.data.get('is_active')
    preferred_day = request.data.get('preferred_day')

    if is_active is not None:
        subscription.is_active = is_active

    if preferred_day is not None:
        subscription.preferred_day = preferred_day

    subscription.save()

    return Response(SubscriptionSerializer(subscription).data)