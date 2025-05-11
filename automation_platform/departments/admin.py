from django.contrib import admin
from .models import Department, DepartmentMember

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')

@admin.register(DepartmentMember)
class DepartmentMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_primary', 'join_date')
    list_filter = ('is_primary', 'join_date')
    search_fields = ('user__email', 'department__name')