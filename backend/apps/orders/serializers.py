from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total_tl = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'name_snapshot', 'unit', 'quantity',
                  'unit_price_cents', 'line_total_cents', 'line_total_tl']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_tl = serializers.ReadOnlyField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    address_title = serializers.CharField(source='address.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_email', 'address_title', 'status', 'status_display',
                  'payment_provider', 'subtotal_cents', 'shipping_cents', 'vat_cents',
                  'total_cents', 'total_tl', 'items', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_provider = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, default='cod')