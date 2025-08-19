from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import BMIForm
from .models import BMIRecord
from django.contrib.auth.decorators import login_required

def get_bmi_category(bmi):
    if bmi < 16.0:
        return "Wygłodzenie"
    elif bmi < 17.0:
        return "Wychudzenie"
    elif bmi < 18.5:
        return "Niedowaga"
    elif bmi < 25.0:
        return "Masa prawidłowa"
    elif bmi < 30.0:
        return "Nadwaga"
    elif bmi < 35.0:
        return "Otyłość I stopnia"
    elif bmi < 40.0:
        return "Otyłość II stopnia"
    else:
        return "Otyłość III stopnia"

BMI_ZONES = [
    {"name": "Wygłodzenie", "min": 0, "max": 15.99, "width": 16},
    {"name": "Wychudzenie", "min": 16.0, "max": 16.99, "width": 1},
    {"name": "Niedowaga", "min": 17.0, "max": 18.49, "width": 1.5},
    {"name": "Masa prawidłowa", "min": 18.5, "max": 24.99, "width": 6.5},
    {"name": "Nadwaga", "min": 25.0, "max": 29.99, "width": 5},
    {"name": "Otyłość I stopnia", "min": 30.0, "max": 34.99, "width": 5},
    {"name": "Otyłość II stopnia", "min": 35.0, "max": 39.99, "width": 5},
    {"name": "Otyłość III stopnia", "min": 40.0, "max": 50.0, "width": 10},
]

def calculate_marker_position(bmi):
    total_width = sum(zone["width"] for zone in BMI_ZONES)
    current_pos = 0
    for zone in BMI_ZONES:
        if zone["min"] <= bmi <= zone["max"]:
            local_ratio = (bmi - zone["min"]) / (zone["max"] - zone["min"])
            local_pos = local_ratio * zone["width"]
            position_percent = ((current_pos + local_pos) / total_width) * 100
            return round(position_percent, 1)
        current_pos += zone["width"]
    return 100.0

@login_required
def bmi_view(request):
    if request.method == 'POST':
        form = BMIForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            height = form.cleaned_data['height']
            height_m = height / 100
            bmi = round(weight / (height_m ** 2), 1)
            category = get_bmi_category(bmi)
            marker_position = calculate_marker_position(bmi)

            BMIRecord.objects.create(
                user=request.user,
                weight=weight,
                height=height,
                bmi=bmi,
                category=category
            )

            notes = {
                "Wygłodzenie": "Twoja masa ciała jest skrajnie niska, co może wskazywać na poważne niedożywienie. Skontaktuj się z lekarzem, aby ustalić przyczynę i wdrożyć leczenie.",
                "Wychudzenie": "Twoja masa ciała jest zbyt niska. Może to prowadzić do osłabienia odporności i zaburzeń hormonalnych. Warto skonsultować się z dietetykiem lub lekarzem.",
                "Niedowaga": "Twoja masa ciała jest poniżej normy. Zadbaj o odpowiednią dietę i skonsultuj się z lekarzem, aby zapobiec ewentualnym problemom zdrowotnym.",
                "Masa prawidłowa": "Twoja masa ciała jest w normie. Gratulacje! Utrzymuj zdrowy styl życia i regularną aktywność fizyczną.",
                "Nadwaga": "Masz lekką nadwagę. Warto zadbać o zbilansowaną dietę i codzienną aktywność, aby uniknąć rozwoju otyłości.",
                "Otyłość I stopnia": "Masa ciała jest zbyt wysoka. Warto skonsultować się z lekarzem, który zaproponuje zmiany w stylu życia, by uniknąć powikłań zdrowotnych.",
                "Otyłość II stopnia": "BMI wskazuje na otyłość II stopnia. To poważny czynnik ryzyka chorób serca, cukrzycy i nadciśnienia. Skontaktuj się z lekarzem.",
                "Otyłość III stopnia": "BMI wskazuje na otyłość III stopnia (tzw. otyłość olbrzymia). Wymagana jest pilna konsultacja medyczna i wsparcie specjalisty.",
            }

            alert_classes = {
                "Wygłodzenie": "danger",
                "Wychudzenie": "warning",
                "Niedowaga": "warning",
                "Masa prawidłowa": "success",
                "Nadwaga": "warning",
                "Otyłość I stopnia": "danger",
                "Otyłość II stopnia": "danger",
                "Otyłość III stopnia": "danger",
            }

            note = notes.get(category, "")
            alert_class = alert_classes.get(category, "info")

            context = {
                'form': form,
                'result': {
                    'bmi': bmi,
                    'category': category,
                    'marker_position': f"{marker_position:.1f}".replace(',', '.'),
                    'note': note,
                    'alert_class': alert_class
                }
            }
            return render(request, 'bmi/bmi_form.html', context)
    else:
        form = BMIForm()

    return render(request, 'bmi/bmi_form.html', {'form': form})

@login_required
def bmi_history(request):
    records = BMIRecord.objects.filter(user=request.user).order_by('-created_at')

    category_classes = {
        'Wygłodzenie': 'wyglodzenie',
        'Wychudzenie': 'wychudzenie',
        'Niedowaga': 'niedowaga',
        'Masa prawidłowa': 'masa-prawidlowa',
        'Nadwaga': 'nadwaga',
        'Otyłość I stopnia': 'otylosc-i-stopnia',
        'Otyłość II stopnia': 'otylosc-ii-stopnia',
        'Otyłość III stopnia': 'otylosc-iii-stopnia',
    }

    for record in records:
        record.css_class = category_classes.get(record.category, '')

    return render(request, 'bmi/bmi_history.html', {'records': records})

@login_required
def delete_bmi_record(request, record_id):
    record = get_object_or_404(BMIRecord, id=record_id, user=request.user)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Rekord BMI został usunięty.")
        return redirect('bmi_history')
    return render(request, 'bmi/delete_bmi.html', {'record': record})
