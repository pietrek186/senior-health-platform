from django.db import models
from django.conf import settings

class Reminder(models.Model):
    title = models.CharField(max_length=255)  # Tytuł przypomnienia
    date = models.DateField()                 # Data przypomnienia
    time = models.TimeField()                 # Godzina przypomnienia
    recurrence = models.CharField(            # Powtarzalność (opcjonalna)
        max_length=50,
        choices=[
            ('daily', 'Codziennie'),
            ('weekly', 'Co tydzień')
        ],
        blank=True,
        null=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
