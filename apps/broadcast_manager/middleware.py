# broadcast_manager/middleware.py
from .models import ActivityLog
from django.utils import timezone

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            action = f"Accessed {request.path}"
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                ip_address=self.get_client_ip(request),
                details={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code
                }
            )
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')