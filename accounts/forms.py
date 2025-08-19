from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="Imię",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Nazwisko",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    #Format zgodny z datą z inputa + akceptacja polskiego zapisu
    date_of_birth = forms.DateField(
        label="Data urodzenia",
        input_formats=["%Y-%m-%d", "%d.%m.%Y"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "date_of_birth", "email"]

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)
        if qs.exists():
            raise forms.ValidationError("Podany e-mail jest już zajęty.")
        return email


class GuardianForm(forms.ModelForm):
    guardian_email = forms.EmailField(
        label="E-mail opiekuna",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    guardian_phone = forms.CharField(
        label="Telefon opiekuna",
        required=True,
        help_text="Wpisz numer w formacie międzynarodowym, np. +48123123123.",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+48..."})
    )

    class Meta:
        model = User
        fields = ["guardian_email", "guardian_phone"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if instance and getattr(instance, "guardian_phone", None):
            self.fields["guardian_phone"].initial = instance.guardian_phone

    def clean_guardian_phone(self):
        phone = (self.cleaned_data.get("guardian_phone") or "").replace(" ", "").replace("-", "")
        return phone


class PasswordChangeOptionalForm(forms.Form):
    old_password = forms.CharField(
        label="Aktualne hasło",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password1 = forms.CharField(
        label="Nowe hasło",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password2 = forms.CharField(
        label="Powtórz nowe hasło",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get("old_password")
        if not self.user.check_password(old):
            raise forms.ValidationError("Nieprawidłowe aktualne hasło.")
        return old

    def clean(self):
        cleaned = super().clean()
        old = cleaned.get("old_password")
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")

        if not p1 and not p2:
            self.add_error("new_password1", "Podaj nowe hasło.")
            self.add_error("new_password2", "Powtórz nowe hasło.")
            return cleaned

        if not p1:
            self.add_error("new_password1", "Podaj nowe hasło.")
            return cleaned

        if not p2:
            self.add_error("new_password2", "Powtórz nowe hasło.")
            return cleaned

        if p1 != p2:
            self.add_error("new_password2", "Hasła muszą być identyczne.")
            return cleaned

        #Sprawdzenie czy nowe hasło nie jest starym hasłem
        if old and p1 == old:
            self.add_error("new_password1", "Nowe hasło nie może być takie samo jak aktualne.")
            self.add_error("new_password2", "Nowe hasło nie może być takie samo jak aktualne.")
            return cleaned

        #Walidacja hasła
        try:
            validate_password(p1, self.user)
        except forms.ValidationError as e:
            self.add_error("new_password1", e)
            return cleaned

        return cleaned

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
