# apps/voting/admin.py
from django.contrib import admin
from .models import VoteSession, Vote

@admin.register(VoteSession)
class VoteSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'status', 'is_active')
    list_filter = ('is_active', 'start_time')
    search_fields = ('name', 'description')
    readonly_fields = ('status', 'created_at', 'updated_at')
    date_hierarchy = 'start_time'
    actions = ['activate_sessions', 'deactivate_sessions']

    def activate_sessions(self, request, queryset):
        queryset.update(is_active=True)
    activate_sessions.short_description = "Activate selected sessions"

    def deactivate_sessions(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_sessions.short_description = "Deactivate selected sessions"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('nominee', 'session', 'get_voter_display', 'voter_type', 'created_at')
    list_filter = ('session', 'voter_type', 'created_at')
    search_fields = ('nominee__name', 'voter_identifier', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_voter_display(self, obj):
        return obj.get_voter_display()
    get_voter_display.short_description = 'Voter'