from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from .api_urls import *
from .api_samples import *


ALLOWED_URLS = (
    STATION_URL, ROUTE_URL, JOURNEY_URL, WORKER_URL, TRAIN_TYPE_URL, TRAIN_URL
)


class AdminMovieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_get_auth_is_not_required(self):
        for url in ALLOWED_URLS:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_journey(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "crew": [sample_crew().id, sample_crew().id],
            "departure_time": "2023-10-27T00:24:00",
            "arrival_time": "2023-10-27T00:24:00"
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_journey_without_train_and_route(self):
        payload = {
            "departure_time": "2023-10-27T00:24:00",
            "arrival_time": "2023-10-27T00:24:00"
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
