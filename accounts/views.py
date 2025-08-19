from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

from .forms import ProfileUpdateForm, PasswordChangeOptionalForm, GuardianForm


@login_required
def settings_select(request):
    return render(request, "accounts/settings_select.html")


@login_required
def edit_user(request):
    user = request.user
    active_tab = "profile"

    if request.method == "POST":
        #Zapis danych podstawowych
        if "profile_submit" in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=user)
            pwd_form = PasswordChangeOptionalForm(user)
            active_tab = "profile"
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Dane zostały zaktualizowane.")
                return redirect(request.path)

        #Zmiana hasła
        elif "password_submit" in request.POST:
            profile_form = ProfileUpdateForm(instance=user)
            pwd_form = PasswordChangeOptionalForm(user, data=request.POST)
            active_tab = "password"
            if pwd_form.is_valid():
                pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Hasło zostało zmienione.")
                return redirect(request.path)

        else:
            profile_form = ProfileUpdateForm(instance=user)
            pwd_form = PasswordChangeOptionalForm(user)
    else:
        profile_form = ProfileUpdateForm(instance=user)
        pwd_form = PasswordChangeOptionalForm(user)

    return render(
        request,
        "accounts/edit_user.html",
        {
            "profile_form": profile_form,
            "pwd_form": pwd_form,
            "active_tab": active_tab,
        },
    )


@login_required
def edit_guardian(request):
    if request.method == "POST":
        form = GuardianForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane opiekuna zostały zaktualizowane.")
            return redirect("accounts:edit_guardian")
    else:
        form = GuardianForm(
            instance=request.user,
            initial={
                "guardian_email": request.user.guardian_email,
                "guardian_phone": request.user.guardian_phone,
            },
        )

    return render(request, "accounts/edit_guardian.html", {"form": form})