from django import forms

class BMIForm(forms.Form):
    weight = forms.FloatField(label='Masa ciała (kg)', min_value=20, max_value=300, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 70'}))
    height = forms.FloatField(label='Wzrost (cm)', min_value=100, max_value=250, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 170'}))
