from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.cart.models import Cart
from apps.accounts.models import Address


@extend_schema(tags=['📦 Orders'])
class OrderListView(generics.ListAPIView):
    """
    Sipariş Listesi

    Kullanıcının tüm siparişlerini en yeniden eskiye doğru listeler.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(tags=['📦 Orders'])
class OrderDetailView(generics.RetrieveAPIView):
    """
    Sipariş Detayı

    Belirli bir siparişin detay bilgilerini ve içindeki ürünleri gösterir.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(tags=['📦 Orders'])
class OrderCreateView(generics.CreateAPIView):
    """
    Sipariş Oluştur

    Sepetteki ürünlerden yeni sipariş oluşturur ve sepeti temizler.

    **Ödeme Yöntemleri:**
    - `cod`: Kapıda Ödeme
    - `credit_card`: Kredi Kartı
    - `bank_transfer`: Banka Havalesi
    """
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data['address_id']
        payment_provider = serializer.validated_data['payment_provider']

        address = get_object_or_404(Address, id=address_id, user=request.user)

        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({'error': 'Sepet boş'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Sepet bulunamadı'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = cart.total_cents
        shipping = 0
        vat = int(subtotal * 0.18)
        total = subtotal + shipping + vat

        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal_cents=subtotal,
            shipping_cents=shipping,
            vat_cents=vat,
            total_cents=total,
            payment_provider=payment_provider
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                name_snapshot=cart_item.product.name,
                unit=cart_item.product.unit,
                unit_price_cents=cart_item.price_snapshot_cents,
                quantity=cart_item.quantity,
                line_total_cents=cart_item.line_total_cents
            )

        cart.clear()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)