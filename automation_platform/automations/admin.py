from django.contrib import admin
from .models import Automation, AutomationExecution

@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('name', 'code', 'description')

@admin.register(AutomationExecution)  
class AutomationExecutionAdmin(admin.ModelAdmin):
    list_display = ('automation', 'user', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('automation__name', 'user__email')
    readonly_fields = ('result', 'error_message', 'parameters')