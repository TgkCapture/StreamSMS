# voting/models.py
from django.db import models
from django.contrib.auth.models import User
from nominations.models import Nominee

class VoteSession(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE)
    session = models.ForeignKey(VoteSession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    voter_identifier = models.CharField(max_length=100)  # For USSD voters
    voter_type = models.CharField(max_length=50, choices=(('ussd', 'USSD'), ('web', 'Web')))

    def __str__(self):
        return f"{self.nominee} - {self.voter_identifier} - {self.voter_type}"
