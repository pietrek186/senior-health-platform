from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Reminder

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

        # >>> WAŻNE: parsowanie na obiekty date/time
        date_str = request.POST.get('date')      # np. "2025-08-11"
        time_str = request.POST.get('time')      # np. "16:30"
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()

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
    # POKAZUJEMY TYLKO AKTYWNE (żeby jednorazowe znikały po wysłaniu)
    reminders = Reminder.objects.filter(user=request.user, is_active=True).order_by('next_run', 'date', 'time')
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

        # >>> WAŻNE: parsowanie na obiekty date/time
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()

        reminder.title = title
        reminder.date = date_obj
        reminder.time = time_obj
        reminder.recurrence = recurrence
        # po edycji przeliczamy „następny termin”
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
