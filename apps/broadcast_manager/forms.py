# apps/broadcast_manager/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User

class PublicRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                raise ValidationError(_("A user with that email already exists."))
        except ValidationError as e:
            raise ValidationError(_("Invalid email address"))
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'VOTER'
        user.can_vote = True
        if commit:
            user.save()
        return user


class StaffCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'department', 'phone_extension', 'password1', 'password2']
        widgets = {
            'role': forms.Select(choices=[
                ('PRODUCER', 'Producer'),
                ('FCC', 'FCC Operator'),
                ('EDITOR', 'Content Editor')
            ])
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('PRODUCER', 'Producer'),
            ('FCC', 'FCC Operator'),
            ('EDITOR', 'Content Editor')
        ]
        self.fields['password1'].help_text = _(
            "Your password must contain at least 8 characters."
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email