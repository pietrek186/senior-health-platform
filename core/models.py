from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator  

phone_validator = RegexValidator(           
    regex=r'^\+?[1-9]\d{7,14}$',
    message="Podaj numer w formacie międzynarodowym, np. +48123123123."
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Użytkownik musi posiadać adres e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    guardian_email = models.EmailField()
    guardian_phone = models.CharField(           
        max_length=16,
        blank=True,
        validators=[phone_validator],
        help_text="Numer telefonu opiekuna w formacie międzynarodowym, np. +48..."
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth', 'guardian_email', 'guardian_phone']  

    def __str__(self):
        return self.email
