from django.urls import reverse

STATION_URL = reverse("train_station:station-list")
ROUTE_URL = reverse("train_station:route-list")
WORKER_URL = reverse("train_station:crew-list")
TRAIN_TYPE_URL = reverse("train_station:traintype-list")
TRAIN_URL = reverse("train_station:train-list")
JOURNEY_URL = reverse("train_station:journey-list")
ORDER_URL = reverse("train_station:order-list")
