from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Olusturuldu'),
        ('paid', 'Odendi'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'Iptal Edildi'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Kapida Odeme'),
        ('credit_card', 'Kredi Karti'),
        ('bank_transfer', 'Banka Havalesi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             verbose_name="Kullanici")
    address = models.ForeignKey('accounts.Address', on_delete=models.PROTECT, verbose_name="Adres")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Durum")
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod',
                                        verbose_name="Odeme Yontemi")
    payment_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="Odeme Referansi")

    subtotal_cents = models.PositiveIntegerField(default=0, verbose_name="Ara Toplam (Kurus)")
    shipping_cents = models.PositiveIntegerField(default=0, verbose_name="Kargo (Kurus)")
    vat_cents = models.PositiveIntegerField(default=0, verbose_name="KDV (Kurus)")
    total_cents = models.PositiveIntegerField(default=0, verbose_name="Toplam (Kurus)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Guncelleme Tarihi")

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = "Siparis"
        verbose_name_plural = "Siparisler"

    def __str__(self):
        return f"Siparis #{self.id} - {self.user.email}"

    @property
    def total_tl(self):
        from apps.products.utils import to_tl
        return to_tl(self.total_cents)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Siparis")
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, verbose_name="Urun")

    name_snapshot = models.CharField(max_length=200, verbose_name="Urun Adi")
    unit = models.CharField(max_length=10, verbose_name="Birim")
    unit_price_cents = models.PositiveIntegerField(verbose_name="Birim Fiyat (Kurus)")
    quantity = models.PositiveIntegerField(verbose_name="Miktar")
    line_total_cents = models.PositiveIntegerField(verbose_name="Satir Toplami (Kurus)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    class Meta:
        db_table = 'order_items'
        verbose_name = "Siparis Urunu"
        verbose_name_plural = "Siparis Urunleri"

    def __str__(self):
        return f"{self.name_snapshot} x {self.quantity}"

    @property
    def line_total_tl(self):
        from apps.products.utils import to_tl
        return to_tl(self.line_total_cents)