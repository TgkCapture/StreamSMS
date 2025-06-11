# StreamSMS/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from apps.messages_app.views import (
    generate_rss_json, 
    generate_rss, 
    generate_concatenated_rss_json,
    africastalking_webhook
)
from .views import homepage, profile, system_dashboard 

urlpatterns = [
    path('', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('rss/', generate_rss, name='generate_rss'),
    path('rss-json/', generate_rss_json, name='generate_rss_json'),
    path('rss-string/', generate_concatenated_rss_json, name='generate_concatenated_rss_json'),
    path('messages/', include('apps.messages_app.urls')),
    path('profile/', profile, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('africastalking-webhook/', africastalking_webhook, name='africastalking_webhook'),
    path('nominations/', include('apps.nominations.urls')),
    path('voting/', include('apps.voting.urls')),
]
