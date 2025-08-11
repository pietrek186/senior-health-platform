from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponse
from medications.utils import send_medication_notifications

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

def placeholder(request):
    return render(request, 'core/placeholder.html', {'section': request.path})

@login_required
def select_results(request):
    return render(request, 'core/select_results.html')

@login_required
def pressure_results(request):
    return render(request, 'pressure/pressure_results.html')  # do stworzenia


def test_email(request):
    send_mail(
        subject='Test e-maila z aplikacji Django',
        message='To jest wiadomość testowa wysłana z projektu ZdrowieApp.',
        from_email=None,  # użyje DEFAULT_FROM_EMAIL z settings.py
        recipient_list=['zdrowieapp2025@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse('E-mail został wysłany!')


def test_alerts(request):
    send_medication_alerts()
    return HttpResponse("Powiadomienia zostały wysłane.")