from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from apps.products.models import Product


@extend_schema(tags=['🛍️ Shopping Cart'])
class CartView(generics.RetrieveAPIView):
    """
    Sepeti Görüntüle

    Kullanıcının sepetini ve içindeki ürünleri gösterir.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


@extend_schema(tags=['🛍️ Shopping Cart'])
class AddToCartView(APIView):
    """
    Sepete Ürün Ekle

    Sepete yeni ürün ekler veya mevcut ürünün miktarını artırır.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock < quantity:
            return Response({'error': 'Yetersiz stok'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


@extend_schema(tags=['🛍️ Shopping Cart'])
class UpdateCartItemView(APIView):
    """
    Sepet Ürün Miktarını Güncelle

    Sepetteki bir ürünün miktarını günceller.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = serializer.validated_data['quantity']

        if cart_item.product.stock < quantity:
            return Response({'error': 'Yetersiz stok'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart_item.cart).data)


@extend_schema(tags=['🛍️ Shopping Cart'])
class RemoveFromCartView(APIView):
    """
    Sepetten Ürün Çıkar

    Sepetten belirli bir ürünü tamamen kaldırır.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data)


@extend_schema(tags=['🛍️ Shopping Cart'])
class ClearCartView(APIView):
    """
    Sepeti Temizle

    Sepetteki tüm ürünleri siler.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.clear()
        return Response({'message': 'Sepet temizlendi'}, status=status.HTTP_200_OK)