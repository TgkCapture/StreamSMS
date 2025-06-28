# broadcast_manager/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, register_public, create_staff_account,
    editor_dashboard, producer_control, fcc_operations,
    activity_logs, staff_list, profile_view
)

app_name = 'broadcast_manager'

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register_public, name='register'),
    
    # Staff management
    path('staff/create/', create_staff_account, name='staff_create'),
    path('staff/', staff_list, name='staff_list'),
    
    # Role-specific dashboards
    path('editor/', editor_dashboard, name='editor_dashboard'),
    path('producer/', producer_control, name='producer_control'),
    path('fcc/', fcc_operations, name='fcc_operations'),
    
    # Activity and profile
    path('activity-logs/', activity_logs, name='activity_logs'),
    path('profile/', profile_view, name='profile'),
]