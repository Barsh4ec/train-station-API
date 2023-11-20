import datetime

from train_station.models import Station, Route, TrainType, Train, Journey, Crew


def sample_station(**params):
    defaults = {
        "name": "sample-station",
        "longitude": 1.01,
        "latitude": 1.02
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(name="source"),
        "destination": sample_station(name="destination"),
        "distance": 200
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {
        "name": "sample-type"
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_train(**params):
    defaults = {
        "name": "sample-train",
        "cargo_num": 10,
        "places_in_cargo": 40,
        "train_type": sample_train_type()
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_journey(**params):
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": datetime.datetime.now(),
        "arrival_time": datetime.datetime.now()
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "first_name",
        "last_name": "last_name"
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)
