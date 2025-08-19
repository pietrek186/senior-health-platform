from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from .models import MedicationNotificationLog
from core.models import CustomUser


def send_medication_notifications(user):
    today = timezone.localdate()

    with transaction.atomic():
        log_obj, created = MedicationNotificationLog.objects.get_or_create(
            user=user, date=today
        )
        if not created:
            return

    user = CustomUser.objects.get(pk=user.pk)

    low_stock = []
    expiring = []

    for med in user.medication_set.all():
        try:
            if med.is_running_low():
                low_stock.append(med.name)
        except Exception:
            pass

        if med.expiration_date:
            days_left = (med.expiration_date - today).days
            if days_left == 0:
                expiring.append((med.name, 0))
            elif 0 < days_left <= 7:
                expiring.append((med.name, days_left))

    if not low_stock and not expiring:
        log_obj.delete()
        return

    if (user.email or "").strip():
        message_user = f"Dzień dobry {user.first_name or user.last_name or ''},\n\n"
        message_user += "Poniżej znajduje się lista leków, które wymagają Twojej uwagi:\n\n"

        for med_name in low_stock:
            message_user += f"- Lek {med_name} ma niski poziom zapasu (≤30%).\n"

        for med_name, days_left in expiring:
            if days_left == 0:
                message_user += f"- Lek {med_name} traci ważność dzisiaj.\n"
            else:
                message_user += f"- Lek {med_name} traci ważność za {days_left} dni.\n"

        message_user += "\nPozdrawiamy,\nZespół ZdrowieApp"

        send_mail(
            subject="Powiadomienie o lekach - ZdrowieApp",
            message=message_user,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

    guardian_mail = (user.guardian_email or "").strip()
    if guardian_mail:
        message_guardian = "Dzień dobry,\n\n"
        message_guardian += (
            f"Poniżej znajduje się lista leków użytkownika {user.first_name or ''}, które wymagają uwagi:\n\n"
        )

        for med_name in low_stock:
            message_guardian += f"- Lek {med_name} ma niski poziom zapasu (≤30%).\n"

        for med_name, days_left in expiring:
            if days_left == 0:
                message_guardian += f"- Lek {med_name} traci ważność dzisiaj.\n"
            else:
                message_guardian += f"- Lek {med_name} traci ważność za {days_left} dni.\n"

        message_guardian += "\nPozdrawiamy,\nZespół ZdrowieApp"

        send_mail(
            subject="Powiadomienie o lekach - ZdrowieApp",
            message=message_guardian,
            from_email=None,
            recipient_list=[guardian_mail],
            fail_silently=False,
        )

def check_and_send_medication_alerts():
    users_with_meds = CustomUser.objects.filter(medication__isnull=False).distinct()
    for user in users_with_meds:
        send_medication_notifications(user)
