# broadcast_manager/urls.py
from django.urls import path
from . import views

app_name = 'broadcast_manager'

urlpatterns = [
    path('editor/', views.editor_dashboard, name='editor_dashboard'),
    path('producer/', views.producer_control, name='producer_control'),
    path('fcc/', views.fcc_operations, name='fcc_operations'),
    path('activity/', views.activity_logs, name='activity_logs'),
]