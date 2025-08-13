# medications/utils.py
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from .models import Medication, MedicationNotificationLog
from core.models import CustomUser


def send_medication_notifications(user):
    """
    Wysyła powiadomienia o niskim stanie/kończącej się ważności leków.
    Zabezpieczenie przed duplikatami:
      - na początku próbujemy UTWORZYĆ log (user, date) get_or_create.
      - jeśli log już istnieje (created == False) -> inny proces już wysyła/ wysłał maila -> wyjście.
      - jeśli po obliczeniach nie ma nic do wysłania -> kasujemy utworzony log (żeby nie śmiecić).
    """
    today = timezone.localdate()

    # 1) Lock na poziomie DB – tylko jeden proces dziennie wejdzie dalej dla danego usera
    log_obj, created = MedicationNotificationLog.objects.get_or_create(user=user, date=today)
    if not created:
        # ktoś już wysłał / właśnie wysyła dzisiaj – kończymy
        return

    # 2) Dla pewności – odśwież dane użytkownika (aktualne imię/nazwisko/email)
    user = CustomUser.objects.get(pk=user.pk)

    low_stock = []
    expiring = []

    # 3) Zlicz co trzeba wysłać
    for med in user.medication_set.all():
        # Niski stan
        try:
            if med.is_running_low():
                low_stock.append(med.name)
        except Exception:
            # ostrożność: gdyby z jakiegoś powodu wyliczenie się nie powiodło, nie blokuj całej pętli
            pass

        # Ważność ≤7 dni (włącznie z dziś)
        if med.expiration_date:
            days_left = (med.expiration_date - today).days
            if days_left == 0:
                expiring.append((med.name, 0))
            elif 0 < days_left <= 7:
                expiring.append((med.name, days_left))

    # 4) Jeśli nie ma nic do powiadomienia – usuń „pusty” log i wyjdź
    if not low_stock and not expiring:
        log_obj.delete()
        return

    # 5) Wiadomość do użytkownika
    message_user = f"Dzień dobry {user.first_name},\n\n"
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
        subject="Powiadomienie o lekach – ZdrowieApp",
        message=message_user,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )

    # 6) Wiadomość do opiekuna (jeśli jest)
    if user.guardian_email:
        message_guardian = "Dzień dobry,\n\n"
        message_guardian += (
            f"Poniżej znajduje się lista leków użytkownika {user.first_name}, które wymagają uwagi:\n\n"
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
            subject="Powiadomienie o lekach – ZdrowieApp",
            message=message_guardian,
            from_email=None,
            recipient_list=[user.guardian_email],
            fail_silently=False,
        )


# Funkcja do użycia przez django-cron
def check_and_send_medication_alerts():
    # iterujemy po użytkownikach, którzy mają jakiekolwiek leki
    users_with_meds = CustomUser.objects.filter(medication__isnull=False).distinct()
    for user in users_with_meds:
        send_medication_notifications(user)
