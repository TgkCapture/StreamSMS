# StreamSMS/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import homepage, profile, system_dashboard 

urlpatterns = [
    path('', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('messages/', include('apps.messages_app.urls')),
    path('profile/', profile, name='profile'),
    path('nominations/', include('apps.nominations.urls')),
    path('voting/', include('apps.voting.urls')),
    path('auth/', include('apps.broadcast_manager.urls')),
]
