from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('glucose/', include('glucose.urls')),
    path('pressure/', include('pressure.urls')),
    path('bmi/', include('bmi.urls')),
    path('medications/', include('medications.urls')),
    path("", include("accounts.urls")),
    path("records/", include("records.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)