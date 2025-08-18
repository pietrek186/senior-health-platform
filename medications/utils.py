# medications/utils.py
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from .models import Medication, MedicationNotificationLog
from core.models import CustomUser


def send_medication_notifications(user):
    """
    Wysyła powiadomienia o niskim stanie/kończącej się ważności leków.
    Anty-dup:
      - transakcyjny get_or_create logu (user, date) na początku
      - jeśli log już istnieje -> kończymy (drugi proces w tej dacie nie wyśle)
      - jeśli po obliczeniach brak pozycji -> usuwamy log (nic dziś nie było do wysłania)
    """
    today = timezone.localdate()

    # 1) Jednorazowość per user/dzień (odporne na wyścig)
    with transaction.atomic():
        log_obj, created = MedicationNotificationLog.objects.get_or_create(
            user=user, date=today
        )
        if not created:
            # Ktoś już wysłał / właśnie wysyła dzisiaj – koniec
            return

    # 2) Odśwież dane użytkownika
    user = CustomUser.objects.get(pk=user.pk)

    low_stock = []
    expiring = []

    # 3) Zlicz pozycje do wysłania
    for med in user.medication_set.all():
        # Niski stan (<= 30%)
        try:
            if med.is_running_low():
                low_stock.append(med.name)
        except Exception:
            # ostrożnościowo nie blokuj całości na jednym wyjątku
            pass

        # Ważność (dzisiaj lub w ciągu 7 dni)
        if med.expiration_date:
            days_left = (med.expiration_date - today).days
            if days_left == 0:
                expiring.append((med.name, 0))
            elif 0 < days_left <= 7:
                expiring.append((med.name, days_left))

    # 4) Nic do wysłania -> usuń log i wyjdź
    if not low_stock and not expiring:
        log_obj.delete()
        return

    # 5) E-mail do użytkownika (jeśli ma e-mail)
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
            subject="Powiadomienie o lekach – ZdrowieApp",
            message=message_user,
            from_email=None,  # użyje DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=False,
        )

    # 6) E-mail do opiekuna (jeśli jest)
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
            subject="Powiadomienie o lekach – ZdrowieApp",
            message=message_guardian,
            from_email=None,
            recipient_list=[guardian_mail],
            fail_silently=False,
        )

    # 7) Log zostawiamy (już utworzony na początku) – gwarant jednego maila dzisiaj


def check_and_send_medication_alerts():
    # Użytkownicy mający jakiekolwiek leki
    users_with_meds = CustomUser.objects.filter(medication__isnull=False).distinct()
    for user in users_with_meds:
        send_medication_notifications(user)
