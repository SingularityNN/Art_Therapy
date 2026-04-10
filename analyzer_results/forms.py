from django import forms
from .models import Experiments

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['drawing',]
        widgets = {
            'drawing': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # Для Bootstrap 5 класс 'form-control' подходит и для file input
        }
