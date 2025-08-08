from django import forms
from .models import Medication
import datetime

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = [
            'name',
            'form',
            'quantity',
            'dosage_amount',
            'volume_ml',
            'dosage_ml_per_time',
            'frequency',
            'start_date',
            'prescription_required',
            'expiration_date',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Np. Paracetamol', 'class': 'form-control'}),
            'form': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Np. 20', 'class': 'form-control'}),
            'dosage_amount': forms.NumberInput(attrs={'placeholder': 'Ilość tabletek na dawkę', 'class': 'form-control'}),
            'volume_ml': forms.NumberInput(attrs={'placeholder': 'Objętość syropu w ml', 'class': 'form-control'}),
            'dosage_ml_per_time': forms.NumberInput(attrs={'placeholder': 'ml na porcję', 'class': 'form-control'}),
            'frequency': forms.NumberInput(attrs={'placeholder': 'Np. 2', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'id_prescription_required'}),
            'expiration_date': forms.DateInput(attrs={
                'type': 'date',
                'min': datetime.date.today().strftime('%Y-%m-%d'),
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].required = False
        self.fields['dosage_amount'].required = False
        self.fields['volume_ml'].required = False
        self.fields['dosage_ml_per_time'].required = False