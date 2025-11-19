from django.contrib import admin
from .models import Subscription, SubscriptionItem


class SubscriptionItemInline(admin.TabularInline):
    model = SubscriptionItem
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'preferred_day', 'is_active', 'estimated_price_tl')
    list_filter = ('type', 'is_active', 'preferred_day')
    search_fields = ('user__email',)
    inlines = [SubscriptionItemInline]

    def estimated_price_tl(self, obj):
        return f"{obj.estimated_price_tl:.2f} TL"