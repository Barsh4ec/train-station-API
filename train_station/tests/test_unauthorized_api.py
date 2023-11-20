from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from .api_urls import *


ALLOWED_URLS = (STATION_URL, ROUTE_URL, JOURNEY_URL)
FORBIDDEN_URLS = (WORKER_URL, TRAIN_TYPE_URL, TRAIN_URL, ORDER_URL)


class UnauthenticatedTrainStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        for url in FORBIDDEN_URLS:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_auth_is_not_required(self):
        for url in ALLOWED_URLS:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_auth_is_required(self):
        for url in ALLOWED_URLS:
            res = self.client.post(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
