from datetime import datetime

import geopy.distance
from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from train_station.models import Station, Route, Crew, TrainType, Train, Journey, Order
from train_station.permissions import IsAdminOrIfAuthenticatedReadOnly, IsAnonymous
from train_station.serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    CrewSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer
)


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_permissions(self):
        if self.request.user.is_anonymous:
            self.permission_classes = [
                IsAnonymous,
            ]
        else:
            self.permission_classes = [
                IsAdminOrIfAuthenticatedReadOnly,
            ]

        return super(StationViewSet, self).get_permissions()

    def get_queryset(self):
        """Retrieve the stations by their name"""
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=str,
                description="Filter by station name (ex. ?name=Lvivskyi Prymis'kyi Vokzal)",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


def haversine_distance(source: Station, destination: Station):
    coords_1 = (source.latitude, source.longitude)
    coords_2 = (destination.latitude, destination.longitude)

    return round(geopy.distance.geodesic(coords_1, coords_2).km, 1)


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_permissions(self):
        if self.request.user.is_anonymous:
            self.permission_classes = [
                IsAnonymous,
            ]
        else:
            self.permission_classes = [
                IsAdminOrIfAuthenticatedReadOnly,
            ]

        return super(RouteViewSet, self).get_permissions()

    def get_queryset(self):
        """Retrieve the Routes with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            queryset = queryset.filter(source__name__icontains=source)

        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)

        return queryset.distinct()

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=str,
                description="Filter by source station name (ex. ?source=Lvivskyi Prymis'kyi Vokzal)",
                required=False,
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description="Filter by destination station name (ex. ?destination=Kyivskyi Pivdennyi Vokzal)",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminUser,)


class TrainTypeViewSet(ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminUser,)


class TrainViewSet(ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        """Retrieve the trains with filters"""
        name = self.request.query_params.get("name")
        train_type = self.request.query_params.get("train_type")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if train_type:
            queryset = queryset.filter(train_type__name__icontains=train_type)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=str,
                description="Filter by train name (ex. ?name=Elekrychka)",
                required=False,
            ),
            OpenApiParameter(
                "train_type",
                type=str,
                description="Filter by train_type name (ex. ?train_type=Electric locomotive)",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class JourneyViewSet(ModelViewSet):
    queryset = (Journey.objects
                .select_related("train", "route")
                .prefetch_related("crew")
                .annotate(
                    tickets_available=(
                            F("train__cargo_num") * F("train__places_in_cargo")
                            - Count("tickets")
                    )
                ))
    serializer_class = JourneySerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_permissions(self):
        if self.request.user.is_anonymous:
            self.permission_classes = [
                IsAnonymous,
            ]
        else:
            self.permission_classes = [
                IsAdminOrIfAuthenticatedReadOnly,
            ]

        return super(JourneyViewSet, self).get_permissions()

    def get_queryset(self):
        """Retrieve the journeys with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        train = self.request.query_params.get("train")
        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")

        queryset = self.queryset

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(route__destination__name__icontains=destination)

        if train:
            queryset = queryset.filter(train__name__icontains=train)

        if departure_date:
            departure_time = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_time)

        if arrival_date:
            arrival_time = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_time)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=str,
                description="Filter by source station name (ex. ?source=Lvivskyi Prymis'kyi Vokzal)",
                required=False,
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description="Filter by destination station name (ex. ?destination=Kyivskyi Pivdennyi Vokzal)",
                required=False,
            ),
            OpenApiParameter(
                "train",
                type=str,
                description="Filter by train name (ex. ?train=Elekrychka)",
                required=False,
            ),
            OpenApiParameter(
                "departure_date",
                type=datetime,
                description="Filter by departure date (ex. ?date=2023-10-22)",
                required=False,
            ),
            OpenApiParameter(
                "arrival_date",
                type=datetime,
                description="Filter by arrival date (ex. ?date=2023-10-22)",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route", "tickets__journey__train"
    )
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        creation_date = self.request.query_params.get("creation_date")
        if not self.request.user.is_staff:
            self.queryset = self.queryset.filter(user=self.request.user)

        if creation_date:
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d").date()
            self.queryset = self.queryset.filter(created_at__date=creation_date)

        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "creation_date",
                type=datetime,
                description="Filter by date of creation order (ex. ?date=2023-10-22)",
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
