from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils.html import format_html
from .models import User, Address


class CustomUserCreationForm(UserCreationForm):
    """Kullanıcı oluşturma formu - Email zorunlu"""
    email = forms.EmailField(
        required=True,
        label='E-posta',
        help_text='Email adresi zorunludur'
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Kullanıcı düzenleme formu - Email zorunlu"""
    email = forms.EmailField(
        required=True,
        label='E-posta'
    )

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Gelişmiş kullanıcı admin paneli"""

    # Formlar
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    # Liste görünümü
    list_display = (
        'email',
        'username',
        'phone',
        'user_status',
        'staff_badge',
        'created_at_formatted'
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'created_at'
    )

    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)

    # Seçilebilir checkboxlar
    list_select_related = True
    list_per_page = 50

    # Toplu işlemler (Actions)
    actions = [
        'activate_users',
        'deactivate_users',
        'make_staff',
        'remove_staff',
        'delete_selected_users'
    ]

    # Kullanıcı eklerken gösterilecek alanlar
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'password1', 'password2'),
        }),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Kullanıcı düzenlerken gösterilecek alanlar
    fieldsets = (
        ('Giriş Bilgileri', {
            'fields': ('email', 'password')
        }),
        ('Kişisel Bilgiler', {
            'fields': ('username', 'phone')
        }),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Önemli Tarihler', {
            'fields': ('last_login', 'created_at'),
        }),
    )

    readonly_fields = ('last_login', 'created_at')

    # Custom display methods
    def user_status(self, obj):
        """Kullanıcı durumu badge"""
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">✗ Pasif</span>'
        )

    user_status.short_description = 'Durum'

    def staff_badge(self, obj):
        """Staff badge"""
        badges = []
        if obj.is_superuser:
            badges.append('<span style="background: #dc2626; color: white; padding: 2px 6px; '
                          'border-radius: 3px; font-size: 10px; margin-right: 3px;">SUPERUSER</span>')
        if obj.is_staff:
            badges.append('<span style="background: #2563eb; color: white; padding: 2px 6px; '
                          'border-radius: 3px; font-size: 10px;">STAFF</span>')
        if not badges:
            return format_html('<span style="color: #6b7280;">Normal Kullanıcı</span>')
        return format_html(''.join(badges))

    staff_badge.short_description = 'Rol'

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Kayıt Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlem metodları
    def activate_users(self, request, queryset):
        """Seçili kullanıcıları aktif yap"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} kullanıcı aktif edildi.')

    activate_users.short_description = "✓ Seçili kullanıcıları aktif yap"

    def deactivate_users(self, request, queryset):
        """Seçili kullanıcıları pasif yap"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} kullanıcı pasif edildi.')

    deactivate_users.short_description = "✗ Seçili kullanıcıları pasif yap"

    def make_staff(self, request, queryset):
        """Seçili kullanıcıları staff yap"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} kullanıcı staff yapıldı.')

    make_staff.short_description = "👤 Seçili kullanıcıları staff yap"

    def remove_staff(self, request, queryset):
        """Seçili kullanıcılardan staff yetkisini al"""
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'{updated} kullanıcıdan staff yetkisi alındı.')

    remove_staff.short_description = "👤 Seçili kullanıcılardan staff kaldır"

    def delete_selected_users(self, request, queryset):
        """Seçili kullanıcıları sil"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} kullanıcı silindi.', level='warning')

    delete_selected_users.short_description = "🗑️ Seçili kullanıcıları SİL"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Gelişmiş adres admin paneli"""

    list_display = (
        'title',
        'user_link',
        'city',
        'district',
        'default_badge',
        'created_at_formatted'
    )

    list_filter = ('city', 'is_default', 'created_at')
    search_fields = ('user__email', 'user__username', 'city', 'district', 'title', 'phone')
    ordering = ('-created_at',)

    list_per_page = 50

    # Toplu işlemler
    actions = ['set_as_default', 'remove_default', 'delete_selected_addresses']

    fieldsets = (
        ('Kullanıcı', {
            'fields': ('user',)
        }),
        ('Adres Bilgileri', {
            'fields': ('title', 'full_address', 'city', 'district', 'phone')
        }),
        ('Ayarlar', {
            'fields': ('is_default',)
        }),
    )

    readonly_fields = ('created_at',)

    # Custom display methods
    def user_link(self, obj):
        """Kullanıcıya link"""
        from django.urls import reverse
        from django.utils.html import format_html

        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)

    user_link.short_description = 'Kullanıcı'

    def default_badge(self, obj):
        """Varsayılan adres badge"""
        if obj.is_default:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px;">★ Varsayılan</span>'
            )
        return format_html('<span style="color: #9ca3af;">-</span>')

    default_badge.short_description = 'Varsayılan'

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Eklenme Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlem metodları
    def set_as_default(self, request, queryset):
        """Seçili adresleri varsayılan yap"""
        for address in queryset:
            # Önce kullanıcının tüm adreslerini varsayılandan çıkar
            Address.objects.filter(user=address.user).update(is_default=False)
            # Sonra bu adresi varsayılan yap
            address.is_default = True
            address.save()
        self.message_user(request, f'{queryset.count()} adres varsayılan yapıldı.')

    set_as_default.short_description = "★ Seçili adresleri varsayılan yap"

    def remove_default(self, request, queryset):
        """Seçili adreslerden varsayılanı kaldır"""
        updated = queryset.update(is_default=False)
        self.message_user(request, f'{updated} adres varsayılandan çıkarıldı.')

    remove_default.short_description = "☆ Varsayılan'dan çıkar"

    def delete_selected_addresses(self, request, queryset):
        """Seçili adresleri sil"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} adres silindi.', level='warning')

    delete_selected_addresses.short_description = "🗑️ Seçili adresleri SİL"