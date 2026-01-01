from typing import Union

import smart_home_server.constants as const
from smart_home_server.errors import clearConseqError, incConseqError
from smart_home_server.hardware_interfaces import BMEData

if const.isRpi() and const.bme280Connected:
    from smbus2 import SMBus
    from bme280 import BME280

    bus = SMBus(1)
    bme280 = BME280(i2c_dev = bus)

    def getBME() -> Union[BMEData, None]:
        try:
            t = round(bme280.get_temperature(), 2) # in C
            h = round(bme280.get_humidity(), 2) # in RH %
            p = round(bme280.get_pressure(), 2) # in hPa
            val = BMEData(temp = t, humid = h, pressure = p)

            clearConseqError("BME280 Read Err")

        except Exception as e:
            print("BME Read Error: \n", e)
            incConseqError("BME280 Read Err")
            val = None
        return val

    # first call is usually off
    getBME()

else:
    def getBME() -> Union[BMEData, None]:
        return None
