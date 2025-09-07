from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP

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

@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'request_count', 'detected_at', 'is_active']
    list_filter = ['reason', 'is_active', 'detected_at']
    search_fields = ['ip_address', 'description']
    list_editable = ['is_active']
    list_per_page = 50
    actions = ['deactivate_suspicious_ips', 'block_suspicious_ips']

    def deactivate_suspicious_ips(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {queryset.count()} suspicious IPs")
    deactivate_suspicious_ips.short_description = "Deactivate selected suspicious IPs"

    def block_suspicious_ips(self, request, queryset):
        for suspicious_ip in queryset:
            BlockedIP.objects.update_or_create(
                ip_address=suspicious_ip.ip_address,
                defaults={
                    'reason': f'Blocked due to: {suspicious_ip.get_reason_display()}',
                    'is_active': True,
                    'created_by': request.user.username
                }
            )
        self.message_user(request, f"Blocked {queryset.count()} suspicious IPs")
    block_suspicious_ips.short_description = "Block selected suspicious IPs"

