# broadcast_manager/backends.py
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

class RoleBasedAuthBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # Superusers and admins have all permissions
        if user_obj.is_superuser or user_obj.is_admin():
            return True
            
        # Handle app-specific permissions
        if perm.startswith('broadcast_manager.'):
            if perm.endswith('nominate_candidates'):
                return user_obj.can_nominate
            elif perm.endswith('vote_in_polls'):
                return user_obj.can_vote
            elif perm.endswith('moderate_content'):
                return user_obj.can_moderate
                
        return super().has_perm(user_obj, perm, obj)
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user and not user.is_active:
            raise PermissionDenied("Account is disabled")
        return user