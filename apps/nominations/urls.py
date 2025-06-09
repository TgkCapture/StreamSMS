# apps/nominations/urls.py
from django.urls import path
from .views import ussd_handler, nominate, vote, category_detail

app_name = 'nominations'

urlpatterns = [
    path('ussd/', ussd_handler, name='ussd_handler'),
    path('nominate/', nominate, name='nominate'),
    path('vote/', vote, name='vote'),
    path('categories/<slug:slug>/', category_detail, name='category_detail'),
]