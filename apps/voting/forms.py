# apps/voting/forms.py
from django import forms
from .models import Vote
from apps.nominations.models import Nominee
from django.utils import timezone

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['nominee']
        widgets = {
            'nominee': forms.RadioSelect(
                attrs={'class': 'form-check-input'}
            ),
        }
        labels = {
            'nominee': 'Select your preferred nominee',
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        if session:
            self.fields['nominee'].queryset = Nominee.objects.filter(
                approved=True
            ).order_by('name')
            self.session = session

    def clean(self):
        cleaned_data = super().clean()
        if not hasattr(self, 'session'):
            raise forms.ValidationError("No voting session specified")
        return cleaned_data