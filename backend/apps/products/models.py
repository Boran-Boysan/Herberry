from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kategori Adi")
    slug = models.SlugField(unique=True, verbose_name="URL")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ust Kategori")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    class Meta:
        db_table = 'categories'
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('piece', 'Adet'),
        ('box', 'Kutu'),
        ('gram', 'Gram'),
        ('liter', 'Litre'),
    ]

    name = models.CharField(max_length=255, verbose_name="Urun Adi")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Aciklama")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Kategori")

    # Fiyat
    price_cents = models.PositiveIntegerField(verbose_name="Fiyat (Kurus)")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, verbose_name="Birim")

    # Indirim
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Indirim Yuzdesi",
        help_text="Ornek: 20 yazarsaniz %20 indirim"
    )
    discount_active = models.BooleanField(default=False, verbose_name="Indirim Aktif mi?")

    # Stok ve durumlar
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok")
    is_organic = models.BooleanField(default=False, verbose_name="Organik mi?")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Urun Resmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Guncelleme Tarihi")

    class Meta:
        db_table = 'products'
        verbose_name = "Urun"
        verbose_name_plural = "Urunler"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def price_tl(self):
        """TL cinsinden fiyat"""
        from .utils import to_tl
        return to_tl(self.price_cents)

    @property
    def has_discount(self):
        """Indirim var mi?"""
        return self.discount_active and self.discount_percentage > 0

    @property
    def discounted_price_cents(self):
        """Indirimli fiyat (cents)"""
        if self.has_discount:
            discount_amount = self.price_cents * (float(self.discount_percentage) / 100)
            return int(self.price_cents - discount_amount)
        return self.price_cents

    @property
    def discounted_price_tl(self):
        """Indirimli fiyat (TL)"""
        from .utils import to_tl
        return to_tl(self.discounted_price_cents)

    @property
    def savings_cents(self):
        """Kazanc (cents)"""
        if self.has_discount:
            return self.price_cents - self.discounted_price_cents
        return 0

    @property
    def savings_tl(self):
        """Kazanc (TL)"""
        from .utils import to_tl
        return to_tl(self.savings_cents)