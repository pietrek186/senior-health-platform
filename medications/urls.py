from django.urls import path
from . import views

urlpatterns = [
    path('', views.medication_list, name='medication_list'),
    path('add/', views.add_medication, name='add_medication'),
    path('edit/<int:pk>/', views.edit_medication, name='edit_medication'),
    path('delete/<int:pk>/', views.delete_medication, name='delete_medication'),
    path('export/csv/', views.export_medications_csv, name='export_medications_csv'),
    path('test-powiadomienia/', views.test_notifications, name='test_notifications'),
]
