from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/train_station/", include("train_station.urls", namespace="train_station")),
]
