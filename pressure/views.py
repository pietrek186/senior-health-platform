from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PressureMeasurementForm

@login_required
def pressure_home(request):
    if request.method == 'POST':
        form = PressureMeasurementForm(request.POST)
        if form.is_valid():
            pressure = form.save(commit=False)
            pressure.user = request.user
            pressure.save()
            return redirect('dashboard') 
    else:
        form = PressureMeasurementForm()

    return render(request, 'pressure/add_pressure.html', {'form': form})
