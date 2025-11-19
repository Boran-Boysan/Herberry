from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'phone', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Bilgiler', {'fields': ('username', 'phone')}),
        ('Izinler', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'district', 'is_default', 'created_at')
    list_filter = ('city', 'is_default')
    search_fields = ('user__email', 'city', 'district', 'title')

    fieldsets = (
        ('Adres Bilgileri', {
            'fields': ('user', 'title', 'full_address', 'city', 'district', 'phone', 'is_default')
        }),
    )