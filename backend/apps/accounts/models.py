from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Özel kullanıcı modeli"""
    email = models.EmailField(unique=True, verbose_name="E-posta")
    is_staff = models.BooleanField(default=False, verbose_name="Personel mi?")
    is_restaurant = models.BooleanField(default=False, verbose_name="Restoran mı?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"

    @property
    def is_admin_user(self):
        """Kullanıcının admin olup olmadığını kontrol et"""
        return hasattr(self, 'admin_profile') and self.admin_profile.is_active


class Admin(models.Model):
    """Admin kullanıcıları - Basit yapı"""

    ROLE_CHOICES = [
        ('super_admin', 'Süper Admin'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile', verbose_name="Kullanıcı")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin', verbose_name="Admin Rolü")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'admins'
        verbose_name = "Admin"
        verbose_name_plural = "Adminler"
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Address(models.Model):
    """Kullanıcı adresleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="Kullanıcı")
    title = models.CharField(max_length=100, verbose_name="Adres Başlığı")
    line1 = models.CharField(max_length=255, verbose_name="Adres Satır 1")
    line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adres Satır 2")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    district = models.CharField(max_length=100, verbose_name="İlçe")
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Posta Kodu")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan Adres")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'addresses'
        verbose_name = "Adres"
        verbose_name_plural = "Adresler"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_default']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
