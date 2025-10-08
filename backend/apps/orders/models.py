from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Oluşturuldu'),
        ('paid', 'Ödendi'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Kapıda Ödeme'),
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Banka Havalesi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey('accounts.Address', on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_ref = models.CharField(max_length=100, blank=True, null=True)

    # Fiyat bilgileri (cent cinsinden)
    subtotal_cents = models.PositiveIntegerField(default=0)
    shipping_cents = models.PositiveIntegerField(default=0)
    discount_cents = models.PositiveIntegerField(default=0)
    vat_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='TRY')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.email}"


class OrderItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('gr', 'Gram'),
        ('lt', 'Litre'),
        ('adet', 'Adet'),
        ('paket', 'Paket'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku = models.ForeignKey('products.SKU', on_delete=models.CASCADE)

    # Snapshot verileri (sipariş anındaki bilgiler)
    name_snapshot = models.CharField(max_length=200)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    unit_price_cents = models.PositiveIntegerField()
    qty = models.PositiveIntegerField()
    line_total_cents = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name_snapshot} x {self.qty}"
