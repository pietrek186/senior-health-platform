from django_cron import CronJobBase, Schedule
from .utils import check_and_send_medication_alerts

class MedicationAlertCronJob(CronJobBase):
    schedule = Schedule(run_at_times=['13:00']) 
    code = 'medications.medication_alert_cron'

    def do(self):
        check_and_send_medication_alerts()
