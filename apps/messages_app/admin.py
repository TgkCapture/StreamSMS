# apps/messages_app/admin.py
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Message

@admin.register(Message)
class MessageAdmin(SimpleHistoryAdmin):
    list_display = ('from_number', 'message_body', 'approved', 'declined', 'created_at')
    list_filter = ('approved', 'declined', 'created_at')
    search_fields = ('from_number', 'message_body')
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('from_number', 'message_body')
        }),
        ('Status', {
            'fields': ('approved', 'declined')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )