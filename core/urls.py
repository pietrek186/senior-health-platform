from django.urls import path
from . import views
from django.urls import path, include
from .views import test_email
from . import api


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),  
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('results/', views.select_results, name='select_results'),
    path('results/pressure/', views.pressure_results, name='pressure_results'),
    path('logout/', views.custom_logout, name='logout'),  
    path('test-email/', test_email),
    path('test-alerts/', views.test_alerts),
    path('reminders/', include('reminders.urls')),
    path('sos/', views.sos_alert, name='sos_alert'),
    path("forums/", views.forums, name="forums"),
    path("clinics/", views.clinics_view, name="clinics"),
    path("api/geocode", api.geocode, name="api_geocode"),
    path("api/clinics", api.clinics, name="api_clinics"),
    path("api/rev/", api.reverse_geocode, name="api_reverse"),
]
