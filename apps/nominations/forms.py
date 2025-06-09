# apps/nominations/forms.py
from django import forms
from .models import Nominee, Vote, NominationCategory

class NomineeForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=NominationCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Nomination Category"
    )
    
    class Meta:
        model = Nominee
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nominee name'
            }),
        }
        labels = {
            'name': 'Nominee Name',
        }
        help_texts = {
            'name': 'Full name of the person or team being nominated',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show categories that are active/approved if needed
        self.fields['category'].queryset = NominationCategory.objects.select_related('main_category')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long")
        return name.strip()

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['nominee', 'voter_identifier', 'voter_type']
        widgets = {
            'nominee': forms.Select(attrs={
                'class': 'form-control',
            }),
            'voter_identifier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your unique identifier'
            }),
            'voter_type': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'nominee': 'Select Nominee',
            'voter_identifier': 'Your ID',
            'voter_type': 'Voting Method',
        }
        help_texts = {
            'voter_identifier': 'Could be phone number, email, or user ID',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show approved nominees
        self.fields['nominee'].queryset = Nominee.objects.filter(
            approved=True
        ).select_related('category')

    def clean_voter_identifier(self):
        identifier = self.cleaned_data.get('voter_identifier')
        if not identifier or len(identifier.strip()) < 3:
            raise forms.ValidationError("Please provide a valid identifier")
        return identifier.strip()