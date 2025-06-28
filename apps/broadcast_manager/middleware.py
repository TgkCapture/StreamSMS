# broadcast_manager/middleware.py
import logging
from django.utils import timezone
from .models import ActivityLog

logger = logging.getLogger(__name__)

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        try:
            if request.user.is_authenticated:
                action = self._get_action_from_request(request)
                ActivityLog.objects.create(
                    user=request.user,
                    action=action,
                    ip_address=self._get_client_ip(request),
                    details={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')
                    }
                )
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
        
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _get_action_from_request(self, request):
        path = request.path
        if path.startswith('/admin/'):
            return 'ADMIN_ACCESS'
        elif path.startswith('/auth/login/'):
            return 'LOGIN'
        elif path.startswith('/auth/logout/'):
            return 'LOGOUT'
        return 'PAGE_VIEW'