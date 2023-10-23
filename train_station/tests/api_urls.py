from django.urls import reverse

STATIONS_URL = reverse("train_station:station-list")
ROUTES_URL = reverse("train_station:route-list")
WORKERS_URL = reverse("train_station:crew-list")
TRAIN_TYPES_URL = reverse("train_station:traintype-list")
TRAINS_URL = reverse("train_station:train-list")
JOURNEYS_URL = reverse("train_station:journey-list")
ORDERS_URL = reverse("train_station:order-list")
