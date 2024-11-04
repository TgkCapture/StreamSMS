from django.contrib import admin
from .models import VoteSession, Vote

admin.site.register(VoteSession)
admin.site.register(Vote)
