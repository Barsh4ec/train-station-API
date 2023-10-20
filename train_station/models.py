import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Station(models.Model):
    name = models.CharField(max_length=63)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.latitude},{self.longitude})"


class Route(models.Model):
    source = models.ForeignKey(to=Station, on_delete=models.CASCADE, related_name="source_routes")
    destination = models.ForeignKey(to=Station, on_delete=models.CASCADE, related_name="destination_routes")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.distance} km)"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/trains/", filename)


class Train(models.Model):
    name = models.CharField(max_length=63)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(to=TrainType, on_delete=models.CASCADE, related_name="trains")
    image = models.ImageField(null=True, upload_to=train_image_file_path)

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"{self.name} ({self.train_type})"


class Journey(models.Model):
    route = models.ForeignKey(to=Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey(to=Train, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route}, {self.train} ({self.departure_time} - {self.arrival_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(to=Journey, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"cargo: {self.cargo}, seat: {self.seat}"
