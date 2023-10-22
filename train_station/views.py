import geopy.distance
from django.db.models import F, Count
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from train_station.models import Station, Route, Crew, TrainType, Train, Journey, Order
from train_station.serializers import (
    StationSerializer, RouteSerializer, RouteListSerializer, RouteDetailSerializer, CrewSerializer, TrainTypeSerializer,
    TrainSerializer, TrainListSerializer, TrainDetailSerializer, JourneySerializer, JourneyListSerializer,
    JourneyDetailSerializer, OrderSerializer, OrderListSerializer
)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


def haversine_distance(source: Station, destination: Station):
    coords_1 = (source.latitude, source.longitude)
    coords_2 = (destination.latitude, destination.longitude)

    return round(geopy.distance.geodesic(coords_1, coords_2).km, 1)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def perform_create(self, serializer):
        source = Station.objects.get(id=self.request.data["source"])
        destination = Station.objects.get(id=self.request.data["destination"])
        distance = haversine_distance(source, destination)
        serializer.save(distance=distance)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return self.serializer_class


class JourneyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (Journey.objects
                .select_related("train", "route")
                .prefetch_related("crew")
                .annotate(
                    tickets_available=(
                        F("train__cargo_num") * F("train__places_in_cargo")
                        - Count("tickets")
                    )
                )
    )
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return self.serializer_class


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route", "tickets__journey__train"
    )
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
