from django.urls import path
from .views import ussd_handler, nominate, vote

urlpatterns = [
    path('ussd/', ussd_handler, name='ussd_handler'),
    path('nominate/', nominate, name='nominate'),
    path('vote/', vote, name='vote'),
]
