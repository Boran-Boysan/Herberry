from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('name_snapshot', 'unit', 'qty', 'unit_price_display', 'line_total_display')
    readonly_fields = ('unit_price_display', 'line_total_display')

    def unit_price_display(self, obj):
        if obj.unit_price_cents is None:
            return "0.00 TL"
        return f"{obj.unit_price_cents / 100:.2f} TL"

    unit_price_display.short_description = "Birim Fiyat"

    def line_total_display(self, obj):
        if obj.line_total_cents is None:
            return "0.00 TL"
        return f"{obj.line_total_cents / 100:.2f} TL"

    line_total_display.short_description = "Satır Toplamı"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'status_badge', 'total_display', 'payment_provider', 'created_at')
    list_filter = ('status', 'payment_provider', 'created_at')
    search_fields = ('user__email', 'id', 'payment_ref')
    readonly_fields = ('total_display', 'created_at', 'updated_at')

    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('user', 'address', 'status', 'payment_provider', 'payment_ref')
        }),
        ('Fiyat Bilgileri', {
            'fields': ('subtotal_cents', 'shipping_cents', 'discount_cents', 'vat_cents', 'total_cents', 'currency', 'total_display')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [OrderItemInline]

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Kullanıcı"
    user_email.admin_order_field = 'user__email'

    def total_display(self, obj):
        if obj.total_cents is None:
            return "0.00 TL"
        return f"{obj.total_cents / 100:.2f} TL"

    total_display.short_description = "Toplam"

    def status_badge(self, obj):
        colors = {
            'created': 'orange',
            'paid': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = "Durum"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name_snapshot', 'qty', 'unit_price_display', 'line_total_display')
    list_filter = ('created_at', 'unit')
    search_fields = ('name_snapshot', 'order__id', 'order__user__email')

    def unit_price_display(self, obj):
        if obj.unit_price_cents is None:
            return "0.00 TL"
        return f"{obj.unit_price_cents / 100:.2f} TL"

    unit_price_display.short_description = "Birim Fiyat"

    def line_total_display(self, obj):
        if obj.line_total_cents is None:
            return "0.00 TL"
        return f"{obj.line_total_cents / 100:.2f} TL"

    line_total_display.short_description = "Satır Toplamı"
