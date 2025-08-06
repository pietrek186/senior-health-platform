from django.db import models
from django.conf import settings
from datetime import timedelta

class Medication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField("Nazwa leku", max_length=100)
    quantity = models.PositiveIntegerField("Ilość tabletek w opakowaniu")
    start_date = models.DateField("Data rozpoczęcia stosowania")
    frequency = models.PositiveIntegerField("Częstotliwość dawkowania (ile razy dziennie)", default=1)
    prescription_required = models.BooleanField("Czy lek na receptę?", default=False)
    expiration_date = models.DateField("Data ważności", null=True, blank=True)

    def estimated_end_date(self):
        if self.frequency and self.quantity:
            days = self.quantity // self.frequency
            return self.start_date + timedelta(days=days)
        return None

    def is_running_low(self):
        estimated_end = self.estimated_end_date()
        if estimated_end:
            return estimated_end <= (self.start_date + timedelta(days=self.quantity // self.frequency - 3))
        return False

    def __str__(self):
        return f"{self.name} ({self.user.username})"
