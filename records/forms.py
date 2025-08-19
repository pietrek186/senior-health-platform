from django import forms
from .models import MedicalFile

class MedicalFileForm(forms.ModelForm):
    class Meta:
        model = MedicalFile
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "d-none", "id": "fileInput"})
        }

    def clean_file(self):
        f = self.cleaned_data["file"]
        return f
