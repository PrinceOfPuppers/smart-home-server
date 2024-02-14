from dataclasses import dataclass

@dataclass
class BMEData:
    temp: float
    humid: float
    pressure: float

    def toJson(self):
        return {
            "temp":     self.temp,
            "humid":    self.humid,
            "pressure": self.pressure,
        }

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
        return {
            "temp":     self.temp,
            "humid":    self.humid,
            "pressure": self.pressure,
            "iaq":      self.iaq,
            "co2Eq":    self.co2Eq,
            "voc":      self.voc,
            "pm1":      self.pm1,
            "pm2.5":    self.pm2_5,
            "pm10":     self.pm2_5,
            "co2":      self.co2,
        }

