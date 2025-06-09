# apps/messages_app/urls.py
from django.urls import path
from .views import (
    moderation_interface, 
    approve_message, 
    messages_list, 
    message_detail, 
    decline_message
)

app_name = 'messages_app'

urlpatterns = [
    path('moderate/', moderation_interface, name='moderation_interface'),
    path('approve/<int:message_id>/', approve_message, name='approve_message'),
    path('decline/<int:id>/', decline_message, name='decline_message'),
    path('all-messages/', messages_list, name='messages_list'),
    path('<int:id>/', message_detail, name='message_detail'),
]