from django.shortcuts import render, redirect
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
        return "Otyłość I"
    elif bmi < 40.0:
        return "Otyłość II"
    else:
        return "Otyłość III"

BMI_ZONES = [
    {"name": "Wygłodzenie", "min": 0, "max": 16, "width": 16},
    {"name": "Wychudzenie", "min": 16, "max": 17, "width": 1},
    {"name": "Niedowaga", "min": 17, "max": 18.5, "width": 1.5},
    {"name": "Masa prawidłowa", "min": 18.5, "max": 25, "width": 6.5},
    {"name": "Nadwaga", "min": 25, "max": 30, "width": 5},
    {"name": "Otyłość I", "min": 30, "max": 35, "width": 5},
    {"name": "Otyłość II", "min": 35, "max": 40, "width": 5},
    {"name": "Otyłość III", "min": 40, "max": 50, "width": 10},
]

def calculate_marker_position(bmi):
    total_width = sum(zone["width"] for zone in BMI_ZONES)
    current_pos = 0

    for zone in BMI_ZONES:
        if zone["min"] <= bmi < zone["max"]:
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

            context = {
                'form': form,
                'result': {
                    'bmi': bmi,
                    'category': category,
                    'marker_position': f"{marker_position:.1f}".replace(',', '.')  # <<< najważniejsza zmiana
                }
            }
            return render(request, 'bmi/bmi_form.html', context)
    else:
        form = BMIForm()

    return render(request, 'bmi/bmi_form.html', {'form': form})

@login_required
def bmi_history(request):
    records = BMIRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bmi/bmi_history.html', {'records': records})
