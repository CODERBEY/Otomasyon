from django.contrib import admin
from .models import Department, DepartmentMember

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')

class DepartmentMemberInline(admin.TabularInline):
    model = DepartmentMember
    extra = 1

@admin.register(DepartmentMember)
class DepartmentMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_primary', 'join_date')
    list_filter = ('is_primary', 'join_date', 'department')
    search_fields = ('user__email', 'department__name')
    autocomplete_fields = ['user', 'department']

# User admin'e DepartmentMember inline ekleyelim
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

class UserDepartmentInline(admin.TabularInline):
    model = DepartmentMember
    extra = 1

# Mevcut User admin'i kaldır
admin.site.unregister(User)

# Yeni User admin tanımla
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserDepartmentInline]
    # Diğer ayarlar accounts/admin.py'den gelecek
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kisisel Bilgiler', {'fields': ('first_name', 'last_name')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Onemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)