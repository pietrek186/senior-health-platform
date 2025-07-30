from django.db import models
from django.conf import settings


class PressureMeasurement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    systolic = models.IntegerField(verbose_name="Ciśnienie skurczowe (mmHg)")
    diastolic = models.IntegerField(verbose_name="Ciśnienie rozkurczowe (mmHg)")
    date = models.DateField(verbose_name="Data pomiaru")
    time = models.TimeField(verbose_name="Godzina pomiaru")

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time} - {self.systolic}/{self.diastolic} mmHg"
