from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import Reminder

def _normalize_date_time(date_str: str, time_str: str):
    ds = (date_str or "").strip()
    ts = (time_str or "").strip()

    if len(ds) > 10:
        ds = ds[-10:]
    if len(ts) > 5:
        ts = ts[:5]

    date_obj = datetime.strptime(ds, '%Y-%m-%d').date()
    time_obj = datetime.strptime(ts, '%H:%M').time()
    return date_obj, time_obj


@login_required
def add_reminder(request):
    if request.method == 'POST':
        title = request.POST.get('custom_title') if request.POST.get('title_select') == "Inne" else request.POST.get('title_select')

        if request.POST.get('repeat_daily'):
            recurrence = 'daily'
        elif request.POST.get('repeat_weekly'):
            recurrence = 'weekly'
        else:
            recurrence = None

        date_obj, time_obj = _normalize_date_time(
            request.POST.get('date'),
            request.POST.get('time')
        )

        reminder = Reminder(
            title=title,
            date=date_obj,
            time=time_obj,
            recurrence=recurrence,
            user=request.user,
            is_active=True,
        )
        reminder.next_run = reminder.compute_initial_next_run()
        reminder.save()

        messages.success(request, "Przypomnienie zostało pomyślnie dodane.")
        return redirect('reminder_list')

    return render(request, 'reminders/add_reminder.html')


@login_required
def reminder_list(request):
    reminders = (
        Reminder.objects
        .filter(user=request.user, is_active=True)
        .order_by('-id')
    )
    return render(request, 'reminders/reminder_list.html', {'reminders': reminders})


@login_required
def edit_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('custom_title') if request.POST.get('title_select') == "Inne" else request.POST.get('title_select')

        if request.POST.get('repeat_daily'):
            recurrence = 'daily'
        elif request.POST.get('repeat_weekly'):
            recurrence = 'weekly'
        else:
            recurrence = None

        date_obj, time_obj = _normalize_date_time(
            request.POST.get('date'),
            request.POST.get('time')
        )

        reminder.title = title
        reminder.date = date_obj
        reminder.time = time_obj
        reminder.recurrence = recurrence
        reminder.next_run = reminder.compute_initial_next_run()
        reminder.is_active = True
        reminder.save()

        messages.success(request, "Przypomnienie zostało pomyślnie zaktualizowane.")
        return redirect('reminder_list')

    return render(request, 'reminders/edit_reminder.html', {'reminder': reminder})


@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, "Przypomnienie zostało pomyślnie usunięte.")
        return redirect('reminder_list')
    return render(request, 'reminders/delete_reminder.html', {'reminder': reminder})
