from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_number', 'message_body', 'approved')
    list_filter = ('approved',)
    search_fields = ('from_number', 'message_body')
