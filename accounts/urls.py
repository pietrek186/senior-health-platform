from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("account-settings/", views.settings_select, name="settings"),
    path("account-settings/user/", views.edit_user, name="edit_user"),
    path("account-settings/guardian/", views.edit_guardian, name="edit_guardian"),
]
