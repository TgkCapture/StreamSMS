from django.contrib import admin
from django.urls import path, include
from .views import homepage
from messages_app.views import generate_rss
from django.contrib.auth import views as auth_views
from messages_app.views import africastalking_webhook

urlpatterns = [
    path('', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('rss/', generate_rss, name='generate_rss'),
    path('messages/', include('messages_app.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('africastalking-webhook/', africastalking_webhook, name='africastalking_webhook'),
    
]
