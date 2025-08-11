from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "np. jan.kowalski@example.com"})
    )
    first_name = forms.CharField(
        label="Imię",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Nazwisko",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_of_birth = forms.DateField(
        label="Data urodzenia",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    guardian_email = forms.EmailField(
        label="E-mail opiekuna",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "np. opiekun@example.com"})
    )
    guardian_phone = forms.CharField(
        label="Telefon opiekuna",
        required=True,  # Wymagane przy rejestracji (dla SOS/SMS)
        help_text="Wpisz numer w formacie międzynarodowym, np. +48123123123.",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+48..."})
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "guardian_email",
            "guardian_phone",
            "password1",
            "password2",
        )

    def clean_guardian_phone(self):
        """Lekka normalizacja: usuń spacje i myślniki. Walidację formatu przeprowadza walidator modelu."""
        phone = self.cleaned_data.get("guardian_phone", "") or ""
        phone = phone.replace(" ", "").replace("-", "")
        return phone
