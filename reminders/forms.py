from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['title', 'date', 'time', 'recurrence']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'recurrence': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Tytuł przypomnienia',
            'date': 'Data',
            'time': 'Godzina',
            'recurrence': 'Powtarzanie',
        }
