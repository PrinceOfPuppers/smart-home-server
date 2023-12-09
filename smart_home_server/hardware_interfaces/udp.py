import socket
from typing import Union

from smart_home_server.errors import currentErrors
import smart_home_server.constants as const
from smart_home_server.hardware_interfaces import BMEData

def udpPromptRead(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(const.udpTimeout)
    # data sent is arbitrary
    sock.sendto(b"1", (ip, port))

    data, addr = sock.recvfrom(256)
    return data.decode("utf-8")

# weather server specific

s = 'Conseq_Weather_Server_Read_Err'
def _addError():
    global currentErrors
    currentErrors[s] += 1

def _clearError():
    global currentErrors
    currentErrors[s] = 0

def getWeatherServerData(ip:str) -> Union[BMEData, None]:
    try:
        res = udpPromptRead(ip, const.weatherServerPort)
        t, h, p = res.split(',')
        val = BMEData(
                temp     = round(float(t),2),     # in C
                humid    = round(float(h),2),     # in RH %
                pressure = round(float(p)/100,2)) # convert to hPa
        _clearError()

    except Exception as e:
        print("Weather Server Read Error: \n", e)
        _addError()
        val = None
    return val
