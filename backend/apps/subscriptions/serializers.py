from rest_framework import serializers
from .models import Subscription, SubscriptionItem


class SubscriptionItemSerializer(serializers.ModelSerializer):
    """Abonelik ürünü serializer"""
    product_name = serializers.CharField(source='sku.product.name', read_only=True)
    unit_price_tl = serializers.ReadOnlyField()
    line_total_tl = serializers.ReadOnlyField()
    line_total_cents = serializers.ReadOnlyField()

    class Meta:
        model = SubscriptionItem
        fields = [
            'id', 'sku', 'product_name',
            'qty', 'unit_price_tl', 'line_total_cents', 'line_total_tl',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionItemCreateSerializer(serializers.ModelSerializer):
    """Abonelik ürünü ekleme serializer"""

    class Meta:
        model = SubscriptionItem
        fields = ['sku', 'qty']

    def validate_qty(self, value):
        if value <= 0:
            raise serializers.ValidationError("Miktar 0'dan büyük olmalıdır.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """Abonelik detay serializer"""
    items = SubscriptionItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    address_title = serializers.CharField(source='address.title', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    preferred_day_display = serializers.CharField(source='get_preferred_day_display', read_only=True)
    total_items = serializers.ReadOnlyField()
    estimated_price_cents = serializers.ReadOnlyField()
    estimated_price_tl = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user_email', 'type', 'type_display',
            'preferred_day', 'preferred_day_display',
            'is_active', 'address', 'address_title',
            'total_items', 'estimated_price_cents', 'estimated_price_tl',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Abonelik liste serializer (hafif)"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    preferred_day_display = serializers.CharField(source='get_preferred_day_display', read_only=True)
    address_title = serializers.CharField(source='address.title', read_only=True)
    total_items = serializers.ReadOnlyField()
    estimated_price_tl = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'type', 'type_display',
            'preferred_day', 'preferred_day_display',
            'is_active', 'address_title', 'total_items',
            'estimated_price_tl', 'created_at'
        ]


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Abonelik oluşturma serializer"""
    items = SubscriptionItemCreateSerializer(many=True, required=False)

    class Meta:
        model = Subscription
        fields = ['type', 'preferred_day', 'address', 'items']

    def validate_preferred_day(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError("Geçerli bir gün seçiniz (1-7 arası).")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        subscription = Subscription.objects.create(**validated_data)

        # Ürünleri ekle
        for item_data in items_data:
            SubscriptionItem.objects.create(subscription=subscription, **item_data)

        return subscription


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    """Abonelik güncelleme serializer"""

    class Meta:
        model = Subscription
        fields = ['type', 'preferred_day', 'address', 'is_active']

    def validate_preferred_day(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError("Geçerli bir gün seçiniz (1-7 arası).")
        return value