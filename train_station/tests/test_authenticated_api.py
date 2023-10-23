import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    JourneyListSerializer,
    JourneyDetailSerializer
)
from .api_urls import *
from .api_samples import *


ALLOWED_URLS = (STATION_URL, ROUTE_URL, JOURNEY_URL)
FORBIDDEN_URLS = (WORKER_URL, TRAIN_TYPE_URL, TRAIN_URL)


def journey_detail_url(journey_id):
    return reverse("train_station:journey-detail", args=[journey_id])


class AuthenticatedTrainStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        for url in FORBIDDEN_URLS:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_auth_is_not_required(self):
        for url in ALLOWED_URLS:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_auth_is_required(self):
        for url in ALLOWED_URLS:
            res = self.client.post(url)
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_journeys(self):
        sample_journey()
        journey_with_crew = sample_journey()

        crew = sample_crew()

        journey_with_crew.crew.add(crew)

        res = self.client.get(JOURNEY_URL)
        response_data = json.dumps(res.data)
        journeys = Journey.objects.all()
        serializer = json.dumps(JourneyListSerializer(journeys, many=True).data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer[1:len(serializer) - 1], response_data)

    def test_filtering_by_source_and_destination(self):
        source = sample_station(name="source-station")
        destination = sample_station(name="destination-station")
        route1 = sample_route(source=source)
        route2 = sample_route(destination=destination)
        journey1 = sample_journey(route=route1)
        journey2 = sample_journey(route=route2)

        res = self.client.get(JOURNEY_URL, {"source": f"{route1.source.name}"})
        response_data = json.dumps(res.data)

        serializer1 = json.dumps(JourneyListSerializer(journey1).data)
        serializer2 = json.dumps(JourneyListSerializer(journey2).data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1[1:len(serializer1) - 1], response_data)
        self.assertNotIn(serializer2[1:len(serializer2) - 1], response_data)

        res = self.client.get(JOURNEY_URL, {"destination": f"{route2.destination.name}"})
        response_data = json.dumps(res.data)

        serializer1 = json.dumps(JourneyListSerializer(journey1).data)
        serializer2 = json.dumps(JourneyListSerializer(journey2).data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer1[1:len(serializer1) - 1], response_data)
        self.assertIn(serializer2[1:len(serializer2) - 1], response_data)

    def test_filtering_by_train(self):
        train = sample_train(name="train-name")
        journey1 = sample_journey(train=train)
        journey2 = sample_journey(train=train)
        journey3 = sample_journey()

        res = self.client.get(JOURNEY_URL, {"train": f"{train.name}"})

        serializer1 = json.dumps(JourneyListSerializer(journey1).data)
        serializer2 = json.dumps(JourneyListSerializer(journey2).data)
        serializer3 = json.dumps(JourneyListSerializer(journey3).data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        response_data = json.dumps(res.data)

        self.assertIn(serializer1[1:len(serializer1) - 1], response_data)
        self.assertIn(serializer2[1:len(serializer2) - 1], response_data)
        self.assertNotIn(serializer3[1:len(serializer3) - 1], response_data)

    def test_retrieve_journey_detail(self):
        journey = sample_journey()

        url = journey_detail_url(journey.id)
        res = self.client.get(url)
        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
