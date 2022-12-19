from dataclasses import dataclass
from typing import Union
from datetime import datetime, timedelta

import smart_home_server.constants as const
from smart_home_server.data_sources.errors import currentErrors

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

if const.isRpi():
    from pigpio_dht import DHT22
    import pigpio
    from time import sleep

    _dht = DHT22(const.dhtGpio)
    _pi = pigpio.pi()
    _pi.set_pull_up_down(const.dhtGpioPwr, pigpio.PUD_OFF)
    _pi.write(const.dhtGpioPwr, 0)


    _prevDHTRes: Union[None, DHTData] = None
    _prevDHTTime:Union[None, datetime] = None

    def getDHT() -> Union[DHTData, None]:
        global _prevDHTTime
        global _prevDHTRes
        global _pi

        firstCall = _prevDHTTime is None or _prevDHTRes is None
        now = datetime.now()
        if not firstCall:
            assert _prevDHTTime is not None
            if now < _prevDHTTime + timedelta(seconds=const.dhtMinSamplePeriod):
                return _prevDHTRes

        try:
            _pi.write(const.dhtGpioPwr, 1)
            sleep(0.1)
            result = _dht.sample(samples=const.dhtSamples)#, max_retries=const.dhtMaxRetry)
            if not result['valid']:
                raise Exception("DHT22 Packet Invalid")
            _prevDHTTime = now
            _prevDHTRes = DHTData(temp=result['temp_c'], humid=result['humidity'])
            _clearError()
            return _prevDHTRes

        except Exception as e:
            print("DHT Read Error: \n", e)
            _addError()
            if not firstCall:
                return _prevDHTRes
        finally:
            _pi.write(const.dhtGpioPwr, 0)

else:
    def getDHT() -> Union[DHTData, None]:
        return None
