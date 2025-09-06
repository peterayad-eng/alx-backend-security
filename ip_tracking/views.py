from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from django.conf import settings
import time

# Create your views here.
@require_http_methods(["POST"])
@csrf_exempt
@ratelimit(key='ip', rate=f'{settings.RATELIMIT_ANONYMOUS}', method='POST', block=False)
def login_view(request):
    """
    Sensitive login view with rate limiting
    """
    was_limited = getattr(request, 'limited', False)

    if was_limited:
        return JsonResponse({"error": "Too many requests. Try again later."}, status=429)

    # Your actual login logic here
    # For demonstration, we'll just return a success message
    time.sleep(1)  # Simulate processing time
    return JsonResponse({"status": "success", "message": "Login processed successfully"})

@require_http_methods(["POST"])
@csrf_exempt
@login_required
@ratelimit(key='user', rate=f'{settings.RATELIMIT_AUTHENTICATED}', method='POST', block=False)
def sensitive_action_view(request):
    """
    Sensitive action that requires authentication with rate limiting
    """
    was_limited = getattr(request, 'limited', False)

    if was_limited:
        return JsonResponse({"error": "Too many requests. Try again later."}, status=429)

    # Your sensitive action logic here
    return JsonResponse({"status": "success", "message": "Login processed successfully"})

# Health check endpoint (without rate limiting)
@require_http_methods(["GET"])
def health_check(request):
    return JsonResponse({'status': 'healthy'})

