from django.db import models
from django.conf import settings

class BMIRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    height = models.FloatField(null=True)
    weight = models.FloatField(null=True)
    bmi = models.FloatField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - BMI: {self.bmi} ({self.created_at})"
