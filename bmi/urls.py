from django.urls import path
from . import views

urlpatterns = [
    path('', views.bmi_view, name='bmi_form'),  # <-- tu zmieniamy nazwę ścieżki z 'bmi' na 'bmi_form'
    path('history/', views.bmi_history, name='bmi_history'),
    path('delete/<int:record_id>/', views.delete_bmi_record, name='delete_bmi_record'),
]
