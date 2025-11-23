from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price_display',
        'discount_badge',
        'stock_badge',
        'is_organic',
        'is_active'
    )
    list_filter = ('category', 'is_organic', 'is_active', 'discount_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'category', 'image')
        }),
        ('Fiyat ve Stok', {
            'fields': ('price_cents', 'unit', 'stock')
        }),
        ('Indirim', {
            'fields': ('discount_active', 'discount_percentage'),
            'description': 'Indirim yapmak icin aktif yapin ve yuzde girin.'
        }),
        ('Ozellikler', {
            'fields': ('is_organic', 'is_active')
        }),
    )

    actions = ['activate_discount', 'deactivate_discount', 'set_discount_10', 'set_discount_20', 'set_discount_50']

    def price_display(self, obj):
        if obj.has_discount:
            discounted = float(obj.discounted_price_tl)
            original = float(obj.price_tl)
            return format_html(
                '<div style="display: flex; flex-direction: column; gap: 2px;">'
                '<span style="color: #10b981; font-weight: bold; font-size: 14px;">{} TL</span>'
                '<del style="color: #999; font-size: 11px;">{} TL</del>'
                '</div>',
                round(discounted, 2),
                round(original, 2)
            )
        price = float(obj.price_tl)
        return format_html('<span style="font-size: 14px;">{} TL</span>', round(price, 2))

    price_display.short_description = "Fiyat"

    def discount_badge(self, obj):
        if obj.has_discount:
            savings = float(obj.savings_tl)
            discount_pct = int(obj.discount_percentage)
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">'
                '-{} ({} TL)'
                '</span>',
                discount_pct,
                round(savings, 2)
            )
        return format_html('<span style="color: #999;">-</span>')

    discount_badge.short_description = "Indirim"

    def stock_badge(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">Tukendi</span>')
        elif obj.stock < 10:
            return format_html('<span style="color: #f59e0b;">{} adet</span>', obj.stock)
        return format_html('<span style="color: #10b981;">{} adet</span>', obj.stock)

    stock_badge.short_description = "Stok"

    def activate_discount(self, request, queryset):
        updated = queryset.update(discount_active=True)
        self.message_user(request, '{} urunun indirimi aktiflesti.'.format(updated))

    activate_discount.short_description = "Indirimi_aktiflestir"

    def deactivate_discount(self, request, queryset):
        updated = queryset.update(discount_active=False)
        self.message_user(request, '{} urunun indirimi kapatildi.'.format(updated))

    deactivate_discount.short_description = "Indirimi_kapat"

    def set_discount_10(self, request, queryset):
        updated = queryset.update(discount_active=True, discount_percentage=10)
        self.message_user(request, '{} urune 10 indirim uygulandi.'.format(updated))

    set_discount_10.short_description = "Indirim_10"

    def set_discount_20(self, request, queryset):
        updated = queryset.update(discount_active=True, discount_percentage=20)
        self.message_user(request, '{} urune 20 indirim uygulandi.'.format(updated))

    set_discount_20.short_description = "Indirim_20"

    def set_discount_50(self, request, queryset):
        updated = queryset.update(discount_active=True, discount_percentage=50)
        self.message_user(request, '{} urune 50 indirim uygulandi.'.format(updated))

    set_discount_50.short_description = "Indirim_50"