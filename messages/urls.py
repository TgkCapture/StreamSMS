from django.urls import path
from .views import sms_webhook, moderation_interface, approve_message, generate_rss

urlpatterns = [
    path('sms/', sms_webhook, name='sms_webhook'),
    path('moderate/', moderation_interface, name='moderation_interface'),
    path('approve/<int:message_id>/', approve_message, name='approve_message'),
    path('rss/', generate_rss, name='generate_rss'),
]
