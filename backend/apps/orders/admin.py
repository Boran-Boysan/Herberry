from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('name_snapshot', 'unit', 'quantity', 'line_total_cents')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status_badge', 'total_display', 'payment_provider', 'created_at')
    list_filter = ('status', 'payment_provider', 'created_at')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]

    def status_badge(self, obj):
        colors = {
            'created': 'orange',
            'paid': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_badge.short_description = "Durum"

    def total_display(self, obj):
        return f"{obj.total_tl:.2f} TL"

    total_display.short_description = "Toplam"