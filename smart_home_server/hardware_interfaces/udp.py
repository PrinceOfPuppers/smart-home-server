import socket

from typing import Union
from smart_home_server.errors import currentErrors
import smart_home_server.constants as const
from smart_home_server.hardware_interfaces import BMEData, AQSData

def udpErr(err):
    if err:
        currentErrors['UDP_Err'] += 1
    else:
        currentErrors['UDP_Err'] = 0

def udpPromptRead(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ip,port))
    sock.settimeout(const.udpTimeout)
    try:
        # data sent is arbitrary
        sock.send(b"1")

        data = sock.recv(256)
        d = data.decode("utf-8")
        udpErr(False)
        return d
    except:
        udpErr(True)




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
        res = None
        i = 0
        while res is None and i < 3:
            res = udpPromptRead(ip, const.weatherServerPort)
            i+=1
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


def iaqToDescription(iaq:float) -> str:
    if iaq < 50:
        return "excellent"
    if iaq < 100:
        return "good"
    if iaq < 150:
        return "light"
    if iaq < 200:
        return "moderate"
    if iaq < 250:
        return "heavy"
    if iaq < 350:
        return "severe"
    return "extreme"

def getAirQualityServerData(ip:str) -> Union[AQSData, None]:
    try:
        res = None
        i = 0
        while res is None and i < 3:
            res = udpPromptRead(ip, const.airQualityServerPort)
            i+=1
        t, h, p, iaq, ceq, v, p1, p2_5, p10, co2  = res.split(',')
        val = AQSData(
            temp     = round(float(t),2),     # in C
            humid    = round(float(h),2),     # in RH %
            pressure = round(float(p)/100,2), # convert to hPa
            iaq      = round(float(iaq),1),   # scale [0--|Excellent|--50--|good|--100--|light|--150--|moderate|--200--|heavy|--250--|severe|--350--|extreme|--...]
            co2Eq    = round(float(ceq),0),   # in ppm
            voc      = round(float(v),1),     # in ppm
            pm1      = int(p1),               # in ug/m^3
            pm2_5    = int(p2_5),             # in ug/m^3
            pm10     = int(p10),              # in ug/m^3
            co2      = int(co2),              # in ppm
        )
        _clearError()

    except Exception as e:
        print("Weather Server Read Error: \n", e)
        _addError()
        val = None
    return val

