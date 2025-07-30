from django.contrib import admin
from django.urls import path, include
from core.views import register


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('glucose/', include('glucose.urls')),
    path('pressure/', include('pressure.urls')),
]