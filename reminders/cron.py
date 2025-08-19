from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Reminder

class ReminderCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reminders.reminder_cron_job'

    def do(self):
        now = timezone.now()

        print("=== REMINDERS CRON START ===")
        print("NOW (UTC):", now)

        due = Reminder.objects.filter(is_active=True, next_run__lte=now)

        print("DUE reminders count:", due.count())

        for r in due:
            recipient = getattr(r.user, 'email', None)
            print(f"[Reminder #{r.id}] title='{r.title}' next_run(UTC)={r.next_run} recipient={recipient}")

            if not recipient:
                r.last_sent = now
                r.schedule_next()
                r.save()
                continue

            subject = f"Przypomnienie: {r.title}"
            when_str_local = timezone.localtime(r.next_run).strftime("%Y-%m-%d %H:%M")
            message = (
                f"Cześć {r.user.first_name or r.user.username},\n\n"
                f"To jest przypomnienie: {r.title}\n"
                f"Zaplanowane na: {when_str_local}\n\n"
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
                print(f"Mail sent to {recipient}")
            except Exception as e:
                print("Błąd wysyłki maila:", e)

            r.last_sent = now
            r.schedule_next()
            r.save()

        print("=== REMINDERS CRON END ===")
