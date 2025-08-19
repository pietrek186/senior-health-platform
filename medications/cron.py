from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.core.cache import cache
from .utils import check_and_send_medication_alerts


class MedicationAlertCronJob(CronJobBase):
    """
    Cron leków:
    - uruchamia się co minutę
    - wysyła powiadomienia tylko o 13:00
    - posiada blokadę na poziomie "tej samej minuty", żeby nie było dubletów
    """
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'medications.medication_alert_cron'

    TARGET_HOUR = 13
    TARGET_MINUTE = 0

    def do(self):
        now_local = timezone.localtime(timezone.now())

        if not (now_local.hour == self.TARGET_HOUR and now_local.minute == self.TARGET_MINUTE):
            return

        cache_key = f"medications_cron_lock_{now_local.strftime('%Y%m%d_%H%M')}"
        if cache.get(cache_key):
            return

        check_and_send_medication_alerts()

        cache.set(cache_key, True, timeout=90)
