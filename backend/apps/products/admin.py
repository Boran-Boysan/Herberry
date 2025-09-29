from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, SKU, Stock, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_organic', 'is_active', 'created_at')
    list_filter = ('category', 'is_organic', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_url', 'created_at', 'updated_at')

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Özellikler', {
            'fields': ('tags', 'is_organic', 'is_active')
        }),
        ('Resim', {
            'fields': ('image', 'image_url')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    fields = ('qty_on_hand', 'min_stock_level')


@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ('product', 'unit', 'price_tl', 'vat_rate', 'is_active')
    list_filter = ('unit', 'is_active', 'vat_rate')
    search_fields = ('product__name', 'barcode')
    raw_id_fields = ('product',)
    inlines = [StockInline]

    def price_tl(self, obj):
        return f"{obj.price_tl:.2f} TL"

    price_tl.short_description = "Fiyat (TL)"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('sku', 'qty_on_hand', 'min_stock_level', 'is_low_stock', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('sku__product__name',)
    raw_id_fields = ('sku',)

    def is_low_stock(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠ Düşük Stok</span>')
        return format_html('<span style="color: green;">✓ Yeterli</span>')

    is_low_stock.short_description = "Stok Durumu"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price_tl',)

    def total_price_tl(self, obj):
        return f"{obj.total_price_tl:.2f} TL"

    total_price_tl.short_description = "Toplam (TL)"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'total_items', 'total_price_tl', 'created_at')
    list_filter = ('created_at', 'currency')
    search_fields = ('user__email', 'session_key')
    readonly_fields = ('total_items', 'total_price_tl')
    inlines = [CartItemInline]

    def total_price_tl(self, obj):
        return f"{obj.total_price_tl:.2f} TL"

    total_price_tl.short_description = "Toplam (TL)"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'sku', 'qty', 'unit_price_tl', 'total_price_tl')
    list_filter = ('created_at',)
    search_fields = ('cart__user__email', 'sku__product__name')
    raw_id_fields = ('cart', 'sku')

    def unit_price_tl(self, obj):
        return f"{obj.unit_price_tl:.2f} TL"

    unit_price_tl.short_description = "Birim Fiyat (TL)"

    def total_price_tl(self, obj):
        return f"{obj.total_price_tl:.2f} TL"

    total_price_tl.short_description = "Toplam (TL)"