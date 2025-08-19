from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from .models import Medication
from .forms import MedicationForm
from .utils import send_medication_notifications


@login_required
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user

            if med.form == Medication.FORM_TABLET:
                med.quantity = form.cleaned_data.get('quantity') or 0
                med.dosage_amount = form.cleaned_data.get('dosage_amount') or 1
                med.frequency = form.cleaned_data.get('frequency') or 1

            elif med.form == Medication.FORM_SYRUP:
                med.volume_ml = form.cleaned_data.get('volume_ml') or 0
                med.dosage_ml_per_time = form.cleaned_data.get('dosage_ml_per_time') or 0
                med.frequency = form.cleaned_data.get('frequency') or 1
                med.quantity = 0

            med.save()
            messages.success(request, 'Lek został pomyślnie dodany do apteczki.')
            return redirect('medication_list')
    else:
        form = MedicationForm(initial={'form': Medication.FORM_TABLET})
    return render(request, 'medications/add_medication.html', {'form': form})


@login_required
def medication_list(request):
    medications = Medication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'medications/medication_list.html', {
        'medications': medications
    })


@login_required
def edit_medication(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=med)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user

            if med.form == Medication.FORM_TABLET:
                if med.quantity is None:
                    med.quantity = 0
                if not med.dosage_amount:
                    med.dosage_amount = 1

            elif med.form == Medication.FORM_SYRUP:
                pass

            med.save()
            messages.success(request, 'Lek został pomyślnie zaktualizowany.')
            return redirect('medication_list')
    else:
        initial = {'form': med.form}
        if med.form == Medication.FORM_TABLET:
            initial['quantity'] = int(med.remaining_quantity or 0)
        elif med.form == Medication.FORM_SYRUP:
            initial['volume_ml'] = int(med.remaining_quantity or 0)

        form = MedicationForm(instance=med, initial=initial)

    return render(request, 'medications/edit_medication.html', {
        'form': form,
        'med': med
    })


@login_required
def delete_medication(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == 'POST':
        med.delete()
        messages.success(request, 'Lek został pomyślnie usunięty.')
        return redirect('medication_list')
    return render(request, 'medications/delete_medication.html', {'medication': med})


@login_required
def export_medications_csv(request):
    qs = Medication.objects.filter(user=request.user).order_by('-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="apteczka.csv"'
    response.write('\ufeff')
    response.write('sep=;\r\n')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Nazwa',
        'Postać',
        'Ilość (pozostała)',
        'Częstotliwość (razy/dzień)',
        'Data rozpoczęcia',
        'Data ważności',
        'Na receptę',
    ])
    for m in qs:
        current_qty = int(m.remaining_quantity or 0)
        writer.writerow([
            m.name,
            dict(Medication.FORM_CHOICES)[m.form],
            current_qty,
            m.frequency,
            m.start_date.strftime('%Y-%m-%d') if m.start_date else '',
            m.expiration_date.strftime('%Y-%m-%d') if m.expiration_date else '',
            'Tak' if m.prescription_required else 'Nie',
        ])

    return response


@login_required
def test_notifications(request):
    send_medication_notifications(request.user)
    return HttpResponse("Powiadomienia zostały wysłane (jeśli były potrzebne).")
