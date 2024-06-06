from django.contrib import admin
from django.urls import path, include
from .views import homepage

urlpatterns = [
    path('', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('messages/', include('messages_app.urls')),
]
