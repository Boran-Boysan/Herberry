"""
Management command to send discount notifications

Usage:
    python manage.py send_discount_notifications --min-discount 20
    python manage.py send_discount_notifications --test-email user@example.com
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.products.models import Product
from apps.accounts.models import User
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send discount notifications to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-discount',
            type=float,
            default=10.0,
            help='Minimum discount percentage to notify (default: 10)',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Send test email to specific email address',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate sending without actually sending emails',
        )

    def handle(self, *args, **options):
        min_discount = options['min_discount']
        test_email = options['test_email']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('🚀 Starting discount notification process...'))

        # İndirimli ürünleri bul
        discounted_products = Product.objects.filter(
            is_active=True,
            discount_active=True,
            discount_percentage__gte=min_discount
        ).order_by('-discount_percentage')

        if not discounted_products.exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  No products with discount >= %{min_discount} found')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Found {discounted_products.count()} products with discount >= %{min_discount}'
            )
        )

        # En yüksek indirim
        max_discount = int(discounted_products.first().discount_percentage)
        self.stdout.write(f'📊 Highest discount: %{max_discount}')

        # Test mode
        if test_email:
            self.send_test_email(test_email, discounted_products, dry_run)
            return

        # Tüm kullanıcılara gönder
        self.send_to_all_users(discounted_products, dry_run)

    def send_test_email(self, email, products, dry_run):
        """Test emaili gönder"""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ User with email {email} not found')
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'🧪 DRY RUN: Would send email to {user.email}')
            )
            return

        from apps.notifications.services import EmailService

        self.stdout.write(f'📧 Sending test email to {user.email}...')

        success = EmailService.send_discount_notification(user, products)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Test email sent successfully to {user.email}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send test email to {user.email}')
            )

    def send_to_all_users(self, products, dry_run):
        """Tüm kullanıcılara email gönder"""
        # Aktif kullanıcıları al
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

        self.stdout.write(f'👥 Total recipients: {len(all_recipients)}')
        self.stdout.write(f'   - With preferences: {users_with_prefs.count()}')
        self.stdout.write(f'   - Without preferences: {len(users_without_prefs)}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n🧪 DRY RUN: Would send emails to {len(all_recipients)} users')
            )
            return

        # Email gönder
        from apps.notifications.services import EmailService
        from apps.notifications.models import EmailLog

        sent_count = 0
        failed_count = 0

        self.stdout.write('\n📧 Sending emails...\n')

        for i, user in enumerate(all_recipients, 1):
            try:
                success = EmailService.send_discount_notification(user, products)

                # Log kaydet
                EmailLog.objects.create(
                    user=user,
                    email=user.email,
                    subject=f'🎉 İndirimler Başladı! - Herberry',
                    success=success
                )

                if success:
                    sent_count += 1
                    self.stdout.write(f'  [{i}/{len(all_recipients)}] ✓ {user.email}')
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  [{i}/{len(all_recipients)}] ⚠ {user.email} (skipped)')
                    )

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  [{i}/{len(all_recipients)}] ✗ {user.email}: {str(e)}')
                )

                EmailLog.objects.create(
                    user=user,
                    email=user.email,
                    subject=f'🎉 İndirimler Başladı! - Herberry',
                    success=False,
                    error_message=str(e)
                )

        # Özet
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'\n✅ EMAIL SUMMARY'))
        self.stdout.write(f'   Total recipients: {len(all_recipients)}')
        self.stdout.write(self.style.SUCCESS(f'   ✓ Sent: {sent_count}'))

        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'   ✗ Failed: {failed_count}'))

        self.stdout.write('\n' + '=' * 50 + '\n')