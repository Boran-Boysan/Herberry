from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Basitlestirilmis kullanici modeli"""
    email = models.EmailField(unique=True, verbose_name="E-posta")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = "Kullanici"
        verbose_name_plural = "Kullanicilar"

    def __str__(self):
        return self.email


class Address(models.Model):
    """Kullanici adresleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="Kullanici")
    title = models.CharField(max_length=100, verbose_name="Adres Basligi")
    full_address = models.TextField(verbose_name="Tam Adres")
    city = models.CharField(max_length=100, verbose_name="Sehir")
    district = models.CharField(max_length=100, verbose_name="Ilce")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    is_default = models.BooleanField(default=False, verbose_name="Varsayilan Adres")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Olusturma Tarihi")

    class Meta:
        db_table = 'addresses'
        verbose_name = "Adres"
        verbose_name_plural = "Adresler"

    def __str__(self):
        return f"{self.title} - {self.user.email}"