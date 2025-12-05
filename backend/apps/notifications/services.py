"""
Email Notification Service
Kullanıcılara güzel HTML emailler göndermek için
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email gönderme servisi"""

    @staticmethod
    def send_discount_notification(user, discounted_products):
        """
        İndirim bildirimi gönder

        Args:
            user: User modeli
            discounted_products: İndirimli ürünler queryset
        """
        try:
            # Email tercihlerini kontrol et
            if hasattr(user, 'email_preferences'):
                if not user.email_preferences.receive_discount_emails:
                    return False

            # En yüksek indirimleri al (max 6 ürün)
            top_discounts = discounted_products.order_by('-discount_percentage')[:6]

            if not top_discounts:
                return False

            # En yüksek indirim yüzdesi
            max_discount = int(top_discounts[0].discount_percentage)

            # Email konusu
            subject = f"🎉 %{max_discount} İndirimlere Kaçırma! - Herberry"

            # HTML içerik
            html_content = render_to_string('emails/discount_notification.html', {
                'user': user,
                'products': top_discounts,
                'max_discount': max_discount,
                'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
            })

            # Text içerik (HTML desteği olmayan mailler için)
            text_content = f"""
Merhaba {user.username},

Herberry'de harika indirimler başladı! 

En Yüksek İndirim: %{max_discount}

İndirimli ürünlerimizi görmek için sitemizi ziyaret edin.

Herberry - En taze sebze ve meyveler kapınızda
            """.strip()

            # Email oluştur
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            # HTML versiyonu ekle
            email.attach_alternative(html_content, "text/html")

            # Gönder
            email.send()

            logger.info(f"Discount email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send discount email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_new_product_notification(user, new_products):
        """Yeni ürün bildirimi gönder"""
        try:
            if hasattr(user, 'email_preferences'):
                if not user.email_preferences.receive_new_product_emails:
                    return False

            subject = f"🆕 Yeni Ürünler Geldi! - Herberry"

            html_content = render_to_string('emails/new_product_notification.html', {
                'user': user,
                'products': new_products[:6],
                'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
            })

            text_content = f"""
Merhaba {user.username},

Herberry'de yeni ürünler eklendi!

Yeni ürünlerimizi görmek için sitemizi ziyaret edin.

Herberry - En taze sebze ve meyveler kapınızda
            """.strip()

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"New product email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send new product email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_order_confirmation(user, order):
        """Sipariş onay emaili gönder"""
        try:
            if hasattr(user, 'email_preferences'):
                if not user.email_preferences.receive_order_updates:
                    return False

            subject = f"✅ Siparişiniz Alındı - #{order.id} - Herberry"

            html_content = render_to_string('emails/order_confirmation.html', {
                'user': user,
                'order': order,
                'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
            })

            text_content = f"""
Merhaba {user.username},

Siparişiniz başarıyla alındı!

Sipariş No: #{order.id}
Toplam: {order.total_tl} TL
Durum: {order.get_status_display()}

Herberry - En taze sebze ve meyveler kapınızda
            """.strip()

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Order confirmation email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send order confirmation email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_cart_reminder(user, cart):
        """Sepet hatırlatma emaili gönder"""
        try:
            # Sepette ürün var mı?
            if not cart.items.exists():
                return False

            subject = f"🛒 Sepetinizde Ürünler Bekliyor! - Herberry"

            html_content = render_to_string('emails/cart_reminder.html', {
                'user': user,
                'cart': cart,
                'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
            })

            text_content = f"""
Merhaba {user.username},

Sepetinizde {cart.total_items} ürün bekliyor!

Toplam: {cart.total_tl} TL

Siparişinizi tamamlamak için sitemizi ziyaret edin.

Herberry - En taze sebze ve meyveler kapınızda
            """.strip()

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Cart reminder email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send cart reminder email to {user.email}: {str(e)}")
            return False


class EmailCampaignService:
    """Email kampanyası servisi"""

    @staticmethod
    def send_discount_campaign(campaign):
        """
        İndirim kampanyası gönder

        Args:
            campaign: EmailCampaign modeli
        """
        from .models import EmailLog

        # İndirimli ürünleri al
        discounted_products = Product.objects.filter(
            is_active=True,
            discount_active=True,
            discount_percentage__gte=campaign.discount_threshold or 0
        )

        if not discounted_products.exists():
            logger.warning(f"No discounted products found for campaign {campaign.id}")
            return 0, 0

        # Aktif kullanıcıları al (email tercihlerine göre)
        users = User.objects.filter(is_active=True)

        # Email tercihlerini kontrol et
        users_with_prefs = users.filter(
            email_preferences__receive_discount_emails=True
        )

        # Tercihleri olmayan kullanıcıları da ekle (default: True)
        users_without_prefs = users.exclude(
            id__in=users_with_prefs.values_list('id', flat=True)
        )

        all_recipients = list(users_with_prefs) + list(users_without_prefs)

        campaign.total_recipients = len(all_recipients)
        campaign.save()

        sent_count = 0
        failed_count = 0

        for user in all_recipients:
            try:
                success = EmailService.send_discount_notification(user, discounted_products)

                # Log kaydet
                EmailLog.objects.create(
                    campaign=campaign,
                    user=user,
                    email=user.email,
                    subject=campaign.subject,
                    success=success
                )

                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"Failed to send campaign email to {user.email}: {str(e)}")

                EmailLog.objects.create(
                    campaign=campaign,
                    user=user,
                    email=user.email,
                    subject=campaign.subject,
                    success=False,
                    error_message=str(e)
                )

                failed_count += 1

        # Kampanya istatistiklerini güncelle
        campaign.total_sent = sent_count
        campaign.total_failed = failed_count
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()

        logger.info(f"Campaign {campaign.id} completed: {sent_count} sent, {failed_count} failed")

        return sent_count, failed_count