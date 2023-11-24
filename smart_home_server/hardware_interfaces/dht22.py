from dataclasses import dataclass
from typing import Union
from datetime import datetime, timedelta

import smart_home_server.constants as const
from smart_home_server.errors import currentErrors

@dataclass
class DHTData:
    temp: float
    humid: float

s = 'Conseq_DHT_Read_Err'
def _addError():
    global currentErrors
    currentErrors[s] += 1

def _clearError():
    global currentErrors
    currentErrors[s] = 0

if const.isRpi() and not const.useBME:
    from pigpio_dht import DHT22
    import pigpio
    from time import sleep

    _dht = DHT22(const.dhtGpio)
    _pi = pigpio.pi()
    _pi.set_pull_up_down(const.dhtGpioPwr, pigpio.PUD_OFF)
    _pi.write(const.dhtGpioPwr, 0)

    def getDHT() -> Union[DHTData, None]:
        global _pi
        global _dht

        try:
            _pi.write(const.dhtGpioPwr, 1)
            sleep(0.1)
            result = _dht.sample(samples=const.dhtSamples, max_retries=const.dhtMaxRetry)
            if not result['valid']:
                raise Exception("DHT22 Packet Invalid")
            val = DHTData(temp=result['temp_c'], humid=result['humidity'])
            _clearError()

        except Exception as e:
            print("DHT Read Error: \n", e)
            _addError()
            # reset device (commented out due to pigpiod problems)
            #_dht = DHT22(const.dhtGpio)
            val = None
        finally:
            _pi.write(const.dhtGpioPwr, 0)

        return val

else:
    def getDHT() -> Union[DHTData, None]:
        return None
