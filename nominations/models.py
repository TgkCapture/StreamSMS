from django.db import models
from django.contrib.auth.models import User

class MainCategory(models.Model):
    """
    Main categories
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class NominationCategory(models.Model):
    """
    Subcategories within each main category
    """
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"


class Nominee(models.Model):
    """
    Individuals or teams nominated in a specific subcategory.
    """
    category = models.ForeignKey(NominationCategory, on_delete=models.CASCADE, related_name="nominees")
    name = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Vote(models.Model):
    """
    Votes submitted for a specific nominee.
    """
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE, related_name="votes")
    voter_identifier = models.CharField(max_length=50)
    voter_type = models.CharField(max_length=10, choices=[('web', 'Web'), ('ussd', 'USSD')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('nominee', 'voter_identifier')

    def __str__(self):
        return f"Vote for {self.nominee} by {self.voter_identifier} ({self.voter_type})"
