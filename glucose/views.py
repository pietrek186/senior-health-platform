from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import GlucoseMeasurementForm

@login_required
def glucose_home(request):
    return redirect('add_glucose')

@login_required
def add_glucose_measurement(request):
    if request.method == 'POST':
        form = GlucoseMeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = request.user
            measurement.save()
            messages.success(request, 'Pomyślnie zapisano pomiar cukru.')
            return redirect('dashboard')  # możesz tu zmienić na listę pomiarów później
    else:
        form = GlucoseMeasurementForm()
    return render(request, 'glucose/add_measurement.html', {'form': form})
