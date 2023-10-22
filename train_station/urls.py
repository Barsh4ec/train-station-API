from django.urls import path, include
from rest_framework import routers

from train_station.views import (
    StationViewSet,
    RouteViewSet, CrewViewSet, TrainTypeViewSet, TrainViewSet, JourneyViewSet, OrderViewSet
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("workers", CrewViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"
