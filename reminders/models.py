from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time as dtime, timedelta

RECURRENCE_CHOICES = [
    ('daily', 'Codziennie'),
    ('weekly', 'Co tydzień'),
]

class Reminder(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()         # data startowa (dla pierwszego uruchomienia)
    time = models.TimeField()         # godzina wysyłki
    recurrence = models.CharField(max_length=50, choices=RECURRENCE_CHOICES, blank=True, null=True)

    # NOWE:
    next_run = models.DateTimeField(blank=True, null=True)   # najbliższy termin wysyłki (TZ-aware)
    last_sent = models.DateTimeField(blank=True, null=True)  # kiedy ostatnio wysłano (info)
    is_active = models.BooleanField(default=True)            # niecykliczne: po wysłaniu ustawiamy False
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def compute_initial_next_run(self):
        """
        Wylicza początkowe next_run na podstawie pól date+time (z uwzględnieniem strefy czasowej).
        Jeśli data/godzina już minęły – nie przesuwamy, cron sam wyśle „od razu” przy najbliższym przebiegu.
        """
        tz = timezone.get_current_timezone()
        dt = datetime.combine(self.date, self.time)
        return timezone.make_aware(dt, tz)

    def schedule_next(self):
        """
        Po wysłaniu:
        - jeśli cykliczne: przesuń next_run o 1 dzień / 7 dni
        - jeśli jednorazowe: wyłącz (is_active=False)
        """
        if self.recurrence == 'daily':
            self.next_run = self.next_run + timedelta(days=1)
        elif self.recurrence == 'weekly':
            self.next_run = self.next_run + timedelta(weeks=1)
        else:
            self.is_active = False
            self.next_run = None
