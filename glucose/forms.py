from django import forms
from .models import GlucoseMeasurement

class GlucoseMeasurementForm(forms.ModelForm):
    class Meta:
        model = GlucoseMeasurement
        fields = ['date', 'time', 'value']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'min': 30, 'max': 600}),
        }
        labels = {
            'date': 'Data pomiaru',
            'time': 'Godzina pomiaru',
            'value': 'Wynik pomiaru (mg/dL)',
        }
