from django.db import models
from django.utils import timezone

# Create your models here.
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default='GET')
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path} @ {self.timestamp}"
    
    class Meta:
        db_table = 'request_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
        ]

