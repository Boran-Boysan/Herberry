from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price_tl = serializers.SerializerMethodField()
    line_total_tl = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='name_snapshot', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'name_snapshot', 'product_name', 'unit', 'qty',
                 'unit_price_cents', 'unit_price_tl', 'line_total_cents', 'line_total_tl']
        read_only_fields = ['id', 'created_at']

    def get_unit_price_tl(self, obj):
        return f"{obj.unit_price_cents / 100:.2f}"

    def get_line_total_tl(self, obj):
        return f"{obj.line_total_cents / 100:.2f}"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_tl = serializers.SerializerMethodField()
    subtotal_tl = serializers.SerializerMethodField()
    shipping_tl = serializers.SerializerMethodField()
    vat_tl = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    address_title = serializers.CharField(source='address.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_display = serializers.CharField(source='get_payment_provider_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_email', 'address_title', 'status', 'status_display',
                 'payment_provider', 'payment_display', 'subtotal_cents', 'subtotal_tl',
                 'shipping_cents', 'shipping_tl', 'vat_cents', 'vat_tl',
                 'total_cents', 'total_tl', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_tl(self, obj):
        return f"{obj.total_cents / 100:.2f}"

    def get_subtotal_tl(self, obj):
        return f"{obj.subtotal_cents / 100:.2f}"

    def get_shipping_tl(self, obj):
        return f"{obj.shipping_cents / 100:.2f}"

    def get_vat_tl(self, obj):
        return f"{obj.vat_cents / 100:.2f}"


class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=True)
    payment_provider = serializers.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        default='cod'
    )

    def validate_address_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Geçerli bir adres ID'si giriniz.")
        return value