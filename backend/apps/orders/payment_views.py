"""
Payment Views for Herberry E-commerce
Handles Stripe payment integration
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Order
from .payment_service import StripePaymentService, get_test_cards


@extend_schema(tags=['💳 Payments'])
class CreatePaymentIntentView(APIView):
    """
    Ödeme Intent'i Oluştur

    Stripe Payment Intent oluşturur. Frontend'de kart bilgileri ile ödeme tamamlanır.

    **Test Kartları:**
    - Başarılı: 4242 4242 4242 4242
    - 3D Secure: 4000 0025 0000 3155
    - Reddedilir: 4000 0000 0000 0002

    **Diğer Bilgiler:**
    - CVV: Herhangi 3 haneli (örn: 123)
    - Son Kullanma: Gelecekteki tarih (örn: 12/25)
    - Posta Kodu: 5 haneli (örn: 12345)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')

        if not order_id:
            return Response(
                {'error': 'order_id gerekli'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Sipariş zaten ödendiyse
        if order.status == 'paid':
            return Response(
                {'error': 'Sipariş zaten ödendi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Payment Intent oluştur
        result = StripePaymentService.create_payment_intent(
            amount_cents=order.total_cents,
            currency='try',
            metadata={
                'order_id': order.id,
                'user_email': request.user.email
            }
        )

        if result['success']:
            # Payment intent ID'yi siparişe kaydet
            order.payment_ref = result['payment_intent_id']
            order.payment_provider = 'credit_card'
            order.save()

            return Response({
                'client_secret': result['client_secret'],
                'payment_intent_id': result['payment_intent_id'],
                'amount': order.total_cents,
                'currency': 'try'
            })
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['💳 Payments'])
class ConfirmPaymentView(APIView):
    """
    Ödeme Onayı

    Frontend'den ödeme tamamlandıktan sonra siparişi 'paid' durumuna geçirir.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')

        if not payment_intent_id:
            return Response(
                {'error': 'payment_intent_id gerekli'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Siparişi bul
        order = get_object_or_404(
            Order,
            payment_ref=payment_intent_id,
            user=request.user
        )

        # Stripe'dan ödeme durumunu kontrol et
        result = StripePaymentService.confirm_payment(payment_intent_id)

        if not result['success']:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ödeme başarılıysa siparişi güncelle
        if result['paid']:
            order.status = 'paid'
            order.save()

            return Response({
                'message': 'Ödeme başarılı',
                'order_id': order.id,
                'status': order.status,
                'amount_paid': result['amount'] / 100  # TL cinsinden
            })
        else:
            return Response(
                {
                    'error': 'Ödeme henüz tamamlanmadı',
                    'payment_status': result['status']
                },
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['💳 Payments'])
class RefundPaymentView(APIView):
    """
    Ödeme İadesi

    Ödenen bir siparişi iade eder.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')

        if not order_id:
            return Response(
                {'error': 'order_id gerekli'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Sipariş ödenmemiş