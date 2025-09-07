from celery import shared_task
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    """
    Detect suspicious IPs:
    1. IPs with more than 100 requests/hour
    2. IPs accessing sensitive paths (/admin, /login)
    """
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # High request volume detection
    high_volume_ips = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(request_count=Count("id"))
        .filter(request_count__gt=100)
    )

    for entry in high_volume_ips:
        ip = entry["ip_address"]
        count = entry["request_count"]

        suspicious, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason="high_volume",
            defaults={
                "request_count": count,
                "description": f"Made {count} requests in the last hour.",
            },
        )
        if not created:
            suspicious.request_count = count
            suspicious.description = f"Made {count} requests in the last hour."
            suspicious.save(update_fields=["request_count", "description", "last_offense"])

    # Sensitive path detection
    sensitive_paths = ["/admin", "/login"]
    sensitive_logs = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago, path__in=sensitive_paths
    ).values("ip_address", "path")

    for entry in sensitive_logs:
        ip = entry["ip_address"]
        path = entry["path"]

        suspicious, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason="sensitive_access",
            defaults={
                "request_count": 1,
                "description": f"Accessed sensitive path: {path}",
            },
        )
        if not created:
            suspicious.request_count += 1
            suspicious.description = f"Repeatedly accessed sensitive path: {path}"
            suspicious.save(update_fields=["request_count", "description", "last_offense"])

