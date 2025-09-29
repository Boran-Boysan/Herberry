from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Admin, Address


class AdminInline(admin.StackedInline):
    model = Admin
    extra = 0
    fields = ('role', 'is_active')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
    'email', 'username', 'first_name', 'last_name', 'is_staff', 'is_restaurant', 'admin_status', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_restaurant', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'username')}),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_restaurant', 'groups', 'user_permissions'),
        }),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    inlines = [AdminInline]

    def admin_status(self, obj):
        if hasattr(obj, 'admin_profile') and obj.admin_profile.is_active:
            role = obj.admin_profile.get_role_display()
            color = 'red' if obj.admin_profile.role == 'super_admin' else 'green'
            return format_html('<span style="color: {};">✓ {}</span>', color, role)
        return format_html('<span style="color: gray;">Normal Kullanıcı</span>')

    admin_status.short_description = "Admin Durumu"


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

    fieldsets = (
        ('Admin Bilgileri', {
            'fields': ('user', 'role', 'is_active')
        }),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"
    user_email.admin_order_field = 'user__email'

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = "Ad Soyad"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user.is_staff = True
            obj.user.save()
        super().save_model(request, obj, form, change)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'district', 'is_default', 'created_at')
    list_filter = ('city', 'is_default', 'created_at')
    search_fields = ('title', 'user__email', 'city', 'district')
    raw_id_fields = ('user',)

    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('user', 'title', 'is_default')
        }),
        ('Adres Detayları', {
            'fields': ('line1', 'line2', 'city', 'district', 'postal_code', 'phone')
        })
    )


# Admin site başlığını özelleştir
admin.site.site_header = "E-Ticaret Yönetim Paneli"
admin.site.site_title = "E-Ticaret Admin"
admin.site.index_title = "Yönetim Paneli"