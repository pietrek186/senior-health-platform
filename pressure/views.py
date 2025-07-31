from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PressureMeasurementForm
from .models import PressureMeasurement
from django.contrib import messages


@login_required
def pressure_home(request):
    if request.method == 'POST':
        form = PressureMeasurementForm(request.POST)
        if form.is_valid():
            pressure = form.save(commit=False)
            pressure.user = request.user
            pressure.save()
            messages.success(request, 'Pomyślnie zapisano pomiar ciśnienia.')
            return redirect('pressure_results')
    else:
        form = PressureMeasurementForm()
        
    return render(request, 'pressure/add_pressure.html', {'form': form})


@login_required
def pressure_results(request):
    measurements = PressureMeasurement.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'pressure/pressure_results.html', {'measurements': measurements})


def edit_pressure(request, measurement_id):
    measurement = get_object_or_404(PressureMeasurement, id=measurement_id, user=request.user)
    if request.method == 'POST':
        form = PressureMeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pomyślnie zaktualizowano pomiar ciśnienia.')
            return redirect('pressure_results')
    else:
        form = PressureMeasurementForm(instance=measurement)
    return render(request, 'pressure/edit_pressure.html', {'form': form})


@login_required
def delete_pressure(request, measurement_id):
    measurement = get_object_or_404(PressureMeasurement, pk=measurement_id, user=request.user)
    if request.method == 'POST':
        measurement.delete()
        messages.success(request, 'Pomyślnie usunięto pomiar ciśnienia.')
        return redirect('pressure_results')
    return render(request, 'pressure/delete_pressure.html', {'measurement': measurement})
