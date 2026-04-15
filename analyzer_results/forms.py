from django import forms
from .models import Experiments

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['drawing',]
        widgets = {
            'drawing': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['note',]
        widgets = {
            'note': forms.Textarea(attrs={'class': 'form-control'}),
        }