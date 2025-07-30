from django import forms
from .models import PressureMeasurement

class PressureMeasurementForm(forms.ModelForm):
    class Meta:
        model = PressureMeasurement
        fields = ['date', 'time', 'systolic', 'diastolic']  # zachowujemy kolejność!
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'systolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 120'}),
            'diastolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 80'}),
        }
