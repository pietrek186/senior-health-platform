from django.urls import path
from . import views

urlpatterns = [
    path('', views.glucose_home, name='glucose'),
    path('add/', views.add_glucose_measurement, name='add_glucose'),
]
