from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

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