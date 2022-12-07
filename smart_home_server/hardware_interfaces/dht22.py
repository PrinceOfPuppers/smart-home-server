from dataclasses import dataclass
from typing import Union
from datetime import datetime, timedelta

import smart_home_server.constants as const

@dataclass
class DHTData:
    temp: float
    humid: float


if const.isRpi():
    from pigpio_dht import DHT22

    _dht = DHT22(const.dhtGpio)

    _prevDHTRes: Union[None, DHTData] = None
    _prevDHTTime:Union[None, datetime] = None

    def getDHT() -> Union[DHTData, None]:
        global _prevDHTTime
        global _prevDHTRes

        firstCall = _prevDHTTime is None or _prevDHTRes is None

        now = datetime.now()
        if not firstCall:
            if now < _prevDHTTime + timedelta(seconds=const.dhtMinSamplePeriod):
                return _prevDHTRes

        try:
            result = _dht.sample(samples=const.dhtSamples)#, max_retries=const.dhtMaxRetry)
            if not result['valid']:
                if not firstCall:
                    return _prevDHTRes
                return None
            _prevDHTTime = now
            _prevDHTRes = DHTData(temp=result['temp_c'], humid=result['humidity'])
            return _prevDHTRes
        except Exception as e:
            print("DHT Read Error: \n", e)
            if not firstCall:
                return _prevDHTRes
            return None
else:
    def getDHT() -> Union[DHTData, None]:
        return None
