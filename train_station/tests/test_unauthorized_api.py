from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from .api_urls import *


ALLOWED_URLS = (STATIONS_URL, ROUTES_URL, JOURNEYS_URL)
FORBIDDEN_URLS = (WORKERS_URL, TRAIN_TYPES_URL, TRAINS_URL, ORDERS_URL)


class UnauthenticatedMovieApiTests(TestCase):
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
