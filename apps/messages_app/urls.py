# apps/messages_app/urls.py
from django.urls import path
from .views import (
    messages_home,
    moderation_interface,
    approve_message,
    decline_message,
    messages_list,
    message_detail,
    africastalking_webhook,
    generate_rss,
    generate_rss_json,
    generate_concatenated_rss_json,
    bulk_action,
    toggle_message_status
)

app_name = 'messages_app'

urlpatterns = [
    # Dashboard
    path('', messages_home, name='messages_home'),
    
    # Moderation
    path('moderate/', moderation_interface, name='moderation_interface'),
    path('approve/<int:message_id>/', approve_message, name='approve_message'),
    path('decline/<int:message_id>/', decline_message, name='decline_message'),
    path('bulk-action/', bulk_action, name='bulk_action'),
    path('toggle-status/<int:message_id>/', toggle_message_status, name='toggle_message_status'),
    
    # Message Views
    path('all-messages/', messages_list, name='messages_list'),
    path('message/<int:message_id>/', message_detail, name='message_detail'),
    
    # Webhook
    path('webhook/africastalking/', africastalking_webhook, name='africastalking_webhook'),
    
    # Feeds
    path('feed/rss/', generate_rss, name='rss_feed'),
    path('feed/json/', generate_rss_json, name='json_feed'),
    path('feed/combined-json/', generate_concatenated_rss_json, name='concatenated_json_feed'),
]