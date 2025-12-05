from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmailCampaign, EmailLog, UserEmailPreference
from .services import EmailCampaignService


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    """Email Kampanyası Yönetimi"""

    list_display = (
        'title',
        'campaign_type',
        'status_badge',
        'stats_display',
        'scheduled_at',
        'sent_at',
        'action_buttons'
    )

    list_filter = ('campaign_type', 'status', 'created_at')
    search_fields = ('title', 'subject')
    ordering = ('-created_at',)

    readonly_fields = ('total_recipients', 'total_sent', 'total_failed', 'sent_at', 'created_by')

    fieldsets = (
        ('Kampanya Bilgileri', {
            'fields': ('title', 'campaign_type', 'status', 'subject')
        }),
        ('İçerik Ayarları', {
            'fields': ('discount_threshold',),
            'description': 'İndirim kampanyaları için minimum indirim yüzdesini belirleyin'
        }),
        ('Zamanlama', {
            'fields': ('scheduled_at', 'sent_at')
        }),
        ('İstatistikler', {
            'fields': ('total_recipients', 'total_sent', 'total_failed'),
            'classes': ('collapse',)
        }),
        ('Sistem', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )

    actions = ['send_campaign_now', 'duplicate_campaign', 'cancel_campaign']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:campaign_id>/send/',
                self.admin_site.admin_view(self.send_campaign_view),
                name='send_campaign',
            ),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kampanya
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def status_badge(self, obj):
        """Durum badge'i"""
        colors = {
            'draft': '#6b7280',
            'scheduled': '#f59e0b',
            'sent': '#10b981',
            'cancelled': '#ef4444'
        }
        icons = {
            'draft': '📝',
            'scheduled': '⏰',
            'sent': '✅',
            'cancelled': '❌'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 12px;">{} {}</span>',
            colors.get(obj.status, '#gray'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )

    status_badge.short_description = 'Durum'

    def stats_display(self, obj):
        """İstatistikler"""
        if obj.status != 'sent':
            return '-'

        total = obj.total_recipients
        sent = obj.total_sent
        failed = obj.total_failed
        success_rate = (sent / total * 100) if total > 0 else 0

        html = f'<div style="font-size: 12px;">'
        html += f'<div>📨 Gönderilen: <strong>{sent}</strong></div>'

        if failed > 0:
            html += f'<div style="color: #ef4444;">❌ Başarısız: <strong>{failed}</strong></div>'

        html += f'<div style="color: #10b981;">📊 Başarı: <strong>{success_rate:.1f}%</strong></div>'
        html += '</div>'

        return format_html(html)

    stats_display.short_description = 'İstatistikler'

    def action_buttons(self, obj):
        """Aksiyon butonları"""
        if obj.status == 'draft':
            return format_html(
                '<a class="button" href="{}">🚀 Hemen Gönder</a>',
                f'/admin/notifications/emailcampaign/{obj.id}/send/'
            )
        elif obj.status == 'sent':
            return format_html(
                '<span style="color: #10b981;">✓ Gönderildi</span>'
            )
        elif obj.status == 'cancelled':
            return format_html(
                '<span style="color: #ef4444;">✗ İptal Edildi</span>'
            )
        return '-'

    action_buttons.short_description = 'İşlemler'

    def send_campaign_view(self, request, campaign_id):
        """Kampanya gönderme view'ı"""
        campaign = EmailCampaign.objects.get(id=campaign_id)

        if request.method == 'POST':
            if campaign.status != 'draft':
                messages.error(request, 'Bu kampanya zaten gönderildi veya iptal edildi!')
                return redirect('..')

            # Kampanyayı gönder
            sent, failed = EmailCampaignService.send_discount_campaign(campaign)

            messages.success(
                request,
                f'✅ Kampanya başarıyla gönderildi! {sent} başarılı, {failed} başarısız.'
            )
            return redirect('..')

        # Önizleme için indirimli ürünleri al
        from apps.products.models import Product
        discounted_products = Product.objects.filter(
            is_active=True,
            discount_active=True,
            discount_percentage__gte=campaign.discount_threshold or 0
        )[:6]

        # Alıcı sayısını hesapla
        from apps.accounts.models import User
        users = User.objects.filter(is_active=True)
        recipient_count = users.count()

        context = {
            'campaign': campaign,
            'discounted_products': discounted_products,
            'recipient_count': recipient_count,
            'opts': self.model._meta,
            'has_permission': True,
        }

        return render(request, 'admin/send_campaign_confirmation.html', context)

    # Toplu işlemler
    def send_campaign_now(self, request, queryset):
        """Seçili kampanyaları hemen gönder"""
        sent_count = 0

        for campaign in queryset:
            if campaign.status == 'draft':
                sent, failed = EmailCampaignService.send_discount_campaign(campaign)
                sent_count += 1

        self.message_user(
            request,
            f'{sent_count} kampanya gönderildi.',
            level=messages.SUCCESS
        )

    send_campaign_now.short_description = "🚀 Seçili kampanyaları hemen gönder"

    def duplicate_campaign(self, request, queryset):
        """Kampanyayı kopyala"""
        for campaign in queryset:
            campaign.pk = None
            campaign.status = 'draft'
            campaign.sent_at = None
            campaign.total_recipients = 0
            campaign.total_sent = 0
            campaign.total_failed = 0
            campaign.title = f"{campaign.title} (Kopya)"
            campaign.save()

        self.message_user(request, f'{queryset.count()} kampanya kopyalandı.')

    duplicate_campaign.short_description = "📋 Kampanyayı kopyala"

    def cancel_campaign(self, request, queryset):
        """Kampanyayı iptal et"""
        updated = queryset.filter(status__in=['draft', 'scheduled']).update(status='cancelled')
        self.message_user(request, f'{updated} kampanya iptal edildi.')

    cancel_campaign.short_description = "❌ Kampanyayı iptal et"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Email Log Yönetimi"""

    list_display = (
        'email',
        'subject',
        'success_badge',
        'campaign',
        'sent_at'
    )

    list_filter = ('success', 'sent_at', 'campaign')
    search_fields = ('email', 'subject', 'error_message')
    ordering = ('-sent_at',)

    readonly_fields = ('campaign', 'user', 'email', 'subject', 'success', 'error_message', 'sent_at')

    def success_badge(self, obj):
        """Başarı durumu"""
        if obj.success:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✓ Başarılı</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: bold;">✗ Başarısız</span>'
        )

    success_badge.short_description = 'Durum'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserEmailPreference)
class UserEmailPreferenceAdmin(admin.ModelAdmin):
    """Kullanıcı Email Tercihleri"""

    list_display = (
        'user',
        'discount_badge',
        'new_product_badge',
        'newsletter_badge',
        'order_updates_badge',
        'unsubscribed_at'
    )

    list_filter = (
        'receive_discount_emails',
        'receive_new_product_emails',
        'receive_newsletter',
        'receive_order_updates'
    )

    search_fields = ('user__email', 'user__username')
    ordering = ('-created_at',)

    def discount_badge(self, obj):
        return self._preference_badge(obj.receive_discount_emails)

    discount_badge.short_description = 'İndirim'

    def new_product_badge(self, obj):
        return self._preference_badge(obj.receive_new_product_emails)

    new_product_badge.short_description = 'Yeni Ürün'

    def newsletter_badge(self, obj):
        return self._preference_badge(obj.receive_newsletter)

    newsletter_badge.short_description = 'Bülten'

    def order_updates_badge(self, obj):
        return self._preference_badge(obj.receive_order_updates)

    order_updates_badge.short_description = 'Sipariş'

    def _preference_badge(self, value):
        if value:
            return format_html('<span style="color: #10b981;">✓</span>')
        return format_html('<span style="color: #ef4444;">✗</span>')