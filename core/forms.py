from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Imię', max_length=100)
    last_name = forms.CharField(label='Nazwisko', max_length=100)
    date_of_birth = forms.DateField(label='Data urodzenia', widget=forms.DateInput(attrs={'type': 'date'}))
    guardian_email = forms.EmailField(label='E-mail opiekuna')

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'guardian_email', 'password1', 'password2')
