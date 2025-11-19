from django.db import models
from django.conf import settings


class Subscription(models.Model):
    TYPE_CHOICES = [
        ('veg_box', 'Sebze Kutusu'),
        ('fruit_box', 'Meyve Kutusu'),
        ('custom_box', 'Ozel Kutu'),
    ]

    WEEKDAY_CHOICES = [
        (1, 'Pazartesi'),
        (2, 'Sali'),
        (3, 'Carsamba'),
        (4, 'Persembe'),
        (5, 'Cuma'),
        (6, 'Cumartesi'),
        (7, 'Pazar'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Kullanici")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Abonelik Tipi")
    preferred_day = models.SmallIntegerField(choices=WEEKDAY_CHOICES, verbose_name="Tercih Edilen Gun")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    address = models.ForeignKey('accounts.Address', on_delete=models.PROTECT, verbose_name="Teslimat Adresi")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Guncelleme Tarihi")

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
        verbose_name = "Abonelik"
        verbose_name_plural = "Abonelikler"

    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def estimated_price_cents(self):
        return sum(item.quantity * item.product.discounted_price_cents for item in self.items.all())

    @property
    def estimated_price_tl(self):
        from apps.products.utils import to_tl
        return to_tl(self.estimated_price_cents)


class SubscriptionItem(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='items', verbose_name="Abonelik")
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, verbose_name="Urun")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miktar")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    class Meta:
        db_table = 'subscription_items'
        unique_together = ['subscription', 'product']
        verbose_name = "Abonelik Urunu"
        verbose_name_plural = "Abonelik Urunleri"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total_tl(self):
        from apps.products.utils import to_tl
        return to_tl(self.quantity * self.product.discounted_price_cents)