# apps/voting/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.nominations.models import Nominee

class VoteSession(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voting Session"
        verbose_name_plural = "Voting Sessions"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return "Upcoming"
        elif self.start_time <= now <= self.end_time:
            return "Active"
        else:
            return "Completed"

class Vote(models.Model):
    VOTER_TYPES = (
        ('ussd', 'USSD'),
        ('web', 'Web'),
        ('mobile', 'Mobile App'),
    )

    nominee = models.ForeignKey(
        Nominee, 
        on_delete=models.CASCADE,
        related_name='voting_votes'
    )
    session = models.ForeignKey(
        VoteSession,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes'
    )
    voter_identifier = models.CharField(max_length=100)
    voter_type = models.CharField(max_length=50, choices=VOTER_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'voter_identifier'],
                name='unique_voter_per_session'
            )
        ]
        indexes = [
            models.Index(fields=['voter_identifier']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Vote for {self.nominee} by {self.get_voter_display()}"

    def get_voter_display(self):
        return self.user.username if self.user else self.voter_identifier