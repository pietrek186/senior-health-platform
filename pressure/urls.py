from django.urls import path
from . import views

urlpatterns = [
     path('', views.pressure_home, name='pressure'), 
     path('results/', views.pressure_results, name='pressure_results'),
     path('edit/<int:measurement_id>/', views.edit_pressure, name='edit_pressure'),
     path('delete/<int:measurement_id>/', views.delete_pressure, name='delete_pressure'),
]
