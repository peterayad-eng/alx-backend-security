import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django_ip_geolocation.backends import IPGeolocationAPI
from .models import RequestLog, BlockedIP

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get client IP address
        ip_address = self.get_client_ip(request)

        # Block blacklisted IPs
        if BlockedIP.objects.filter(ip_address= ip_address, is_active=True).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Store IP temporarily on request object for logging later
        request._client_ip = ip_address

        return None

    def process_response(self, request, response):
        # Create log entry
        try:
            ip_address = getattr(request, "_client_ip", None)
            # Try cache first
            geolocation_data = cache.get(f"geo_{ip_address}")
            if not geolocation_data:
                try:
                    backend = IPGeolocationAPI()
                    geo = backend.get_geolocation(ip_address)

                    geolocation_data = {
                        "country": geo.country_name,
                        "city": geo.city,
                        "region": geo.region
                    }
                    # cache for 24 hours
                    cache.set(f"geo_{ip_address}", geolocation_data, 60 * 60 * 24)
                except Exception:
                    geolocation_data = {"country": None, "city": None, "region": None}

            if ip_address:
                RequestLog.objects.create(
                    ip_address=ip_address,
                    timestamp=timezone.now(),
                    path=request.path,
                    method=request.method,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500], 
                    country=geolocation_data.get('country'),
                    city=geolocation_data.get('city'),
                    region=geolocation_data.get('region'),
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

