# broadcast_manager/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User

class RoleBasedAuthBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_admin():
            return True
        elif user_obj.is_editor():
            return True
        elif user_obj.is_producer():
            return True
        elif user_obj.is_fcc():
            return True
        return super().has_perm(user_obj, perm, obj)