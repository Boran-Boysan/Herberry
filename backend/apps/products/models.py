from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid
import os


def product_image_upload_path(instance, filename):
    """Ürün resimlerini organize bir şekilde sakla"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"products/{instance.category.slug if instance.category else 'uncategorized'}/{filename}"


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL Slug")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Üst Kategori")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'categories'
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Kategori yolunu döndür (Ana > Alt > Kategori)"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Ürün Açıklaması")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    tags = models.JSONField(default=list, blank=True, verbose_name="Etiketler")
    is_organic = models.BooleanField(default=False, verbose_name="Organik mi?")
    image = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True, verbose_name="Ürün Resmi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'products'
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_organic']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        """Resim URL'ini döndür"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

    @property
    def active_skus(self):
        """Aktif SKU'ları döndür"""
        return self.skus.filter(is_active=True)

    @property
    def min_price(self):
        """En düşük fiyatı döndür (TL cinsinden)"""
        active_skus = self.active_skus
        if active_skus.exists():
            return min(sku.price_tl for sku in active_skus)
        return 0


class SKU(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('piece', 'Adet'),
        ('box', 'Kutu'),
        ('gram', 'Gram'),
        ('liter', 'Litre'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus', verbose_name="Ürün")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, verbose_name="Birim")
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Barkod")
    price_cents = models.PositiveIntegerField(verbose_name="Fiyat (Kuruş)")  # Kuruş cinsinden fiyat
    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.2000, verbose_name="KDV Oranı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'skus'
        verbose_name = "SKU"
        verbose_name_plural = "SKU'lar"
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['barcode']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_unit_display()}"

    @property
    def price_tl(self):
        """Türk Lirası cinsinden fiyat"""
        return self.price_cents / 100

    @property
    def price_with_vat(self):
        """KDV dahil fiyat (TL)"""
        return self.price_tl * (1 + float(self.vat_rate))

    @property
    def is_in_stock(self):
        """Stokta var mı?"""
        return hasattr(self, 'stock') and self.stock.qty_on_hand > 0


class Stock(models.Model):
    sku = models.OneToOneField(SKU, on_delete=models.CASCADE, related_name='stock', verbose_name="SKU")
    qty_on_hand = models.PositiveIntegerField(default=0, verbose_name="Mevcut Stok")
    min_stock_level = models.PositiveIntegerField(default=0, verbose_name="Minimum Stok Seviyesi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'stocks'
        verbose_name = "Stok"
        verbose_name_plural = "Stoklar"

    def __str__(self):
        return f"{self.sku} - {self.qty_on_hand} adet"

    @property
    def is_low_stock(self):
        """Düşük stok uyarısı"""
        return self.qty_on_hand <= self.min_stock_level

    def decrease_stock(self, quantity):
        """Stok azalt"""
        if self.qty_on_hand >= quantity:
            self.qty_on_hand -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        """Stok arttır"""
        self.qty_on_hand += quantity
        self.save()


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kullanıcı")
    session_key = models.CharField(max_length=255, null=True, blank=True, verbose_name="Oturum Anahtarı")
    currency = models.CharField(max_length=3, default='TRY', verbose_name="Para Birimi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'carts'
        verbose_name = "Sepet"
        verbose_name_plural = "Sepetler"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        if self.user:
            return f"Sepet - {self.user.email}"
        return f"Sepet - Session: {self.session_key}"

    @property
    def total_items(self):
        """Toplam ürün sayısı"""
        return sum(item.qty for item in self.items.all())

    @property
    def total_price_cents(self):
        """Toplam fiyat (kuruş)"""
        return sum(item.total_price_cents for item in self.items.all())

    @property
    def total_price_tl(self):
        """Toplam fiyat (TL)"""
        return self.total_price_cents / 100

    def clear(self):
        """Sepeti temizle"""
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Sepet")
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name="SKU")
    qty = models.PositiveIntegerField(default=1, verbose_name="Miktar")  # default=1 eklendi
    unit_price_cents = models.PositiveIntegerField(default=0, verbose_name="Birim Fiyat (Kuruş)")  # default=0 eklendi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'cart_items'
        verbose_name = "Sepet Öğesi"
        verbose_name_plural = "Sepet Öğeleri"
        unique_together = ['cart', 'sku']
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.qty} adet"

    @property
    def total_price_cents(self):
        """Toplam fiyat (kuruş)"""
        # None kontrolü ekle
        qty = self.qty or 0
        unit_price = self.unit_price_cents or 0
        return qty * unit_price

    @property
    def total_price_tl(self):
        """Toplam fiyat (TL)"""
        return self.total_price_cents / 100

    @property
    def unit_price_tl(self):
        """Birim fiyat (TL)"""
        unit_price = self.unit_price_cents or 0
        return unit_price / 100

    def save(self, *args, **kwargs):
        # Eğer unit_price_cents belirtilmemişse, SKU'dan al
        if not self.unit_price_cents and self.sku_id:
            self.unit_price_cents = self.sku.price_cents
        # qty None ise 1 yap
        if not self.qty:
            self.qty = 1
        super().save(*args, **kwargs)