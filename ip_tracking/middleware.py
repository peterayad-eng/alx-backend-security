import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import RequestLog

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get client IP address
        ip_address = self.get_client_ip(request)
        
        # Create log entry
        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=timezone.now(),
            path=request.path,
            method=request.method,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        return response

    def get_client_ip(self, request):
        """
        Get the real client IP address, handling proxy headers
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, first one is client
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

