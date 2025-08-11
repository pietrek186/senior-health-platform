from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Reminder

class ReminderCronJob(CronJobBase):
    # uruchamiaj co 1 minutę (dopasuj do swojego Task Scheduler)
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reminders.reminder_cron_job'

    def do(self):
        now = timezone.now()

        # Bierzemy aktywne, których czas nadszedł
        due = Reminder.objects.filter(is_active=True, next_run__lte=now)

        for r in due:
            # bezpieczeństwo: upewnij się, że user ma email
            recipient = getattr(r.user, 'email', None)
            if not recipient:
                # brak e-maila użytkownika — pomiń to przypomnienie i przesuń dalej/wyłącz
                r.last_sent = now
                r.schedule_next()
                r.save()
                continue

            subject = f"Przypomnienie: {r.title}"
            when_str = timezone.localtime(r.next_run).strftime("%Y-%m-%d %H:%M")
            message = (
                f"Cześć {r.user.first_name or r.user.username},\n\n"
                f"To jest przypomnienie: {r.title}\n"
                f"Zaplanowane na: {when_str}\n\n"
                f"Pozdrawiamy,\nZespół Zdrowie"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    recipient_list=[recipient],
                    fail_silently=False,
                )
            except Exception:
                # w realu: zaloguj błąd
                pass

            # zaktualizuj status po „wysłaniu”
            r.last_sent = now
            r.schedule_next()
            r.save()
