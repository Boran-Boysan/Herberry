"""
Stripe Payment Service for Herberry E-commerce
Handles payment processing with Stripe
"""

import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Stripe ödeme işlemleri"""

    @staticmethod
    def create_payment_intent(amount_cents, currency='try', metadata=None):
        """
        Payment Intent oluştur

        Args:
            amount_cents: Ödeme miktarı (kuruş cinsinden)
            currency: Para birimi (try, usd, eur)
            metadata: Ekstra bilgiler (order_id, user_email vb.)

        Returns:
            dict: Payment Intent bilgileri
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'status': intent.status
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def confirm_payment(payment_intent_id):
        """
        Ödeme durumunu kontrol et

        Args:
            payment_intent_id: Stripe Payment Intent ID

        Returns:
            dict: Ödeme durumu
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'status': intent.status,
                'paid': intent.status == 'succeeded',
                'amount': intent.amount,
                'currency': intent.currency
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_checkout_session(line_items, success_url, cancel_url, metadata=None):
        """
        Stripe Checkout Session oluştur (Alternatif yöntem)

        Args:
            line_items: Ürün listesi
            success_url: Başarılı ödeme sonrası URL
            cancel_url: İptal sonrası URL
            metadata: Ekstra bilgiler

        Returns:
            dict: Checkout session bilgileri
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'session_id': session.id,
                'url': session.url
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def refund_payment(payment_intent_id, amount_cents=None):
        """
        Ödeme iadesi

        Args:
            payment_intent_id: Stripe Payment Intent ID
            amount_cents: İade miktarı (None = tam iade)

        Returns:
            dict: İade durumu
        """
        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount_cents:
                refund_data['amount'] = amount_cents

            refund = stripe.Refund.create(**refund_data)
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }


class IyzicoPaymentService:
    """
    iyzico ödeme servisi (Türkiye için alternatif)

    Not: iyzico Python SDK kurulumu gerekir:
    pip install iyzipay
    """

    def __init__(self):
        """
        iyzico konfigürasyonu
        """
        # TODO: iyzico credentials ekle
        self.api_key = settings.IYZICO_API_KEY
        self.secret_key = settings.IYZICO_SECRET_KEY
        self.base_url = settings.IYZICO_BASE_URL  # sandbox or production

    def create_payment(self, order_data):
        """
        iyzico ile ödeme oluştur

        Args:
            order_data: Sipariş bilgileri

        Returns:
            dict: Ödeme sonucu
        """
        # TODO: iyzico implementation
        pass


# Test kartları için yardımcı fonksiyon
def get_test_cards():
    """
    Stripe test kartları

    Returns:
        dict: Test kart numaraları ve açıklamaları
    """
    return {
        'success': {
            'number': '4242424242424242',
            'description': 'Başarılı ödeme'
        },
        'requires_authentication': {
            'number': '4000002500003155',
            'description': '3D Secure gerektirir'
        },
        'declined': {
            'number': '4000000000000002',
            'description': 'Reddedilir'
        },
        'insufficient_funds': {
            'number': '4000000000009995',
            'description': 'Yetersiz bakiye'
        },
        'info': {
            'exp_month': 'Gelecekteki herhangi bir ay (örn: 12)',
            'exp_year': 'Gelecekteki herhangi bir yıl (örn: 2025)',
            'cvc': 'Herhangi 3 haneli numara (örn: 123)',
            'zip': 'Herhangi 5 haneli posta kodu (örn: 12345)'
        }
    }