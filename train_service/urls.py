from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/train_station/", include("train_station.urls", namespace="train_station")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
