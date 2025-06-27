# broadcast_manager/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'System Administrator'),
        ('EDITOR', 'Content Editor'),
        ('PRODUCER', 'Program Producer'),
        ('FCC', 'FCC Operator'),
    )
    
    role = models.CharField(max_length=10, choices=ROLES)
    department = models.CharField(max_length=50, blank=True)
    phone_extension = models.CharField(max_length=10, blank=True)
    
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    def is_editor(self):
        return self.role == 'EDITOR'
    
    def is_producer(self):
        return self.role == 'PRODUCER'

    def is_fcc(self):
        return self.role == 'FCC'

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']