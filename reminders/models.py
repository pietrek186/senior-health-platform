from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

RECURRENCE_CHOICES = [
    ('daily', 'Codziennie'),
    ('weekly', 'Co tydzień'),
]

class Reminder(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    recurrence = models.CharField(max_length=50, choices=RECURRENCE_CHOICES, blank=True, null=True)

    next_run = models.DateTimeField(blank=True, null=True)
    last_sent = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def compute_initial_next_run(self):
        naive_dt = datetime.combine(self.date, self.time)
        local_aware = timezone.make_aware(naive_dt, timezone.get_current_timezone())
        return local_aware.astimezone(timezone.utc)

    def schedule_next(self):
        if self.recurrence == 'daily':
            self.next_run = self.next_run + timedelta(days=1)
        elif self.recurrence == 'weekly':
            self.next_run = self.next_run + timedelta(weeks=1)
        else:
            self.is_active = False
            self.next_run = None

    def save(self, *args, **kwargs):
        if self.next_run is None and self.date and self.time:
            self.next_run = self.compute_initial_next_run()
        super().save(*args, **kwargs)