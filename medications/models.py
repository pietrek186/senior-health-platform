from django.db import models
from django.conf import settings
from datetime import timedelta, date

LOW_STOCK_THRESHOLD = 0.30  # 30% zapasu

class Medication(models.Model):
    FORM_TABLET = 'tablet'
    FORM_SYRUP  = 'syrup'
    FORM_CHOICES = [
        (FORM_TABLET, 'Tabletki'),
        (FORM_SYRUP,  'Syrop'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField("Nazwa leku", max_length=100)
    form = models.CharField("Postać leku", max_length=10, choices=FORM_CHOICES, default=FORM_TABLET)
    # Tabletki
    quantity = models.PositiveIntegerField("Ilość tabletek")
    dosage = models.CharField("Dawkowanie (np. 1 tabletka 2× dziennie)", max_length=100, blank=True)
    # Syrop
    volume_ml = models.PositiveIntegerField("Objętość syropu (ml)", null=True, blank=True)
    dosage_ml_per_time = models.PositiveIntegerField("Dawka syropu (ml)", null=True, blank=True)
    # Wspólne
    frequency = models.PositiveIntegerField("Częstotliwość dawkowania (ile razy dziennie)", default=1)
    dosage_amount = models.PositiveIntegerField("Ilość leku na dawkę (np. 2 tabletki/ml)", default=1)
    start_date = models.DateField("Data rozpoczęcia stosowania")
    prescription_required = models.BooleanField("Czy lek na receptę?", default=False)
    expiration_date = models.DateField("Data ważności", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def estimated_end_date(self):
        """Zwraca datę wyczerpania zapasu (przybliżenie)."""
        if self.form == self.FORM_TABLET:
            daily = (self.dosage_amount or 1) * (self.frequency or 1)
            days = self.quantity // daily if daily else 0
        else:  # syrop
            per = (self.dosage_ml_per_time or 1)
            freq = (self.frequency or 1)
            doses = (self.volume_ml or 0) // per if per else 0
            days = doses // freq if freq else 0
        return self.start_date + timedelta(days=days)

    def days_to_expiry(self):
        """Ile dni zostało do końca ważności (może zwrócić liczbę ujemną, jeśli przeterminowany)."""
        if not self.expiration_date:
            return None
        return (self.expiration_date - date.today()).days

    def is_expiring_soon(self):
        """True, gdy ważność kończy się w ciągu 7 dni (włącznie), ale lek jeszcze nie jest przeterminowany."""
        d = self.days_to_expiry()
        return d is not None and 0 <= d <= 7

    def is_expired(self):
        return bool(self.expiration_date and self.expiration_date < date.today())

    @property
    def remaining_quantity(self):
        """
        Aktualny pozostały stan (tabletki lub ml), liczony od start_date
        na podstawie dawki (dosage_amount / dosage_ml_per_time) i frequency.
        """
        if not self.start_date:
            return self.volume_ml if self.form == self.FORM_SYRUP else self.quantity

        days_used = (date.today() - self.start_date).days
        if days_used < 0:
            return self.volume_ml if self.form == self.FORM_SYRUP else self.quantity

        if self.form == self.FORM_TABLET:
            daily_usage = (self.dosage_amount or 1) * (self.frequency or 1)
            used = daily_usage * days_used
            return max(self.quantity - used, 0)

        elif self.form == self.FORM_SYRUP:
            per = self.dosage_ml_per_time or 1
            freq = self.frequency or 1
            used_ml = per * freq * days_used
            return max((self.volume_ml or 0) - used_ml, 0)

        return self.quantity

    def is_out(self):
        """True, gdy zapas dokładnie się skończył (0)."""
        return (self.remaining_quantity or 0) <= 0

    def is_running_low(self):
        """
        True, gdy zostało <= 30% zapasu.
        - tabletki: prog = 30% quantity (początkowej)
        - syrop:    prog = 30% volume_ml (początkowej)
        """
        remaining = self.remaining_quantity or 0
        if self.form == self.FORM_TABLET:
            threshold = (self.quantity or 0) * LOW_STOCK_THRESHOLD
        else:
            threshold = (self.volume_ml or 0) * LOW_STOCK_THRESHOLD
        return remaining <= threshold

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class MedicationNotificationLog(models.Model):
    """
    Minimalny dzienny log wysłania powiadomień dla użytkownika.
    Dzięki unikalności (user, date) zapobiegamy podwójnej wysyłce,
    nawet jeśli zadanie uruchomi się dwa razy.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medication_notification_logs'
    )
    date = models.DateField()  # lokalna data „dzisiejsza”
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"Notifications sent for {self.user.email} on {self.date}"
