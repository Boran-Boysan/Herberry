from django.db import models
from django.conf import settings


class Subscription(models.Model):
    """Abonelik sistemi"""
    TYPE_CHOICES = [
        ('veg_box', 'Sebze Kutusu'),
        ('fruit_box', 'Meyve Kutusu'),
        ('custom_box', 'Özel Kutu'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Abonelik Türü")
    preferred_day = models.PositiveSmallIntegerField(
        null=True, blank=True,
        preferred_day=models.PositiveSmallIntegerField(
            null=True, blank=True,
            help_text="1-7 arası (1=Pazartesi, 7=Pazar)",
            verbose_name="Tercih Edilen Gün"
        )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    address = models.ForeignKey('accounts.Address', on_delete=models.RESTRICT, verbose_name="Teslimat Adresi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'subscriptions'
        verbose_name = "Abonelik"
        verbose_name_plural = "Abonelikler"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()}"


class SubscriptionItem(models.Model):
    """Abonelik ürünleri"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='items',
                                     verbose_name="Abonelik")
    sku = models.ForeignKey('products.SKU', on_delete=models.CASCADE, verbose_name="SKU")
    qty = models.PositiveIntegerField(verbose_name="Miktar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'subscription_items'
        verbose_name = "Abonelik Ürünü"
        verbose_name_plural = "Abonelik Ürünleri"
        unique_together = ('subscription', 'sku')
        indexes = [
            models.Index(fields=['subscription']),
        ]

    def __str__(self):
        return f"{self.sku.product.name} x{self.qty}"