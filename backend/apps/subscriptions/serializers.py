from rest_framework import serializers
from .models import Subscription, SubscriptionItem
from apps.products.serializers import ProductSerializer


class SubscriptionItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    line_total_tl = serializers.ReadOnlyField()

    class Meta:
        model = SubscriptionItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'line_total_tl', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    items = SubscriptionItemSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    preferred_day_display = serializers.CharField(source='get_preferred_day_display', read_only=True)
    address_title = serializers.CharField(source='address.title', read_only=True)
    total_items = serializers.ReadOnlyField()
    estimated_price_tl = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = ['id', 'type', 'type_display', 'preferred_day', 'preferred_day_display',
                  'is_active', 'address', 'address_title', 'total_items', 'estimated_price_tl',
                  'items', 'created_at', 'updated_at']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['type', 'preferred_day', 'address']