from django.db import models
from django.conf import settings


class Cart(models.Model):
    """Kullanici sepeti"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', verbose_name="Kullanici")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Guncelleme Tarihi")

    class Meta:
        db_table = 'carts'
        verbose_name = "Sepet"
        verbose_name_plural = "Sepetler"

    def __str__(self):
        return f"Sepet - {self.user.email}"

    @property
    def total_items(self):
        """Toplam urun sayisi"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_cents(self):
        """Toplam fiyat (cents)"""
        return sum(item.line_total_cents for item in self.items.all())

    @property
    def total_tl(self):
        """Toplam fiyat (TL)"""
        from apps.products.utils import to_tl
        return to_tl(self.total_cents)

    def clear(self):
        """Sepeti temizle"""
        self.items.all().delete()


class CartItem(models.Model):
    """Sepet urunu"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Sepet")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="Urun")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miktar")
    price_snapshot_cents = models.PositiveIntegerField(verbose_name="Anlik Fiyat (Kurus)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product']
        verbose_name = "Sepet Urunu"
        verbose_name_plural = "Sepet Urunleri"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total_cents(self):
        """Satir toplami (cents)"""
        return self.quantity * self.price_snapshot_cents

    @property
    def line_total_tl(self):
        """Satir toplami (TL)"""
        from apps.products.utils import to_tl
        return to_tl(self.line_total_cents)

    @property
    def unit_price_tl(self):
        """Birim fiyat (TL)"""
        from apps.products.utils import to_tl
        return to_tl(self.price_snapshot_cents)

    def save(self, *args, **kwargs):
        if not self.pk and self.product:
            self.price_snapshot_cents = self.product.discounted_price_cents
        super().save(*args, **kwargs)