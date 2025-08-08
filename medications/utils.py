from django.core.mail import send_mail
from django.utils import timezone
from .models import Medication
from core.models import CustomUser  

def send_medication_notifications(user):
    today = timezone.now().date()
    low_stock = []
    expiring = []

    for med in user.medication_set.all():
        if med.is_running_low():
            low_stock.append(med.name)
        if med.expiration_date and (med.expiration_date - today).days == 7:
            expiring.append((med.name, 7))
        elif med.expiration_date and 0 < (med.expiration_date - today).days < 7:
            days_left = (med.expiration_date - today).days
            expiring.append((med.name, days_left))
        elif med.expiration_date == today:
            expiring.append((med.name, 0))

    if not low_stock and not expiring:
        return

    # Wiadomość do użytkownika
    message_user = f"Dzień dobry {user.first_name},\n\n"
    message_user += "Poniżej znajduje się lista leków, które wymagają Twojej uwagi:\n\n"

    for med_name in low_stock:
        message_user += f"- Lek **{med_name}** ma niski poziom zapasu (≤30%).\n"

    for med_name, days_left in expiring:
        if days_left == 0:
            message_user += f"- Lek **{med_name}** traci ważność **dzisiaj**.\n"
        else:
            message_user += f"- Lek **{med_name}** traci ważność za {days_left} dni.\n"

    message_user += "\nPozdrawiamy,\nZespół ZdrowieApp"

    send_mail(
        subject="Powiadomienie o lekach – ZdrowieApp",
        message=message_user,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )

    # Wiadomość do opiekuna
    message_guardian = f"Dzień dobry,\n\n"
    message_guardian += f"Poniżej znajduje się lista leków użytkownika {user.first_name}, które wymagają uwagi:\n\n"

    for med_name in low_stock:
        message_guardian += f"- Lek **{med_name}** ma niski poziom zapasu (≤30%).\n"

    for med_name, days_left in expiring:
        if days_left == 0:
            message_guardian += f"- Lek **{med_name}** traci ważność **dzisiaj**.\n"
        else:
            message_guardian += f"- Lek **{med_name}** traci ważność za {days_left} dni.\n"

    message_guardian += "\nPozdrawiamy,\nZespół ZdrowieApp"

    send_mail(
        subject="Powiadomienie o lekach – ZdrowieApp",
        message=message_guardian,
        from_email=None,
        recipient_list=[user.guardian_email],
        fail_silently=False,
    )


# Funkcja do użycia przez django-cron
def check_and_send_medication_alerts():
    users_with_meds = CustomUser.objects.filter(medication__isnull=False).distinct()
    for user in users_with_meds:
        send_medication_notifications(user)
