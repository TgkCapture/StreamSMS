# apps/messages_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Message
from django.utils import timezone

@admin.register(Message)
class MessageAdmin(SimpleHistoryAdmin):
    list_display = (
        'truncated_message',
        'masked_number',
        'status_badge',
        'source',
        'created_at',
        'moderation_info'
    )
    list_filter = (
        'approved',
        'declined',
        'source',
        'created_at',
        'moderated_at'
    )
    search_fields = (
        'from_number',
        'message_body'
    )
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = (
        'created_at',
        'moderated_at',
        'moderated_by'
    )
    actions = [
        'approve_selected',
        'decline_selected'
    ]
    
    fieldsets = (
        (None, {
            'fields': (
                'from_number',
                'message_body',
                'source'
            )
        }),
        ('Status', {
            'fields': (
                'approved',
                'declined'
            )
        }),
        ('Moderation', {
            'fields': (
                'moderated_by',
                'moderated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def truncated_message(self, obj):
        return obj.message_body[:75] + '...' if len(obj.message_body) > 75 else obj.message_body
    truncated_message.short_description = "Message"

    def masked_number(self, obj):
        if len(obj.from_number) > 5:
            return f"{obj.from_number[:3]}** ** {obj.from_number[-2:]}"
        return obj.from_number
    masked_number.short_description = "Sender"

    def status_badge(self, obj):
        if obj.approved:
            return format_html(
                '<span class="badge bg-success">Approved</span>'
            )
        elif obj.declined:
            return format_html(
                '<span class="badge bg-danger">Declined</span>'
            )
        return format_html(
            '<span class="badge bg-warning text-dark">Pending</span>'
        )
    status_badge.short_description = "Status"
    status_badge.admin_order_field = 'approved'

    def moderation_info(self, obj):
        if obj.moderated_by and obj.moderated_at:
            return format_html(
                '{}<br><small>{}</small>',
                obj.moderated_by.get_short_name(),
                obj.moderated_at.strftime('%Y-%m-%d %H:%M')
            )
        return "-"
    moderation_info.short_description = "Moderated By"

    def approve_selected(self, request, queryset):
        updated = queryset.filter(approved=False, declined=False).update(
            approved=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(
            request,
            f"Successfully approved {updated} messages"
        )
    approve_selected.short_description = "Approve selected messages"

    def decline_selected(self, request, queryset):
        updated = queryset.filter(approved=False, declined=False).update(
            declined=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(
            request,
            f"Successfully declined {updated} messages"
        )
    decline_selected.short_description = "Decline selected messages"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('moderated_by')

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            )
        }