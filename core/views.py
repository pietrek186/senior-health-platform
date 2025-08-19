from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponse
from medications.utils import send_medication_notifications
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST


def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konto zostało utworzone pomyślnie. Możesz się teraz zalogować.')
            return redirect('login')  
    else:
        form = RegisterForm()
    
    return render(request, 'core/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Zalogowano pomyślnie.')
        return super().form_valid(form)
    

def custom_logout(request):
    logout(request)
    messages.success(request, "Wylogowano pomyślnie.")
    return redirect('login')
    

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@login_required
def select_results(request):
    return render(request, 'core/select_results.html')

@login_required
def pressure_results(request):
    return render(request, 'pressure/pressure_results.html')


def test_email(request):
    send_mail(
        subject='Test e-maila z aplikacji Django',
        message='To jest wiadomość testowa wysłana z projektu ZdrowieApp.',
        from_email=None,
        recipient_list=['zdrowieapp2025@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse('E-mail został wysłany!')


def test_alerts(request):
    send_medication_notifications()
    return HttpResponse("Powiadomienia zostały wysłane.")



@login_required
@require_POST
def sos_alert(request):
    user = request.user

    guardian_email = (getattr(user, "guardian_email", "") or "").strip()
    guardian_phone = (getattr(user, "guardian_phone", "") or "").strip()

    if not guardian_email:
        fallback = getattr(settings, "DEFAULT_GUARDIAN_EMAIL", "")
        if fallback:
            guardian_email = fallback

    now = timezone.localtime()
    full_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
    display_name = full_name if full_name else (user.email or "Użytkownik")

    subject = "ALERT SOS - potrzebna pomoc"
    body = (
        f"Użytkownik: {display_name} ({user.email})\n"
        f"Data i czas: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        "Komunikat: Użytkownik źle się poczuł i prosi o natychmiastowy kontakt/pomoc."
    )

    email_ok = False
    email_reason = ""
    if guardian_email:
        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[guardian_email],
                fail_silently=False,
            )
            email_ok = sent > 0
            if not email_ok:
                email_reason = "Serwer pocztowy nie przyjął wiadomości."
        except Exception as e:
            email_reason = f"Błąd e-mail: {e}"
    else:
        email_reason = "Brak adresu e-mail opiekuna."

    #Działa tylko, gdy SOS_SMS_ENABLED=True
    sms_ok = False
    sms_reason = ""
    sms_attempted = False

    if getattr(settings, "SOS_SMS_ENABLED", False):
        sms_attempted = True
        token = getattr(settings, "SMSAPI_TOKEN", None)

        if not guardian_phone:
            sms_reason = "Brak numeru telefonu opiekuna."
        elif not token:
            sms_reason = "Brak tokenu SMSAPI (SMSAPI_TOKEN)."
        else:
            try:
                url = "https://api.smsapi.pl/sms.do"

                safe_email = ""
                if user.email:
                    safe_email = user.email.replace("@", " [at] ").replace(".", " [dot] ")
                sms_text = f"SOS: {display_name} potrzebuje pomocy. Skontaktuj się pilnie."
                if safe_email:
                    sms_text += f" Email: {safe_email}"

                data = {
                    "to": guardian_phone,
                    "message": sms_text,
                    "format": "json",
                    "encoding": "utf-8",
                }
                sender = getattr(settings, "SMSAPI_SENDER", None)
                if sender:
                    data["from"] = sender
                if getattr(settings, "SMSAPI_NORMALIZE", False):
                    data["normalize"] = "1"
                if getattr(settings, "SMSAPI_TEST_MODE", False):
                    data["test"] = "1"

                import requests
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.post(url, data=data, headers=headers, timeout=10)

                if resp.status_code == 200:
                    ok = True
                    try:
                        j = resp.json()
                        if isinstance(j, dict) and j.get("error"):
                            ok = False
                            sms_reason = f"SMSAPI error: {j.get('message') or j.get('error')}"
                    except ValueError:
                        if "ERROR" in resp.text.upper():
                            ok = False
                            sms_reason = f"SMSAPI response: {resp.text}"
                    sms_ok = ok
                else:
                    sms_reason = f"HTTP {resp.status_code}: {resp.text[:120]}"
            except Exception as e:
                sms_reason = f"Błąd SMS: {e}"

    if sms_attempted:
        if email_ok and sms_ok:
            messages.success(request, "Wysłano alert SOS: e-mail i SMS.")
            if getattr(settings, "SMSAPI_TEST_MODE", False):
                messages.info(request, "Uwaga: SMS wysłany w trybie TESTOWYM (nie został fizycznie dostarczony).")
        elif email_ok and not sms_ok:
            messages.warning(request, f"Wysłano e-mail SOS, ale SMS nie został wysłany. {sms_reason}")
        elif sms_ok and not email_ok:
            messages.warning(request, f"Wysłano SMS SOS, ale e-mail nie został wysłany. {email_reason}")
        else:
            messages.error(request, f"Nie udało się wysłać alertu SOS. {email_reason} {sms_reason}".strip())
    else:
        if email_ok:
            messages.success(request, "Wysłano alert SOS e-mailem.")
        else:
            messages.error(request, f"Nie udało się wysłać alertu SOS e-mailem. {email_reason}")

    return redirect("dashboard")


@login_required
def forums(request):
    return render(request, "core/forums.html")

@login_required
def clinics_view(request):
    return render(request, "core/clinics.html")