# apps/voting/urls.py
from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.vote_home, name='vote_home'),
    path('cast-vote/', views.vote, name='vote'),
    path('ussd/', views.ussd_vote, name='ussd_vote'),
    path('results/', views.results, name='results'),
    path('api/results/', views.results_api, name='results_api'),
]