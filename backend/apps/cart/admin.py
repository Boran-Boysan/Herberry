from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('price_snapshot_cents', 'line_total_tl')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_tl', 'created_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]

    def total_tl(self, obj):
        return f"{obj.total_tl:.2f} TL"

    total_tl.short_description = "Toplam"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'unit_price_tl', 'line_total_tl')
    search_fields = ('cart__user__email', 'product__name')