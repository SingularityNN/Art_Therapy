from django import forms
from .models import Experiments

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['drawing',]
