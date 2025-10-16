from django.contrib import admin
from django.utils.html import format_html
from .models import Subscription, SubscriptionItem


class SubscriptionItemInline(admin.TabularInline):
    model = SubscriptionItem
    extra = 0
    fields = ('sku', 'qty', 'unit_price_display', 'line_total_display')
    readonly_fields = ('unit_price_display', 'line_total_display')
    raw_id_fields = ('sku',)

    def unit_price_display(self, obj):
        if obj.id:
            return f"{obj.unit_price_tl:.2f} TL"
        return "-"

    unit_price_display.short_description = "Birim Fiyat"

    def line_total_display(self, obj):
        if obj.id:
            return f"{obj.line_total_tl:.2f} TL"
        return "-"

    line_total_display.short_description = "Satır Toplamı"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_email', 'type_badge', 'preferred_day_display',
        'is_active_badge', 'total_items', 'estimated_price_display', 'created_at'
    )
    list_filter = ('type', 'is_active', 'preferred_day', 'created_at')
    search_fields = ('user__email', 'user__username', 'id')
    readonly_fields = ('total_items', 'estimated_price_display', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'address')

    fieldsets = (
        ('Abonelik Bilgileri', {
            'fields': ('user', 'type', 'preferred_day', 'is_active')
        }),
        ('Teslimat', {
            'fields': ('address',)
        }),
        ('Özet', {
            'fields': ('total_items', 'estimated_price_display')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [SubscriptionItemInline]

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Kullanıcı"
    user_email.admin_order_field = 'user__email'

    def type_badge(self, obj):
        colors = {
            'veg_box': '#10b981',
            'fruit_box': '#f59e0b',
            'custom_box': '#8b5cf6'
        }
        color = colors.get(obj.type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_type_display()
        )

    type_badge.short_description = "Tip"
    type_badge.admin_order_field = 'type'

    def preferred_day_display(self, obj):
        return obj.get_preferred_day_display()

    preferred_day_display.short_description = "Tercih Günü"
    preferred_day_display.admin_order_field = 'preferred_day'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: 600;">✗ Pasif</span>'
        )

    is_active_badge.short_description = "Durum"
    is_active_badge.admin_order_field = 'is_active'

    def estimated_price_display(self, obj):
        return f"{obj.estimated_price_tl:.2f} TL"

    estimated_price_display.short_description = "Tahmini Fiyat"

    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} abonelik aktifleştirildi.')

    activate_subscriptions.short_description = "Seçili abonelikleri aktifleştir"

    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} abonelik pasifleştirildi.')

    deactivate_subscriptions.short_description = "Seçili abonelikleri pasifleştir"


@admin.register(SubscriptionItem)
class SubscriptionItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subscription_id', 'user_email', 'product_name',
        'qty', 'unit_price_display', 'line_total_display'
    )
    list_filter = ('created_at',)
    search_fields = (
        'subscription__user__email',
        'sku__product__name',
        'subscription__id'
    )
    raw_id_fields = ('subscription', 'sku')
    readonly_fields = ('unit_price_display', 'line_total_display', 'created_at', 'updated_at')

    fieldsets = (
        ('Abonelik Bilgileri', {
            'fields': ('subscription',)
        }),
        ('Ürün Bilgileri', {
            'fields': ('sku', 'qty')
        }),
        ('Fiyat Bilgileri', {
            'fields': ('unit_price_display', 'line_total_display')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_email(self, obj):
        return obj.subscription.user.email

    user_email.short_description = "Kullanıcı"

    def subscription_id(self, obj):
        return f"#{obj.subscription.id}"

    subscription_id.short_description = "Abonelik"
    subscription_id.admin_order_field = 'subscription__id'

    def product_name(self, obj):
        return obj.sku.product.name

    product_name.short_description = "Ürün"

    def unit_price_display(self, obj):
        return f"{obj.unit_price_tl:.2f} TL"

    unit_price_display.short_description = "Birim Fiyat"

    def line_total_display(self, obj):
        return f"{obj.line_total_tl:.2f} TL"

    line_total_display.short_description = "Satır Toplamı"