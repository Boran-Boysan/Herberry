from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class ProductSerializer(serializers.ModelSerializer):
    # Frontend icin hesaplanmis alanlar
    price_tl = serializers.ReadOnlyField()
    discounted_price_tl = serializers.ReadOnlyField()
    has_discount = serializers.ReadOnlyField()
    savings_tl = serializers.ReadOnlyField()

    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'category', 'category_name',
            'price_cents', 'price_tl',
            'discounted_price_tl',
            'has_discount',
            'discount_percentage',
            'savings_tl',
            'unit', 'unit_display',
            'stock', 'is_organic', 'is_active',
            'image', 'created_at'
        ]

    def to_representation(self, instance):
        """Frontend icin ekstra bilgiler"""
        data = super().to_representation(instance)
        data['in_stock'] = instance.stock > 0

        # Indirim varsa ekstra bilgi
        if instance.has_discount:
            data['discount_label'] = f"%{int(instance.discount_percentage)} Indirim"
            data['original_price'] = f"{instance.price_tl:.2f} TL"
            data['final_price'] = f"{instance.discounted_price_tl:.2f} TL"

        return data