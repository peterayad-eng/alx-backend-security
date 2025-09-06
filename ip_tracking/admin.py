from django.contrib import admin
from .models import RequestLog, BlockedIP

# Register your models here.
@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'path', 'method', 'timestamp']
    list_filter = ['method', 'timestamp']
    search_fields = ['ip_address', 'path']
    readonly_fields = ['ip_address', 'path', 'method', 'timestamp', 'user_agent']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "reason", "is_active", "created_by", "created_at")
    list_filter = ("is_active", "created_by", "created_at")
    search_fields = ("ip_address", "reason")
    ordering = ("-created_at",)

