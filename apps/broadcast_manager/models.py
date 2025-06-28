# broadcast_manager/models.py
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLES = (
        ('ADMIN', _('System Administrator')),
        ('EDITOR', _('Content Editor')),
        ('PRODUCER', _('Program Producer')),
        ('FCC', _('FCC Operator')),
        ('VOTER', _('Voter')),
        ('NOMINATOR', _('Nominator')),
    )
    
    role = models.CharField(max_length=10, choices=ROLES)
    department = models.CharField(max_length=50, blank=True)
    phone_extension = models.CharField(max_length=10, blank=True)
    
    # Permission flags
    can_nominate = models.BooleanField(
        default=False,
        help_text=_('Can submit nominations')
    )
    can_vote = models.BooleanField(
        default=False,
        help_text=_('Can participate in voting')
    )
    can_moderate = models.BooleanField(
        default=False,
        help_text=_('Can moderate content')
    )

    # Override default groups and permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='broadcast_users',
        related_query_name='broadcast_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='broadcast_users',
        related_query_name='broadcast_user',
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = [
            ('nominate_candidates', _('Can nominate candidates')),
            ('vote_in_polls', _('Can vote in polls')),
            ('manage_voting', _('Can manage voting sessions')),
            ('moderate_content', _('Can moderate user content')),
        ]
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['can_vote']),
            models.Index(fields=['can_nominate']),
        ]
    
    def clean(self):
        """Validate role-permission consistency"""
        if self.role == 'VOTER' and not self.can_vote:
            raise ValidationError(_('Voters must have voting permissions'))
        if self.role == 'NOMINATOR' and not self.can_nominate:
            raise ValidationError(_('Nominators must have nomination permissions'))
    
    def save(self, *args, **kwargs):
        """Auto-set permissions based on role"""
        if not self.pk:  # Only on creation
            if self.role == 'ADMIN':
                self.is_staff = True
                self.can_nominate = True
                self.can_vote = True
                self.can_moderate = True
            elif self.role == 'VOTER':
                self.can_vote = True
            elif self.role == 'NOMINATOR':
                self.can_nominate = True
        
        super().save(*args, **kwargs)
        self._sync_permissions()
    
    def _sync_permissions(self):
        """Ensure permissions match the user's role and flags"""
        nominate_perm = Permission.objects.get(codename='nominate_candidates')
        vote_perm = Permission.objects.get(codename='vote_in_polls')
        
        if self.can_nominate:
            self.user_permissions.add(nominate_perm)
        else:
            self.user_permissions.remove(nominate_perm)
            
        if self.can_vote:
            self.user_permissions.add(vote_perm)
        else:
            self.user_permissions.remove(vote_perm)

    # Role check methods
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    def is_editor(self):
        return self.role == 'EDITOR'
    
    def is_producer(self):
        return self.role == 'PRODUCER'

    def is_fcc(self):
        return self.role == 'FCC'
    
    def is_voter(self):
        return self.role == 'VOTER' or self.can_vote
    
    def is_nominator(self):
        return self.role == 'NOMINATOR' or self.can_nominate

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('LOGIN', _('User Login')),
        ('LOGOUT', _('User Logout')),
        ('NOMINATION', _('Nomination Submitted')),
        ('VOTE', _('Vote Cast')),
        ('MODERATION', _('Content Moderation')),
        ('SYSTEM', _('System Event')),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='activities',
        verbose_name=_('User')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('Action Type')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )
    details = models.JSONField(
        default=dict,
        verbose_name=_('Additional Details')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    
    class Meta:
        verbose_name = _('Activity Log')
        verbose_name_plural = _('Activity Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} by {self.user or 'System'} at {self.timestamp}"