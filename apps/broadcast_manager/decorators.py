# broadcast_manager/decorators.py
from django.http import HttpResponseForbidden, JsonResponse
from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(*roles, api=False):
    """
    Decorator for views that checks whether a user has a particular role.
    Can handle both web and API requests.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if api:
                    return JsonResponse(
                        {'error': 'Authentication required'}, 
                        status=401
                    )
                return HttpResponseForbidden()
                
            if request.user.role not in roles and not request.user.is_admin():
                if api:
                    return JsonResponse(
                        {'error': 'Insufficient permissions'}, 
                        status=403
                    )
                return HttpResponseForbidden()
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def permission_required(perm, api=False):
    """
    Decorator that checks for specific permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(perm):
                if api:
                    return JsonResponse(
                        {'error': 'Missing permission: ' + perm},
                        status=403
                    )
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator