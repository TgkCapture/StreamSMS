from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Message

admin.site.register(Message, SimpleHistoryAdmin)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_number', 'message_body', 'approved')
    list_filter = ('approved',)
    search_fields = ('from_number', 'message_body')
