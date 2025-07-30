from django.urls import path
from . import views

urlpatterns = [
     path('', views.pressure_home, name='pressure'), 
]
