from django.db import models
from django.conf import settings


class EmailCampaign(models.Model):
    """Email kampanyaları"""
    CAMPAIGN_TYPES = [
        ('discount', 'İndirim Bildirimi'),
        ('new_product', 'Yeni Ürün'),
        ('newsletter', 'Bülten'),
        ('reminder', 'Hatırlatma'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('scheduled', 'Zamanlanmış'),
        ('sent', 'Gönderildi'),
        ('cancelled', 'İptal Edildi'),
    ]

    title = models.CharField(max_length=255, verbose_name="Kampanya Başlığı")
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, verbose_name="Kampanya Tipi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Durum")

    subject = models.CharField(max_length=255, verbose_name="Email Konusu")

    # İçerik
    discount_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimum İndirim Yüzdesi",
        help_text="Bu yüzdeden yüksek indirimleri bildirir (örn: 20 = %20 ve üzeri)"
    )

    # Gönderim zamanı
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="Zamanlanmış Gönderim")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Gönderilme Zamanı")

    # İstatistikler
    total_recipients = models.PositiveIntegerField(default=0, verbose_name="Toplam Alıcı")
    total_sent = models.PositiveIntegerField(default=0, verbose_name="Gönderilen")
    total_failed = models.PositiveIntegerField(default=0, verbose_name="Başarısız")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Oluşturan"
    )

    class Meta:
        db_table = 'email_campaigns'
        verbose_name = "Email Kampanyası"
        verbose_name_plural = "Email Kampanyaları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class EmailLog(models.Model):
    """Email gönderim logları"""
    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        verbose_name="Kampanya"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kullanıcı"
    )

    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=255, verbose_name="Konu")

    success = models.BooleanField(default=False, verbose_name="Başarılı mı?")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")

    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")

    class Meta:
        db_table = 'email_logs'
        verbose_name = "Email Logu"
        verbose_name_plural = "Email Logları"
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.email} - {'✓' if self.success else '✗'}"


class UserEmailPreference(models.Model):
    """Kullanıcı email tercihleri"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_preferences',
        verbose_name="Kullanıcı"
    )

    # Tercihler
    receive_discount_emails = models.BooleanField(default=True, verbose_name="İndirim Emaillerini Al")
    receive_new_product_emails = models.BooleanField(default=True, verbose_name="Yeni Ürün Emaillerini Al")
    receive_newsletter = models.BooleanField(default=True, verbose_name="Bülten Al")
    receive_order_updates = models.BooleanField(default=True, verbose_name="Sipariş Güncellemelerini Al")

    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name="Abonelikten Çıkma Zamanı")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")

    class Meta:
        db_table = 'user_email_preferences'
        verbose_name = "Email Tercihi"
        verbose_name_plural = "Email Tercihleri"

    def __str__(self):
        return f"{self.user.email} - Tercihler"