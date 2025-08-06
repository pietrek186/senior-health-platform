from django import forms
from .models import Medication
import datetime

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'quantity', 'start_date', 'frequency', 'prescription_required', 'expiration_date']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Np. Paracetamol'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Np. 20'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'frequency': forms.NumberInput(attrs={'placeholder': 'Np. 2'}),
            'expiration_date': forms.DateInput(attrs={
                'type': 'date',
                'min': datetime.date.today().strftime('%Y-%m-%d')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prescription_required'].widget.attrs.update({
            'class': 'form-check-input',
            'role': 'switch'
        })
