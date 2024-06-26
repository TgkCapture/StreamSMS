from django.contrib import admin
from django.urls import path, include
from .views import homepage, profile
from messages_app.views import generate_rss_json, generate_rss, generate_concatenated_rss_json
from django.contrib.auth import views as auth_views
from messages_app.views import africastalking_webhook

urlpatterns = [
    path('', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('rss/', generate_rss, name='generate_rss'),
    path('rss-json/', generate_rss_json, name='generate_rss_json'),
    path('rss-string/', generate_concatenated_rss_json, name='generate_concatenated_rss_json'),
    path('messages/', include('messages_app.urls')),
    path('profile/', profile, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('africastalking-webhook/', africastalking_webhook, name='africastalking_webhook'),
    
]
