# apps/messages_app/models.py
from django.db import models
from simple_history.models import HistoricalRecords

class Message(models.Model):
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
    history = HistoricalRecords()

    class Meta:
        verbose_name = "SMS Message"
        verbose_name_plural = "SMS Messages"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['approved', 'declined']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.from_number}: {self.message_body[:50]}"