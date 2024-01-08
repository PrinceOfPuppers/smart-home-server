from typing import Union
from threading import Lock, Thread
from datetime import datetime
import socket

import smart_home_server.constants as const
from smart_home_server.handlers.lcd.helpers import _startLcd, _stopLcd, _overwriteLcd, _getLcd, _getLcds, _deleteLcd, _saveLcd, LcdAlreadyExists, LcdDoesNotExist, _disconnectAllLcds, _setBacklight, _toggleBacklight
from smart_home_server.hardware_interfaces.tcp import tcpListener, tcpRecievePacket


lcdLock = Lock()
_lcdListenerLoopCondition = False
_lcdListenerThread        = None

#######
# api #
#######
def startLcd(num:int, c:Union[socket.socket, None] = None):
    with lcdLock:
        _startLcd(num, c)

def overwriteLcd(num:int, data:dict):
    data["num"] = num

    with lcdLock:
        if "backlight" in data:
            if data["backlight"] == "toggle":
                _toggleBacklight(num)
            else:
                _setBacklight(num, data["backlight"] == "on")

        # early exit
        if "name" not in data and "fmt" not in data:
            return

        lcd = _getLcd(num)

        # if name or fmt not included, leave them unchanged
        if "name" not in data:
            data["name"] = lcd["name"]
        if "fmt" not in data:
            data["fmt"] = lcd["fmt"]

        _overwriteLcd(num, data)


def saveLcd(num:int, lcd:dict):
    with lcdLock:
        _saveLcd(num, lcd)


def getLcd(num:int)->dict:
    with lcdLock:
        return _getLcd(num)

def getLcds(tagActive=False)->list[dict]:
    with lcdLock:
        return _getLcds(tagActive)

def deleteLcd(num:int):
    with lcdLock:
        _deleteLcd(num, restart = True)

def setBacklight(num: int, on: bool):
    with lcdLock:
        _setBacklight(num, on)

def toggleBacklight(num):
    with lcdLock:
        _toggleBacklight(num)

###################
# listener target #
###################
def _listenerTarget(c:socket.socket, addr):
    lcdNumStr = tcpRecievePacket(c)
    try:
        lcdNum = int(lcdNumStr)
        if(lcdNum < 1):
            raise Exception()
    except:
        print("Ignoring Invalid LCD Num: ", lcdNumStr)
        return

    print("LCD:" , lcdNum, "Connected on Address:", addr)

    startLcd(lcdNum, c)

####################
# listener controls#
####################
def stopLcdListener():
    global _lcdListenerLoopCondition
    _lcdListenerLoopCondition = False

    _disconnectAllLcds()

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

    _lcdListenerThread = Thread(target=lambda: tcpListener(const.lcdListenerPort, _listenerTarget, lambda: _lcdListenerLoopCondition))
    _lcdListenerThread.start()
    print("lcdListener started")

