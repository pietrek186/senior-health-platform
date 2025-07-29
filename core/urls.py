from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import render

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),  
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # Tymczasowe adresy dla przycisków — dodamy widoki później:
    path('glucose/', views.placeholder, name='glucose'),
    path('pressure/', views.placeholder, name='pressure'),
    path('bmi/', views.placeholder, name='bmi'),
    path('medicine/', views.placeholder, name='medicine'),
    path('reminders/', views.placeholder, name='reminders'),
    path('clinics/', views.placeholder, name='clinics'),
    path('forums/', views.placeholder, name='forums'),
    path('results/', views.select_results, name='select_results'),
    path('results/glucose/', views.glucose_results, name='glucose_results'),
    path('results/pressure/', views.pressure_results, name='pressure_results'),
    path('settings/', views.placeholder, name='settings'),
    path('logout/', views.custom_logout, name='logout'),  
]


