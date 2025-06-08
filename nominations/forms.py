from django import forms
from .models import Nominee, Vote

class NomineeForm(forms.ModelForm):
    class Meta:
        model = Nominee
        fields = ['name', 'category']

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['nominee', 'voter_identifier', 'voter_type']
