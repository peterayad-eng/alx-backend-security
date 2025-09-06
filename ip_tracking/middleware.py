import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import RequestLog

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get client IP address
        ip_address = self.get_client_ip(request)

        # Block blacklisted IPs
        if BlockedIP.objects.filter(ip_address= ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Store IP temporarily on request object for logging later
        request._client_ip = ip_address

    def process_response(self, request, response):        
        # Create log entry
        try:
            ip_address = getattr(request, "_client_ip", None)
            if ip_address:
                RequestLog.objects.create(
                    ip_address=ip_address,
                    timestamp=timezone.now(),
                    path=request.path,
                    method=request.method,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                )
        except Exception as e:
            # Don't crash the app because of logging errors
            print(f"[IPLoggingMiddleware] Logging failed: {e}")

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

