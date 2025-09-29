from django.contrib import admin
from .models import Subscription, SubscriptionItem


class SubscriptionItemInline(admin.TabularInline):
    model = SubscriptionItem
    extra = 1
    fields = ('sku', 'qty')
    raw_id_fields = ('sku',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'type', 'preferred_day_display', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'preferred_day', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user', 'address')

    fieldsets = (
        ('Abonelik Bilgileri', {
            'fields': ('user', 'type', 'preferred_day', 'address', 'is_active')
        }),
    )

    inlines = [SubscriptionItemInline]

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Kullanıcı"

    def preferred_day_display(self, obj):
        if obj.preferred_day:
            days = ['', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            return days[obj.preferred_day]
        return "Belirtilmemiş"

    preferred_day_display.short_description = "Tercih Edilen Gün"


@admin.register(SubscriptionItem)
class SubscriptionItemAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'sku', 'qty')
    list_filter = ('created_at',)
    search_fields = ('sku__product__name', 'subscription__user__email')
    raw_id_fields = ('subscription', 'sku')