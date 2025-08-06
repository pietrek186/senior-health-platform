from django.shortcuts import render, redirect, get_object_or_404
from .models import Medication
from .forms import MedicationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import csv
from django.http import HttpResponse

@login_required
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user
            medication.save()
            messages.success(request, 'Lek został pomyślnie dodany do apteczki.')
            return redirect('medication_list')
    else:
        form = MedicationForm()
    return render(request, 'medications/add_medication.html', {'form': form})


@login_required
def medication_list(request):
    medications = Medication.objects.filter(user=request.user).order_by('expiration_date')
    return render(request, 'medications/medication_list.html', {'medications': medications})


@login_required
def edit_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Lek został pomyślnie zaktualizowany.')
            return redirect('medication_list')
    else:
        form = MedicationForm(instance=medication)
    return render(request, 'medications/edit_medication.html', {'form': form})


@login_required
def delete_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == 'POST':
        medication.delete()
        messages.success(request, 'Lek został pomyślnie usunięty.')
        return redirect('medication_list')
    return render(request, 'medications/delete_medication.html', {'medication': medication})


@login_required
def export_medications_csv(request):
    # Pobieramy wszystkie leki danego użytkownika
    meds = Medication.objects.filter(user=request.user).order_by('expiration_date')

    # Tworzymy odpowiedź z content_type UTF-8 i semikoną jako CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="apteczka.csv"'

    # **BOM** żeby Excel nie popsuł polskich znaków
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    # Nagłówki kolumn
    writer.writerow([
        'Nazwa',
        'Ilość',
        'Częstotliwość',
        'Data rozpoczęcia',
        'Data ważności',
        'Czy na receptę',
        'Status'
    ])

    for m in meds:
        writer.writerow([
            m.name,
            m.quantity,
            f"{m.frequency}x dziennie",
            m.start_date.strftime('%Y-%m-%d'),
            m.expiration_date.strftime('%Y-%m-%d'),
            'Tak' if m.prescription_required else 'Nie',
            'Kończy się' if m.is_running_low() else 'OK',
        ])

    return response