import socket
from typing import Union, Callable
from dataclasses import dataclass

from smart_home_server.errors import currentErrors
import smart_home_server.constants as const
from smart_home_server.hardware_interfaces import BMEData

def udpErr(err):
    if err:
        currentErrors['UDP_Err'] += 1
    else:
        currentErrors['UDP_Err'] = 0

def udpPromptRead(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(const.udpTimeout)
    try:
        # data sent is arbitrary
        sock.sendto(b"1", (ip, port))

        data, addr = sock.recvfrom(256)
        d = data.decode("utf-8")
        udpErr(False)
        return d
    except:
        udpErr(True)


# cb types: str cb(ip:str, port:int, request: str) where returned str is response
def udpListener(port:int, cb:Callable, continueCb:Callable):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1) # so we check continue cb periodically
    sock.bind(('', port))
    while continueCb():
        try:
            # get request
            data, addr = sock.recvfrom(256)
            d = data.decode("utf-8")
            ip = addr[0]
            port = addr[1]

            # send response
            res = cb(ip,port,d)
            sock.sendto(res.encode("utf-8"), (ip, port))

            udpErr(False)
        except socket.timeout:
            continue
        except:
            udpErr(True)

# write s and wait for ack
def udpWriteAck(ip:str, port: int, s:str) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(const.udpTimeout)
    try:
        # data sent is arbitrary
        sock.sendto(s.encode("utf-8"), (ip, port))
        ack, addr = sock.recvfrom(256)
        #d = ack.decode("utf-8")
        udpErr(False)
        return True
    except socket.timeout:
        udpErr(False)
        return False
    except:
        udpErr(True)

    return False


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


# remote lcd specific

# records previous written strings
@dataclass
class LCDCacheEntry:
    conseqAckMiss:int
    lastWritten:str

_lcdCache = {}

# if acks hits maxAckMiss, returns false
def writeLCD(ip:str, port:str, lines:list, maxAckMiss = 3):
    global _lcdCache

    s = "".join(lines)
    cs = ip + port #cache string

    if cs in _lcdCache:
        if _lcdCache[cs].lastWritten == s:
            #cache hit
            return True

    ack = udpWriteAck(ip, port, s)

    if ack:
        _lcdCache[cs] = LCDCacheEntry(0,s)
        return True

    #no ack

    if cs not in _lcdCache: # first send was no ack
        _lcdCache[cs] = LCDCacheEntry(1,"")
    else:
        _lcdCache[cs].conseqAckMiss +=1

    # check for max number of Ack Misses
    if _lcdCache[cs].conseqAckMiss >= maxAckMiss:
        return False

    return True

