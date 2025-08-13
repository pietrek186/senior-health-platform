from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MedicalFileForm
from .models import MedicalFile


@login_required
def record_list(request):
    """
    Lista plików użytkownika + upload.
    - Dostęp tylko dla zalogowanych.
    - Zawsze zwracamy WYŁĄCZNIE pliki zalogowanego usera.
    - Sortujemy od najnowszych.
    - Opcjonalny filtr po nazwie (q) – zarówno GET, jak i filtr JS w szablonie.
    """
    if request.method == "POST":
        form = MedicalFileForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES.get("file"):
            obj = form.save(commit=False)
            obj.user = request.user

            uploaded = request.FILES["file"]
            obj.original_name = uploaded.name
            obj.content_type = getattr(uploaded, "content_type", "") or ""
            obj.size = getattr(uploaded, "size", 0) or 0

            obj.save()
            messages.success(request, "Plik dodany do kartoteki.")
            return redirect("records:list")
    else:
        form = MedicalFileForm()

    q = (request.GET.get("q") or "").strip()
    files = MedicalFile.objects.filter(user=request.user).order_by("-uploaded_at")
    if q:
        files = files.filter(original_name__icontains=q)

    return render(
        request,
        "records/record_list.html",
        {
          "form": form,
          "files": files,
          "q": q,
        },
    )


@login_required
def record_delete(request, pk: int):
    """
    Potwierdzenie usunięcia pliku z kartoteki (tylko właściciel).
    Usuwa również fizyczny plik ze storage.
    """
    obj = get_object_or_404(MedicalFile, pk=pk, user=request.user)

    if request.method == "POST":
        # usuń plik fizyczny
        if obj.file:
            obj.file.delete(save=False)
        obj.delete()
        messages.success(request, "Plik został usunięty.")
        return redirect("records:list")

    return render(request, "records/delete_record.html", {"fileobj": obj})
