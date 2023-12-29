import string
from typing import Union
from threading import Lock, Thread
from datetime import datetime

import smart_home_server.constants as const
from smart_home_server.handlers.lcd.helpers import _startLcd, _stopLcd, _overwriteLcd, _getLcd, _getLcds, _deleteLcd
from smart_home_server.hardware_interfaces.udp import udpListener

lcdLock = Lock()
_lcdListenLoopCondition = False

#######
# api #
#######
def startLcd(num:int, ip:Union[str,None] = None, port:Union[int, None] = None):
    with lcdLock:
        _startLcd(num, ip, port)

def stopLcd(num:int):
    with lcdLock:
        _stopLcd(num)

def overwriteLcd(num:int, lcd:dict):
    with lcdLock:
        _overwriteLcd(num, lcd)

def getLcd(num:int)->dict:
    with lcdLock:
        return _getLcd(num)

def getLcds()->list[dict]:
    with lcdLock:
        return _getLcds()

def deleteLcd(num:int):
    with lcdLock:
        _deleteLcd(num)


###################
# listener target #
###################
def _addLcd(ip, port, lcdNumStr):
    # must return expected polling period
    try:
        lcdNum = int(lcdNumStr)
        startLcd(lcdNum, ip, port)
    except:
        return

####################
# listener controls#
####################
def stopLcdListener():
    global _lcdListenerLoopCondition
    _lcdListenerLoopCondition = False

    # stop integrated lcd
    stopLcd(0)

def joinLcdListener():
    global _lcdListenerLoopCondition
    global _lcdListenerThread

    if _lcdListenerThread is not None and _lcdListenerThread.is_alive():
        _lcdListenerLoopCondition = False
        _lcdListenerThread.join()
    else:
        _lcdListenerLoopCondition = False

def startLcdListener():
    global _lcdListenerLoopCondition
    global _lcdListenerThread
    if _lcdListenerLoopCondition:
        raise Exception("LcdListener Already Running")


    joinLcdListener()

    # start integrated lcd
    startLcd(0)

    print(f"LcdListener Load Time: {datetime.now()}")
    _lcdListenerLoopCondition = True
    _lcdListenerThread = Thread(target=lambda: udpListener(const.lcdListenerPort, _addLcd, lambda: _lcdListenLoopCondition))
    _lcdListenerThread.start()
    print("lcdListener started")

