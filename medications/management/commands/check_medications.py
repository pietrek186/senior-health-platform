from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from medications.models import Medication
from django.conf import settings
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sprawdza stan leków i wysyła powiadomienia, jeśli coś się kończy lub zaraz się przeterminuje'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        all_medications = Medication.objects.select_related('user')

        for med in all_medications:
            user = med.user
            warnings = []

            # Sprawdzenie: czy lek się kończy
            if med.is_running_low():
                warnings.append(f"- Lek **{med.name}** kończy się (pozostało mniej niż 30%)")

            # Sprawdzenie: czy zaraz się przeterminuje
            if med.expiration_date:
                days_left = (med.expiration_date - today).days
                if days_left <= 7:
                    warnings.append(f"- Lek **{med.name}** ma ważność tylko do {med.expiration_date} (za {days_left} dni)")

            # Jeśli są ostrzeżenia – wysyłamy e-mail
            if warnings:
                subject = "Powiadomienie z apteczki – ważne informacje o lekach"
                body = (
                    f"Dzień dobry {user.first_name},\n\n"
                    f"Z Twojej apteczki wynika, że:\n\n"
                    + "\n".join(warnings) +
                    "\n\nZadbaj o uzupełnienie zapasów lub skontaktuj się z lekarzem.\n\n"
                    "Pozdrawiamy,\nTwój asystent zdrowia"
                )

                recipient_list = [user.email]
                if user.guardian_email:
                    recipient_list.append(user.guardian_email)

                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=False
                )

                self.stdout.write(f"Wysłano powiadomienie do {user.email}")
