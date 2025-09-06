from django.db import models
from django.utils import timezone

# Create your models here.
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default='GET')
    user_agent = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        location = f"{self.city}, {self.country}" if self.country else "Unknown location"
        return f"{self.ip_address} - {self.path} - {location}"

    class Meta:
        db_table = 'request_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
        ]

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, default='system')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'blocked_ips'
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason or 'No reason provided'}"

