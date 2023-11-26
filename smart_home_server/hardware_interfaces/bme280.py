from typing import Union

import smart_home_server.constants as const
from smart_home_server.errors import currentErrors
from smart_home_server.hardware_interfaces import BMEData


s = 'Conseq_BME_Read_Err'
def _addError():
    global currentErrors
    currentErrors[s] += 1

def _clearError():
    global currentErrors
    currentErrors[s] = 0

if const.isRpi() and const.useBME:
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
            _clearError()

        except Exception as e:
            print("BME Read Error: \n", e)
            _addError()
            val = None
        return val

    # first call is usually off
    getBME()

else:
    def getBME() -> Union[BMEData, None]:
        return None
