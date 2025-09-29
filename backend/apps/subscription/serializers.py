from rest_framework import serializers
from .models import Subscription, SubscriptionItem


class SubscriptionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_product_name(self, obj):
        return obj.sku.product.name


class SubscriptionSerializer(serializers.ModelSerializer):
    items = SubscriptionItemSerializer(many=True, read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user_email(self, obj):
        return obj.user.email