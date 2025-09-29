from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from products.models import Cart, CartItem
from accounts.models import Address


class OrderListView(generics.ListAPIView):
    """Kullanıcının siparişleri"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Sipariş detayı"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(generics.CreateAPIView):
    """Sepetten sipariş oluştur"""
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data['address_id']
        payment_provider = serializer.validated_data.get('payment_provider', 'cod')

        # Adresin kullanıcıya ait olduğunu kontrol et
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({'error': 'Geçersiz adres'}, status=status.HTTP_400_BAD_REQUEST)

        # Sepeti kontrol et
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({'error': 'Sepet boş'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Sepet bulunamadı'}, status=status.HTTP_400_BAD_REQUEST)

        # Sipariş oluştur
        subtotal_cents = sum(item.total_price_cents for item in cart.items.all())
        shipping_cents = 0  # Ücretsiz kargo
        vat_cents = int(subtotal_cents * 0.18)  # %18 KDV
        total_cents = subtotal_cents + shipping_cents + vat_cents

        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal_cents=subtotal_cents,
            shipping_cents=shipping_cents,
            vat_cents=vat_cents,
            total_cents=total_cents,
            payment_provider=payment_provider
        )

        # Sipariş ürünlerini oluştur
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                sku=cart_item.sku,
                name_snapshot=cart_item.sku.product.name,
                unit=cart_item.sku.unit,
                unit_price_cents=cart_item.unit_price_cents,
                qty=cart_item.qty,
                line_total_cents=cart_item.total_price_cents
            )

        # Sepeti temizle
        cart.clear()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)