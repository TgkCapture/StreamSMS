# apps/nominations/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('nominations:category_detail', args=[self.slug])

class NominationCategory(models.Model):
    main_category = models.ForeignKey(
        MainCategory, 
        on_delete=models.CASCADE, 
        related_name="subcategories"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nomination Category"
        verbose_name_plural = "Nomination Categories"
        ordering = ['main_category', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['main_category', 'name'],
                name='unique_category_name_per_main_category'
            )
        ]

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

class Nominee(models.Model):
    category = models.ForeignKey(
        NominationCategory,
        on_delete=models.CASCADE,
        related_name="nominees"
    )
    name = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nominee"
        verbose_name_plural = "Nominees"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['approved']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def vote_count(self):
        return self.votes.count()

class Vote(models.Model):
    VOTER_TYPES = [
        ('web', 'Web'),
        ('ussd', 'USSD'),
        ('sms', 'SMS'),
    ]

    nominee = models.ForeignKey(
        Nominee,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    voter_identifier = models.CharField(max_length=100)
    voter_type = models.CharField(max_length=10, choices=VOTER_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['nominee', 'voter_identifier'],
                name='unique_vote_per_nominee'
            )
        ]
        indexes = [
            models.Index(fields=['voter_identifier']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Vote for {self.nominee} by {self.voter_identifier}"