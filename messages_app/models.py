from django.db import models

class Message(models.Model):
    from_number = models.CharField(max_length=15)
    message_body = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_number}: {self.message_body}"