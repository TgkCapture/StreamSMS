# apps/messages_app/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

class Message(models.Model):
    SOURCE_CHOICES = [
        ('sms', 'SMS'),
        ('web', 'Web'),
        ('api', 'API'),
        ('other', 'Other'),
    ]

    from_number = models.CharField(
        max_length=15,
        verbose_name="Sender Number"
    )
    message_body = models.TextField(
        verbose_name="Message Content"
    )
    approved = models.BooleanField(
        default=False,
        verbose_name="Approved Status"
    )
    declined = models.BooleanField(
        default=False,
        verbose_name="Declined Status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creation Date"
    )
    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Moderation Date"
    )
    moderated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Moderated By",
        related_name='moderated_messages'
    )
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='sms',
        verbose_name="Message Source"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "SMS Message"
        verbose_name_plural = "SMS Messages"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['approved', 'declined']),
            models.Index(fields=['created_at']),
            models.Index(fields=['source']),
            models.Index(fields=['moderated_by']),
        ]

    def __str__(self):
        return f"{self.from_number}: {self.message_body[:50]}"

    def get_status(self):
        if self.approved:
            return "approved"
        if self.declined:
            return "declined"
        return "pending"

    def save(self, *args, **kwargs):
        if self.approved or self.declined:
            if not self.moderated_at:
                self.moderated_at = timezone.now()
        super().save(*args, **kwargs)