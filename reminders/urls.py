from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_reminder, name='add_reminder'),
    path('list/', views.reminder_list, name='reminder_list'),
    path('edit/<int:reminder_id>/', views.edit_reminder, name='edit_reminder'),
    path('delete/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
]
