# broadcast_manager/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, ActivityLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'can_vote', 'can_nominate')
    search_fields = ('username', 'email', 'department', 'phone_extension')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Role Information'), {
            'fields': ('role', 'department', 'phone_extension'),
        }),
        (_('Special Permissions'), {
            'fields': ('can_nominate', 'can_vote', 'can_moderate'),
            'classes': ('collapse',),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_staff=True)
        return qs

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'details', 'ip_address')
    readonly_fields = ('timestamp', 'ip_address')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False