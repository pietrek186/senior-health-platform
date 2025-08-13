from django.db import models
from django.conf import settings


def medical_upload_to(instance, filename: str) -> str:
    # media/medical_records/<user_id>/<yyyy>/<mm>/<plik>
    from datetime import datetime
    now = datetime.now()
    return f"medical_records/{instance.user_id}/{now:%Y}/{now:%m}/{filename}"

class MedicalFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medical_files")
    file = models.FileField(upload_to=medical_upload_to)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]  # najnowsze u góry

    def __str__(self) -> str:
        return f"{self.original_name} ({self.user.email})"
