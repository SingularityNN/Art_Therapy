from django import forms
from .models import Experiments

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['drawing_first', 'drawing_second']
        widgets = {
            'drawing_first': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'drawing_second': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['note',]
        widgets = {
            'note': forms.Textarea(attrs={'class': 'form-control'}),
        }