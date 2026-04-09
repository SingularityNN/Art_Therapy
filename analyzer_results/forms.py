from django import forms
from .models import Experiments

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['drawing',]


        # def clean_id(self):
        #     """Проверка на уникальность ID"""
        #     id_value = self.cleaned_data.get('id')
        #     if Experiments.objects.filter(id=id_value).exists():
        #         raise forms.ValidationError(f"Эксперимент с ID '{id_value}' уже существует.")
        #     return id_value