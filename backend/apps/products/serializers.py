from rest_framework import serializers
from .models import Category, Product, SKU, Stock
import os


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'created_at']


class SKUSerializer(serializers.ModelSerializer):
    price_tl = serializers.ReadOnlyField()

    class Meta:
        model = SKU
        fields = ['id', 'unit', 'barcode', 'price_cents', 'price_tl', 'vat_rate', 'is_active']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['qty_on_hand']


class ProductListSerializer(serializers.ModelSerializer):
    """Ürün listesi için basit serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'category_name', 'is_organic', 'image_url', 'is_active']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Ürün detayı için kapsamlı serializer"""
    category = CategorySerializer(read_only=True)
    skus = SKUSerializer(many=True, read_only=True)
    image_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'tags', 'is_organic',
                  'image', 'image_url', 'skus', 'is_active', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Ürün oluşturma/güncelleme için serializer"""

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'tags', 'is_organic', 'image', 'is_active']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Eski resmi sil (isteğe bağlı)
        if 'image' in validated_data and instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance