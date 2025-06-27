# broadcast_manager/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_admin():
                return HttpResponseForbidden("Insufficient permissions")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator