from django.urls import path
from . import views

urlpatterns = [
    path('', views.glucose_home, name='glucose'),
    path('add/', views.add_glucose_measurement, name='add_glucose'),
    path('results/', views.glucose_results, name='glucose_results'),  
    path('edit/<int:pk>/', views.edit_glucose, name='edit_glucose'),
    path('delete/<int:pk>/', views.delete_glucose, name='delete_glucose'),
    path('export/', views.export_glucose_csv, name='export_glucose_csv'),
]