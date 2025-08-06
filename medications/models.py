from django.db import models
from django.conf import settings
from datetime import timedelta, date

LOW_STOCK_THRESHOLD = 0.30  # 30% zapasu

class Medication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField("Nazwa leku", max_length=100)
    quantity = models.PositiveIntegerField("Ilość tabletek w opakowaniu")
    frequency = models.PositiveIntegerField("Częstotliwość dawkowania (ile razy dziennie)", default=1)
    start_date = models.DateField("Data rozpoczęcia stosowania")
    prescription_required = models.BooleanField("Czy lek na receptę?", default=False)
    expiration_date = models.DateField("Data ważności", null=True, blank=True)

    def estimated_end_date(self):
        if self.frequency and self.quantity:
            days = self.quantity // self.frequency
            return self.start_date + timedelta(days=days)
        return None

    def is_running_low(self):
        """
        Zwraca True gdy pozostało <= LOW_STOCK_THRESHOLD (np. 30%) tabletek.
        """
        # Ile dni od rozpoczęcia
        days_since = (date.today() - self.start_date).days
        # Ile tabletek zużyto
        consumed = days_since * self.frequency
        remaining = self.quantity - consumed
        if remaining < 0:
            remaining = 0
        # Sprawdzamy, czy pozostało mniej niż threshold*quantity
        return remaining <= (self.quantity * LOW_STOCK_THRESHOLD)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
