from django.db import models
from django.conf import settings


class Subscription(models.Model):
    """Kullanıcı abonelikleri"""

    TYPE_CHOICES = [
        ('veg_box', 'Sebze Kutusu'),
        ('fruit_box', 'Meyve Kutusu'),
        ('custom_box', 'Özel Kutu'),
    ]

    WEEKDAY_CHOICES = [
        (1, 'Pazartesi'),
        (2, 'Salı'),
        (3, 'Çarşamba'),
        (4, 'Perşembe'),
        (5, 'Cuma'),
        (6, 'Cumartesi'),
        (7, 'Pazar'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Kullanıcı"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Abonelik Tipi"
    )
    preferred_day = models.SmallIntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name="Tercih Edilen Gün"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?"
    )
    address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.RESTRICT,
        verbose_name="Teslimat Adresi"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'subscriptions'
        verbose_name = "Abonelik"
        verbose_name_plural = "Abonelikler"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['preferred_day']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()} ({self.get_preferred_day_display()})"

    @property
    def total_items(self):
        """Abonelikteki toplam ürün sayısı"""
        return sum(item.qty for item in self.items.all())

    @property
    def estimated_price_cents(self):
        """Tahmini fiyat (kuruş)"""
        return sum(item.qty * item.sku.price_cents for item in self.items.all())

    @property
    def estimated_price_tl(self):
        """Tahmini fiyat (TL)"""
        return self.estimated_price_cents / 100


class SubscriptionItem(models.Model):
    """Abonelik kalemleri - her abonelikteki ürünler"""

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Abonelik"
    )
    sku = models.ForeignKey(
        'products.SKU',
        on_delete=models.RESTRICT,
        verbose_name="Ürün (SKU)"
    )
    qty = models.PositiveIntegerField(
        default=1,
        verbose_name="Miktar"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'subscription_items'
        verbose_name = "Abonelik Ürünü"
        verbose_name_plural = "Abonelik Ürünleri"
        ordering = ['id']
        unique_together = ['subscription', 'sku']
        indexes = [
            models.Index(fields=['subscription']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.subscription.user.email} - {self.sku.product.name} x {self.qty}"

    @property
    def line_total_cents(self):
        """Satır toplamı (kuruş)"""
        return self.qty * self.sku.price_cents

    @property
    def line_total_tl(self):
        """Satır toplamı (TL)"""
        return self.line_total_cents / 100

    @property
    def unit_price_tl(self):
        """Birim fiyat (TL)"""
        return self.sku.price_cents / 100