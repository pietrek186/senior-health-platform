from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import GlucoseMeasurement
from .forms import GlucoseMeasurementForm
import csv

@login_required
def glucose_home(request):
    return redirect('glucose_results')

@login_required
def add_glucose_measurement(request):
    if request.method == 'POST':
        form = GlucoseMeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = request.user
            measurement.save()
            messages.success(request, 'Pomyślnie zapisano pomiar glukozy.')
            return redirect('glucose_results')
    else:
        form = GlucoseMeasurementForm()
    return render(request, 'glucose/add_measurement.html', {'form': form})

@login_required
def glucose_results(request):
    measurements = GlucoseMeasurement.objects.filter(user=request.user)
    return render(request, 'glucose/glucose_results.html', {'measurements': measurements})

@login_required
def edit_glucose(request, pk):
    measurement = get_object_or_404(GlucoseMeasurement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GlucoseMeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pomyślnie zaktualizowano pomiar.')
            return redirect('glucose_results')
    else:
        form = GlucoseMeasurementForm(instance=measurement)
    return render(request, 'glucose/edit_measurement.html', {'form': form})

@login_required
def delete_glucose(request, pk):
    measurement = get_object_or_404(GlucoseMeasurement, pk=pk, user=request.user)
    if request.method == 'POST':
        measurement.delete()
        messages.success(request, 'Pomyślnie usunięto pomiar.')
        return redirect('glucose_results')
    return render(request, 'glucose/delete_measurement.html', {'measurement': measurement})

@login_required
def export_glucose_csv(request):
    measurements = GlucoseMeasurement.objects.filter(user=request.user).order_by('date', 'time')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="glucose_measurements.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'Godzina', 'Poziom glukozy (mg/dL)'])
    for m in measurements:
        writer.writerow([m.date.strftime('%Y-%m-%d'), m.time.strftime('%H:%M'), m.value])

    return response
