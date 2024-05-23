from dataclasses import dataclass
from math import isnan


def _toJson(obj):
    res = {}
    for attr, value in obj.__dict__.items():
        if isinstance(value, float) and isnan(value): # nan is not valid json token
            continue
        res[attr] = value
    return res


@dataclass
class BMEData:
    temp: float
    humid: float
    pressure: float

    def toJson(self):
        return _toJson(self)


@dataclass
class AQSData:
    temp: float
    humid: float
    pressure: float
    iaq: float
    co2Eq: float
    voc: float

    pm1: int
    pm2_5: int
    pm10: int

    co2: int

    def toJson(self):
        return _toJson(self)
