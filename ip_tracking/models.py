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

class SuspiciousIP(models.Model):
    REASON_CHOICES = [
        ('high_volume', 'High request volume'),
        ('sensitive_access', 'Access to sensitive paths'),
        ('multiple_failures', 'Multiple authentication failures'),
        ('scanning', 'Port scanning behavior'),
    ]

    ip_address = models.GenericIPAddressField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    request_count = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_offense = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suspicious_ips'
        verbose_name = 'Suspicious IP'
        verbose_name_plural = 'Suspicious IPs'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['ip_address', 'reason']

    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"

