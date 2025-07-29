from django.db import models
from django.conf import settings

class GlucoseMeasurement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    value = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time} - {self.value} mg/dL"
